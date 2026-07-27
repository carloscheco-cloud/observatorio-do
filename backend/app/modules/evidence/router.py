from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.evidence import service
from app.modules.evidence.schemas import EvidenceCreate, EvidenceRead

router = APIRouter(prefix="/evidence", tags=["evidence"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[EvidenceRead])
def list_all(db: DatabaseSession) -> list[EvidenceRead]:
    return [EvidenceRead.model_validate(item) for item in service.list_evidence(db)]


@router.post("", response_model=EvidenceRead, status_code=status.HTTP_201_CREATED)
def create(payload: EvidenceCreate, db: DatabaseSession) -> EvidenceRead:
    return EvidenceRead.model_validate(service.create_evidence(db, payload))
