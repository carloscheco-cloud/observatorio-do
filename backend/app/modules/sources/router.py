from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.sources import service
from app.modules.sources.schemas import SourceCreate, SourceRead

router = APIRouter(prefix="/sources", tags=["sources"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[SourceRead])
def list_all(db: DatabaseSession) -> list[SourceRead]:
    return [SourceRead.model_validate(item) for item in service.list_sources(db)]


@router.post("", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
def create(payload: SourceCreate, db: DatabaseSession) -> SourceRead:
    return SourceRead.model_validate(service.create_source(db, payload))
