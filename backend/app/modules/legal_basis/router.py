from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.legal_basis import service
from app.modules.legal_basis.schemas import LegalBasisCreate, LegalBasisRead

router = APIRouter(prefix="/legal-bases", tags=["legal-bases"])
DatabaseSession = Annotated[Session, Depends(get_db)]
ActorType = Annotated[str, Header()]


@router.get("", response_model=list[LegalBasisRead])
def list_all(db: DatabaseSession) -> list[LegalBasisRead]:
    return [LegalBasisRead.model_validate(item) for item in service.list_legal_bases(db)]


@router.post("", response_model=LegalBasisRead, status_code=status.HTTP_201_CREATED)
def create(
    payload: LegalBasisCreate, db: DatabaseSession, x_actor_type: ActorType = "human"
) -> LegalBasisRead:
    try:
        return LegalBasisRead.model_validate(
            service.create_legal_basis(db, payload, actor_type=x_actor_type)
        )
    except (service.InvalidLegalBasis, PermissionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
