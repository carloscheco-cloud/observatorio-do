import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.payroll_entries import service
from app.modules.payroll_entries.schemas import (
    PayrollComponentCreate,
    PayrollEntryCreate,
    PayrollEntryRead,
)

router = APIRouter(tags=["payroll entries"])
Db = Annotated[Session, Depends(get_db)]


@router.get("/payroll-periods/{period_id}/entries", response_model=list[PayrollEntryRead])
def entries(period_id: uuid.UUID, db: Db) -> list[PayrollEntryRead]:
    return [PayrollEntryRead.model_validate(row) for row in service.list_entries(db, period_id)]


@router.post(
    "/payroll-periods/{period_id}/entries",
    response_model=PayrollEntryRead,
    status_code=status.HTTP_201_CREATED,
)
def create(
    period_id: uuid.UUID,
    payload: PayrollEntryCreate,
    db: Db,
    x_actor_type: Annotated[str, Header()] = "human",
) -> PayrollEntryRead:
    try:
        return PayrollEntryRead.model_validate(
            service.create_entry(db, period_id, payload, actor_type=x_actor_type)
        )
    except (ValueError, PermissionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/payroll-entries/{entry_id}/components", status_code=status.HTTP_201_CREATED)
def component(
    entry_id: uuid.UUID,
    payload: PayrollComponentCreate,
    db: Db,
    x_actor_type: Annotated[str, Header()] = "human",
) -> dict[str, str]:
    try:
        row = service.add_component(db, entry_id, payload, actor_type=x_actor_type)
    except (ValueError, PermissionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"id": str(row.id)}


@router.get("/persons/{person_id}/salary-history", response_model=list[PayrollEntryRead])
def salary_history(person_id: uuid.UUID, db: Db) -> list[PayrollEntryRead]:
    from sqlalchemy import select

    from app.modules.payroll_entries.models import PayrollEntry

    rows = db.scalars(
        select(PayrollEntry)
        .where(PayrollEntry.person_id == person_id)
        .order_by(PayrollEntry.processed_at.desc())
    )
    return [PayrollEntryRead.model_validate(row) for row in rows]
