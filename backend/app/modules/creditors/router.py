import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.creditors import service
from app.modules.creditors.models import Creditor
from app.modules.creditors.schemas import CreditorCreate, CreditorExposure, CreditorRead

router = APIRouter(tags=["creditors"])
Db = Annotated[Session, Depends(get_db)]
Actor = Annotated[str, Header(alias="X-Actor-Type")]


@router.get("/creditors", response_model=list[CreditorRead])
def list_creditors(
    db: Db, creditor_type: str | None = None, status: str | None = None
) -> list[Creditor]:
    query = select(Creditor)
    if creditor_type:
        query = query.where(Creditor.creditor_type == creditor_type)
    if status:
        query = query.where(Creditor.status == status)
    return list(db.scalars(query))


@router.post("/creditors", response_model=CreditorRead, status_code=201)
def create(payload: CreditorCreate, db: Db, actor: Actor = "human") -> Creditor:
    try:
        return service.create_creditor(db, payload, actor)
    except PermissionError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/creditors/{item_id}", response_model=CreditorRead)
def get(item_id: uuid.UUID, db: Db) -> Creditor:
    item = db.get(Creditor, item_id)
    if item is None:
        raise HTTPException(404, "Creditor not found")
    return item


@router.get("/creditors/{item_id}/exposure", response_model=CreditorExposure)
def get_exposure(item_id: uuid.UUID, db: Db) -> CreditorExposure:
    item = get(item_id, db)
    principal, guarantees = service.exposure(db, item_id)
    return CreditorExposure(
        creditor_id=item_id,
        principal_outstanding=str(principal),
        guarantee_exposure=str(guarantees),
        potential_duplicates=service.potential_duplicates(db, item),
    )
