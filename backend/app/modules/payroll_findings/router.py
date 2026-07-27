import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.payroll_findings import service
from app.modules.payroll_findings.models import PayrollFinding
from app.modules.payroll_findings.schemas import FindingReview, PayrollFindingRead

router = APIRouter(tags=["payroll findings"])
Db = Annotated[Session, Depends(get_db)]


@router.get("/payroll-findings", response_model=list[PayrollFindingRead])
def all_findings(db: Db) -> list[PayrollFindingRead]:
    return [PayrollFindingRead.model_validate(row) for row in service.list_findings(db)]


@router.get("/payroll-findings/{finding_id}", response_model=PayrollFindingRead)
def get_finding(finding_id: uuid.UUID, db: Db) -> PayrollFindingRead:
    row = db.get(PayrollFinding, finding_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    return PayrollFindingRead.model_validate(row)


@router.patch("/payroll-findings/{finding_id}/review", response_model=PayrollFindingRead)
def review(finding_id: uuid.UUID, payload: FindingReview, db: Db) -> PayrollFindingRead:
    row = db.get(PayrollFinding, finding_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    row.status = payload.status
    row.reviewer_notes = payload.reviewer_notes
    db.commit()
    db.refresh(row)
    return PayrollFindingRead.model_validate(row)
