from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.institutions import service
from app.modules.institutions.schemas import InstitutionCreate, InstitutionRead

router = APIRouter(prefix="/institutions", tags=["institutions"])
DatabaseSession = Annotated[Session, Depends(get_db)]
ActorType = Annotated[str, Header()]


@router.get("", response_model=list[InstitutionRead])
def list_all(db: DatabaseSession) -> list[InstitutionRead]:
    return [InstitutionRead.model_validate(item) for item in service.list_institutions(db)]


@router.post("", response_model=InstitutionRead, status_code=status.HTTP_201_CREATED)
def create(
    payload: InstitutionCreate,
    db: DatabaseSession,
    x_actor_type: ActorType = "human",
) -> InstitutionRead:
    try:
        item = service.create_institution(db, payload, actor_type=x_actor_type)
    except (service.InvalidInstitution, PermissionError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return InstitutionRead.model_validate(item)
