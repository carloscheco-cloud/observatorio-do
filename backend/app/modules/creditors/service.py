import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.creditors.models import Creditor
from app.modules.creditors.schemas import CreditorCreate


def create_creditor(db: Session, payload: CreditorCreate, actor_type: str = "human") -> Creditor:
    if actor_type.lower() == "ai":
        raise PermissionError("AI actors cannot write canonical creditor data")
    item = Creditor(**payload.model_dump(), actor_type=actor_type)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def potential_duplicates(db: Session, item: Creditor) -> list[uuid.UUID]:
    return list(
        db.scalars(
            select(Creditor.id).where(
                Creditor.normalized_name == item.normalized_name, Creditor.id != item.id
            )
        )
    )


def exposure(db: Session, creditor_id: uuid.UUID) -> tuple[object, object]:
    from app.modules.public_debt.models import DebtBalanceSnapshot, DebtInstrument, PublicGuarantee

    principal = db.scalar(
        select(func.coalesce(func.sum(DebtBalanceSnapshot.principal_outstanding), 0))
        .join(DebtInstrument)
        .where(DebtInstrument.creditor_id == creditor_id)
    )
    guarantees = db.scalar(
        select(func.coalesce(func.sum(PublicGuarantee.outstanding_exposure), 0)).where(
            PublicGuarantee.beneficiary_creditor_id == creditor_id
        )
    )
    return principal, guarantees
