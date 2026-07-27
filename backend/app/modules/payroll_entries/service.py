import hashlib
import hmac
import os
import re
import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.evidence.models import Evidence
from app.modules.organizational_units.models import OrganizationalUnit
from app.modules.payroll_entries.models import PayrollEntry, PayrollEntryComponent
from app.modules.payroll_entries.schemas import PayrollComponentCreate, PayrollEntryCreate
from app.modules.payroll_periods.models import PayrollPeriod
from app.modules.positions.models import Position

SENSITIVE_ID = re.compile(r"(?<!\d)\d{3}-?\d{7}-?\d(?!\d)")


class InvalidPayrollEntry(ValueError):
    pass


def hash_sensitive_reference(value: str) -> str:
    salt = os.getenv("PAYROLL_REFERENCE_SALT")
    if not salt:
        raise RuntimeError("PAYROLL_REFERENCE_SALT is required")
    return hmac.new(salt.encode(), value.encode(), hashlib.sha256).hexdigest()


def list_entries(db: Session, period_id: uuid.UUID) -> list[PayrollEntry]:
    return list(
        db.scalars(
            select(PayrollEntry)
            .where(PayrollEntry.payroll_period_id == period_id)
            .order_by(PayrollEntry.row_number, PayrollEntry.normalized_name)
        )
    )


def _contains_sensitive(value: object) -> bool:
    if isinstance(value, str):
        return bool(SENSITIVE_ID.search(value))
    if isinstance(value, dict):
        return any(_contains_sensitive(k) or _contains_sensitive(v) for k, v in value.items())
    if isinstance(value, list):
        return any(_contains_sensitive(item) for item in value)
    return False


def create_entry(
    db: Session,
    period_id: uuid.UUID,
    payload: PayrollEntryCreate,
    *,
    actor_type: str = "human",
) -> PayrollEntry:
    if actor_type.lower() == "ai":
        raise PermissionError("AI actors cannot write canonical payroll entries")
    period = db.get(PayrollPeriod, period_id)
    if period is None:
        raise InvalidPayrollEntry("Payroll period does not exist")
    if period.institution_id != payload.institution_id:
        raise InvalidPayrollEntry("Entry institution must match payroll period")
    if _contains_sensitive(payload.raw_payload):
        raise InvalidPayrollEntry("Apparent national identifier is prohibited in raw payload")
    if payload.position_id:
        position = db.get(Position, payload.position_id)
        if position is None or position.institution_id != payload.institution_id:
            raise InvalidPayrollEntry("Position belongs to another institution")
    if payload.organizational_unit_id:
        unit = db.get(OrganizationalUnit, payload.organizational_unit_id)
        if unit is None or unit.institution_id != payload.institution_id:
            raise InvalidPayrollEntry("Organizational unit belongs to another institution")
    evidence = db.get(Evidence, payload.evidence_id) if payload.evidence_id else None
    if evidence and evidence.source_id != payload.source_id:
        raise InvalidPayrollEntry("Source must match evidence source")
    difference = abs(payload.gross_income - payload.total_deductions - payload.net_income)
    item = PayrollEntry(
        payroll_period_id=period_id,
        **payload.model_dump(),
        reconciliation_flag=difference > Decimal("0.01"),
        actor_type=actor_type,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def add_component(
    db: Session, entry_id: uuid.UUID, payload: PayrollComponentCreate, *, actor_type: str = "human"
) -> PayrollEntryComponent:
    if actor_type.lower() == "ai":
        raise PermissionError("AI actors cannot write canonical payroll components")
    if db.get(PayrollEntry, entry_id) is None:
        raise InvalidPayrollEntry("Payroll entry does not exist")
    evidence = db.get(Evidence, payload.evidence_id)
    if evidence is None or evidence.source_id != payload.source_id:
        raise InvalidPayrollEntry("Component source must match evidence source")
    item = PayrollEntryComponent(payroll_entry_id=entry_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
