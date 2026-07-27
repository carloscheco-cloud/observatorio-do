import uuid
from decimal import Decimal
from typing import Any

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.public_debt.models import (
    DebtBalanceSnapshot,
    DebtDisbursement,
    DebtInstrument,
    DebtPayment,
    DebtServiceSchedule,
    FinancialTransfer,
    MultiYearCommitment,
    PublicGuarantee,
    PublicObligation,
)
from app.modules.public_debt.schemas import DebtMetrics


def create_canonical[T](
    db: Session, model: type[T], payload: BaseModel, actor_type: str = "human"
) -> T:
    if actor_type.lower() == "ai":
        raise PermissionError("AI actors cannot write canonical public debt data")
    values = payload.model_dump()
    if "actor_type" in model.__table__.columns:  # type: ignore[attr-defined]
        values["actor_type"] = actor_type
    row = model(**values)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def create_disbursement(
    db: Session, payload: BaseModel, actor_type: str = "human"
) -> DebtDisbursement:
    instrument = db.get(DebtInstrument, payload.debt_instrument_id)  # type: ignore[attr-defined]
    if instrument is None or instrument.debtor_institution_id != payload.debtor_institution_id:  # type: ignore[attr-defined]
        raise ValueError("disbursement institution is incompatible with instrument")
    total = Decimal(
        db.scalar(
            select(func.coalesce(func.sum(DebtDisbursement.amount), 0)).where(
                DebtDisbursement.debt_instrument_id == instrument.id
            )
        )
        or 0
    )
    limit = instrument.approved_amount or instrument.original_principal
    if total + payload.amount > limit and not payload.exception_documented:  # type: ignore[attr-defined]
        raise ValueError("accumulated disbursements exceed approved amount")
    return create_canonical(db, DebtDisbursement, payload, actor_type)


def create_payment(db: Session, payload: BaseModel, actor_type: str = "human") -> DebtPayment:
    instrument = db.get(DebtInstrument, payload.debt_instrument_id)  # type: ignore[attr-defined]
    if instrument is None or instrument.debtor_institution_id != payload.debtor_institution_id:  # type: ignore[attr-defined]
        raise ValueError("payment institution is incompatible with instrument")
    if payload.creditor_id and instrument.creditor_id != payload.creditor_id:  # type: ignore[attr-defined]
        raise ValueError("payment creditor is incompatible with instrument")
    return create_canonical(db, DebtPayment, payload, actor_type)


def list_rows[T](db: Session, model: type[T], **filters: object) -> list[T]:
    query = select(model)
    for key, value in filters.items():
        if value is not None:
            query = query.where(getattr(model, key) == value)
    return list(db.scalars(query))


def metrics(db: Session, institution_id: uuid.UUID) -> DebtMetrics:
    def amount(query: Any) -> Decimal:
        return Decimal(db.scalar(query) or 0)

    instruments = select(DebtInstrument.id).where(
        DebtInstrument.debtor_institution_id == institution_id
    )
    return DebtMetrics(
        institution_id=institution_id,
        instrument_count=int(
            db.scalar(
                select(func.count())
                .select_from(DebtInstrument)
                .where(DebtInstrument.debtor_institution_id == institution_id)
            )
            or 0
        ),
        current_principal=amount(
            select(func.sum(DebtInstrument.current_principal)).where(
                DebtInstrument.debtor_institution_id == institution_id
            )
        ),
        principal_outstanding=amount(
            select(func.sum(DebtBalanceSnapshot.principal_outstanding)).where(
                DebtBalanceSnapshot.debt_instrument_id.in_(instruments)
            )
        ),
        accrued_interest=amount(
            select(func.sum(DebtBalanceSnapshot.interest_accrued)).where(
                DebtBalanceSnapshot.debt_instrument_id.in_(instruments)
            )
        ),
        paid_service=amount(
            select(func.sum(DebtPayment.total_paid)).where(
                DebtPayment.debtor_institution_id == institution_id
            )
        ),
        projected_service=amount(
            select(func.sum(DebtServiceSchedule.total_due)).where(
                DebtServiceSchedule.debt_instrument_id.in_(instruments),
                DebtServiceSchedule.schedule_status.in_(
                    ("projected", "confirmed", "partially_paid")
                ),
            )
        ),
        arrears=amount(
            select(
                func.sum(
                    DebtBalanceSnapshot.arrears_principal + DebtBalanceSnapshot.arrears_interest
                )
            ).where(DebtBalanceSnapshot.debt_instrument_id.in_(instruments))
        ),
        active_guarantees=amount(
            select(func.sum(PublicGuarantee.outstanding_exposure)).where(
                PublicGuarantee.guarantor_institution_id == institution_id,
                PublicGuarantee.status.in_(("active", "partially_called", "called")),
            )
        ),
        pending_obligations=amount(
            select(func.sum(PublicObligation.outstanding_amount)).where(
                PublicObligation.institution_id == institution_id,
                PublicObligation.status.in_(("recognized", "pending", "partially_paid", "overdue")),
            )
        ),
    )


def transfers(db: Session, institution_id: uuid.UUID) -> list[FinancialTransfer]:
    return list(
        db.scalars(
            select(FinancialTransfer).where(
                (FinancialTransfer.origin_institution_id == institution_id)
                | (FinancialTransfer.destination_institution_id == institution_id)
            )
        )
    )


def commitments(db: Session, institution_id: uuid.UUID) -> list[MultiYearCommitment]:
    return list_rows(db, MultiYearCommitment, institution_id=institution_id)
