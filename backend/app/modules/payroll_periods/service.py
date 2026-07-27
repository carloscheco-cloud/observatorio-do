import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.evidence.models import Evidence
from app.modules.institutions.models import Institution
from app.modules.payroll_periods.models import PayrollPeriod
from app.modules.payroll_periods.schemas import PayrollPeriodCreate, PayrollSummary
from app.modules.sources.models import Source


class InvalidPayrollPeriod(ValueError):
    pass


def list_periods(db: Session, *, institution_id: uuid.UUID | None = None) -> list[PayrollPeriod]:
    query = select(PayrollPeriod)
    if institution_id:
        query = query.where(PayrollPeriod.institution_id == institution_id)
    return list(db.scalars(query.order_by(PayrollPeriod.year.desc(), PayrollPeriod.month.desc())))


def create_period(
    db: Session, payload: PayrollPeriodCreate, *, actor_type: str = "human"
) -> PayrollPeriod:
    if actor_type.lower() == "ai":
        raise PermissionError("AI actors cannot write canonical payroll periods")
    if db.get(Institution, payload.institution_id) is None:
        raise InvalidPayrollPeriod("Institution does not exist")
    if payload.source_id and db.get(Source, payload.source_id) is None:
        raise InvalidPayrollPeriod("Source does not exist")
    evidence = db.get(Evidence, payload.evidence_id) if payload.evidence_id else None
    if payload.evidence_id and evidence is None:
        raise InvalidPayrollPeriod("Evidence does not exist")
    if evidence and evidence.source_id != payload.source_id:
        raise InvalidPayrollPeriod("Source must match evidence source")
    existing = db.scalar(
        select(PayrollPeriod).where(
            PayrollPeriod.institution_id == payload.institution_id,
            PayrollPeriod.year == payload.year,
            PayrollPeriod.month == payload.month,
            PayrollPeriod.version == payload.version,
        )
    )
    if existing:
        if payload.checksum and existing.checksum == payload.checksum:
            return existing
        raise InvalidPayrollPeriod("Payroll period version already exists")
    item = PayrollPeriod(**payload.model_dump(), actor_type=actor_type)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def summary(db: Session, period_id: uuid.UUID) -> PayrollSummary:
    from app.modules.payroll_entries.models import PayrollEntry

    values = db.execute(
        select(
            func.count(func.distinct(PayrollEntry.person_id)),
            func.coalesce(func.sum(PayrollEntry.gross_income), 0),
            func.coalesce(func.sum(PayrollEntry.total_deductions), 0),
            func.coalesce(func.sum(PayrollEntry.net_income), 0),
            func.coalesce(func.sum(PayrollEntry.other_compensation), 0),
            func.coalesce(func.avg(PayrollEntry.gross_income), 0),
            func.coalesce(func.min(PayrollEntry.gross_income), 0),
            func.coalesce(func.max(PayrollEntry.gross_income), 0),
        ).where(PayrollEntry.payroll_period_id == period_id)
    ).one()
    return PayrollSummary(
        period_id=period_id,
        people=values[0],
        gross_total=Decimal(values[1]),
        deductions_total=Decimal(values[2]),
        net_total=Decimal(values[3]),
        other_compensation_total=Decimal(values[4]),
        average_gross=Decimal(values[5]),
        minimum_gross=Decimal(values[6]),
        maximum_gross=Decimal(values[7]),
    )
