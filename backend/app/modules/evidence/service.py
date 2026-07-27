from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.evidence.models import Evidence
from app.modules.evidence.schemas import EvidenceCreate


def list_evidence(db: Session) -> list[Evidence]:
    return list(db.scalars(select(Evidence).order_by(Evidence.observed_at.desc())))


def create_evidence(db: Session, payload: EvidenceCreate) -> Evidence:
    evidence = Evidence(**payload.model_dump())
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence
