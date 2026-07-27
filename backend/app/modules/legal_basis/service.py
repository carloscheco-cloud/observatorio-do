from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.evidence.models import Evidence
from app.modules.legal_basis.models import LegalBasis
from app.modules.legal_basis.schemas import LegalBasisCreate


class InvalidLegalBasis(ValueError):
    pass


def list_legal_bases(db: Session) -> list[LegalBasis]:
    return list(db.scalars(select(LegalBasis).order_by(LegalBasis.reference)))


def create_legal_basis(
    db: Session, payload: LegalBasisCreate, *, actor_type: str = "human"
) -> LegalBasis:
    if actor_type.lower() == "ai":
        raise PermissionError("AI actors cannot write canonical legal basis records")
    if db.get(Evidence, payload.evidence_id) is None:
        raise InvalidLegalBasis("Evidence does not exist")
    item = LegalBasis(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
