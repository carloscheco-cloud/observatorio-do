from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.territories import service
from app.modules.territories.schemas import TerritoryCreate, TerritoryRead

router = APIRouter(prefix="/territories", tags=["territories"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[TerritoryRead])
def list_all(db: DatabaseSession) -> list[TerritoryRead]:
    return [TerritoryRead.model_validate(item) for item in service.list_territories(db)]


@router.post("", response_model=TerritoryRead, status_code=status.HTTP_201_CREATED)
def create(payload: TerritoryCreate, db: DatabaseSession) -> TerritoryRead:
    return TerritoryRead.model_validate(service.create_territory(db, payload))
