import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.payroll_findings import service as findings_service
from app.modules.payroll_findings.schemas import PayrollFindingRead
from app.modules.payroll_periods import service
from app.modules.payroll_periods.models import PayrollPeriod
from app.modules.payroll_periods.schemas import (
    PayrollPeriodCreate,
    PayrollPeriodRead,
    PayrollSummary,
)

router = APIRouter(tags=["payroll periods"])
Db = Annotated[Session, Depends(get_db)]


@router.get("/payroll-periods", response_model=list[PayrollPeriodRead])
def periods(db: Db, institution_id: uuid.UUID | None = None) -> list[PayrollPeriodRead]:
    return [
        PayrollPeriodRead.model_validate(row)
        for row in service.list_periods(db, institution_id=institution_id)
    ]


@router.post(
    "/payroll-periods", response_model=PayrollPeriodRead, status_code=status.HTTP_201_CREATED
)
def create(
    payload: PayrollPeriodCreate,
    db: Db,
    x_actor_type: Annotated[str, Header()] = "human",
) -> PayrollPeriodRead:
    try:
        return PayrollPeriodRead.model_validate(
            service.create_period(db, payload, actor_type=x_actor_type)
        )
    except (ValueError, PermissionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/payroll-periods/{period_id}", response_model=PayrollPeriodRead)
def get(period_id: uuid.UUID, db: Db) -> PayrollPeriodRead:
    row = db.get(PayrollPeriod, period_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Payroll period not found")
    return PayrollPeriodRead.model_validate(row)


@router.get("/payroll-periods/{period_id}/summary", response_model=PayrollSummary)
def period_summary(period_id: uuid.UUID, db: Db) -> PayrollSummary:
    return service.summary(db, period_id)


@router.get("/payroll-periods/{period_id}/findings", response_model=list[PayrollFindingRead])
def findings(period_id: uuid.UUID, db: Db) -> list[PayrollFindingRead]:
    return [
        PayrollFindingRead.model_validate(row)
        for row in findings_service.list_findings(db, period_id=period_id)
    ]


@router.post(
    "/payroll-periods/{period_id}/compare/{comparison_period_id}",
    response_model=list[PayrollFindingRead],
)
def compare(
    period_id: uuid.UUID, comparison_period_id: uuid.UUID, db: Db
) -> list[PayrollFindingRead]:
    try:
        rows = findings_service.compare_periods(db, period_id, comparison_period_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return [PayrollFindingRead.model_validate(row) for row in rows]


@router.get(
    "/institutions/{institution_id}/payroll-history", response_model=list[PayrollPeriodRead]
)
@router.get(
    "/institutions/{institution_id}/payroll-evolution", response_model=list[PayrollPeriodRead]
)
def institution_history(institution_id: uuid.UUID, db: Db) -> list[PayrollPeriodRead]:
    return [
        PayrollPeriodRead.model_validate(row)
        for row in service.list_periods(db, institution_id=institution_id)
    ]


@router.get("/institutions/{institution_id}/payroll-metrics", response_model=list[PayrollSummary])
def institution_metrics(institution_id: uuid.UUID, db: Db) -> list[PayrollSummary]:
    return [
        service.summary(db, row.id)
        for row in service.list_periods(db, institution_id=institution_id)
    ]
