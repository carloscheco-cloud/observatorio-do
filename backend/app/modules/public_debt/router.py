import uuid
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.public_debt import service
from app.modules.public_debt.models import (
    DebtBalanceSnapshot,
    DebtDisbursement,
    DebtInstrument,
    DebtPayment,
    DebtServiceSchedule,
    DebtTerm,
    DebtVersion,
    FinancialTransfer,
    FiscalRiskFinding,
    MultiYearCommitment,
    PublicGuarantee,
    PublicObligation,
    PublicSubsidy,
)
from app.modules.public_debt.schemas import (
    CommitmentCreate,
    DebtMetrics,
    DisbursementCreate,
    DisbursementRead,
    FindingReview,
    GenericRead,
    GuaranteeCreate,
    InstrumentCreate,
    InstrumentRead,
    ObligationCreate,
    PaymentCreate,
    PaymentRead,
    SubsidyCreate,
    TransferCreate,
)

router = APIRouter(tags=["public debt and fiscal risks"])
Db = Annotated[Session, Depends(get_db)]
Actor = Annotated[str, Header(alias="X-Actor-Type")]


def _create(db: Session, model: type[Any], payload: Any, actor: str) -> Any:
    try:
        return service.create_canonical(db, model, payload, actor)
    except (ValueError, PermissionError) as exc:
        raise HTTPException(422, str(exc)) from exc


def _get(db: Session, model: type[Any], item_id: uuid.UUID) -> Any:
    row = db.get(model, item_id)
    if row is None:
        raise HTTPException(404, "Resource not found")
    return row


@router.get("/debt-instruments", response_model=list[InstrumentRead])
def instruments(
    db: Db,
    institution_id: uuid.UUID | None = None,
    creditor_id: uuid.UUID | None = None,
    year: int | None = None,
    currency: str | None = None,
    instrument_type: str | None = None,
    origin: str | None = None,
    status: str | None = None,
) -> list[DebtInstrument]:
    query = select(DebtInstrument)
    filters = {
        "debtor_institution_id": institution_id,
        "creditor_id": creditor_id,
        "currency": currency,
        "instrument_type": instrument_type,
        "origin": origin,
        "status": status,
    }
    for key, value in filters.items():
        if value is not None:
            query = query.where(getattr(DebtInstrument, key) == value)
    if year:
        query = query.where(DebtInstrument.effective_date.between(f"{year}-01-01", f"{year}-12-31"))
    return list(db.scalars(query))


@router.post("/debt-instruments", response_model=InstrumentRead, status_code=201)
def post_instrument(payload: InstrumentCreate, db: Db, actor: Actor = "human") -> Any:
    return _create(db, DebtInstrument, payload, actor)


@router.get("/debt-instruments/{item_id}", response_model=InstrumentRead)
def instrument(item_id: uuid.UUID, db: Db) -> DebtInstrument:
    return cast(DebtInstrument, _get(db, DebtInstrument, item_id))


@router.get("/debt-instruments/{item_id}/history", response_model=list[GenericRead])
def history(item_id: uuid.UUID, db: Db) -> list[DebtVersion]:
    return service.list_rows(db, DebtVersion, new_entity_id=item_id)


def _children(db: Session, model: type[Any], item_id: uuid.UUID) -> list[Any]:
    return service.list_rows(db, model, debt_instrument_id=item_id)


@router.get("/debt-instruments/{item_id}/terms", response_model=list[GenericRead])
def terms(item_id: uuid.UUID, db: Db) -> list[Any]:
    return _children(db, DebtTerm, item_id)


@router.get("/debt-instruments/{item_id}/disbursements", response_model=list[DisbursementRead])
def disbursements_for(item_id: uuid.UUID, db: Db) -> list[Any]:
    return _children(db, DebtDisbursement, item_id)


@router.get("/debt-instruments/{item_id}/schedule", response_model=list[GenericRead])
def schedule(item_id: uuid.UUID, db: Db) -> list[Any]:
    return _children(db, DebtServiceSchedule, item_id)


@router.get("/debt-instruments/{item_id}/payments", response_model=list[PaymentRead])
def payments_for(item_id: uuid.UUID, db: Db) -> list[Any]:
    return _children(db, DebtPayment, item_id)


@router.get("/debt-instruments/{item_id}/balances", response_model=list[GenericRead])
def balances(item_id: uuid.UUID, db: Db) -> list[Any]:
    return _children(db, DebtBalanceSnapshot, item_id)


@router.get("/debt-disbursements", response_model=list[DisbursementRead])
def disbursements(db: Db) -> list[Any]:
    return service.list_rows(db, DebtDisbursement)


@router.post("/debt-disbursements", response_model=DisbursementRead, status_code=201)
def post_disbursement(payload: DisbursementCreate, db: Db, actor: Actor = "human") -> Any:
    try:
        return service.create_disbursement(db, payload, actor)
    except (ValueError, PermissionError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/debt-payments", response_model=list[PaymentRead])
def payments(db: Db) -> list[Any]:
    return service.list_rows(db, DebtPayment)


@router.post("/debt-payments", response_model=PaymentRead, status_code=201)
def post_payment(payload: PaymentCreate, db: Db, actor: Actor = "human") -> Any:
    try:
        return service.create_payment(db, payload, actor)
    except (ValueError, PermissionError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/public-guarantees", response_model=list[GenericRead])
def guarantees(db: Db) -> list[Any]:
    return service.list_rows(db, PublicGuarantee)


@router.post("/public-guarantees", response_model=GenericRead, status_code=201)
def post_guarantee(payload: GuaranteeCreate, db: Db, actor: Actor = "human") -> Any:
    return _create(db, PublicGuarantee, payload, actor)


@router.get("/public-guarantees/{item_id}", response_model=GenericRead)
def guarantee(item_id: uuid.UUID, db: Db) -> Any:
    return _get(db, PublicGuarantee, item_id)


@router.get("/public-obligations", response_model=list[GenericRead])
def obligations(db: Db) -> list[Any]:
    return service.list_rows(db, PublicObligation)


@router.post("/public-obligations", response_model=GenericRead, status_code=201)
def post_obligation(payload: ObligationCreate, db: Db, actor: Actor = "human") -> Any:
    return _create(db, PublicObligation, payload, actor)


@router.get("/financial-transfers", response_model=list[GenericRead])
def financial_transfers(db: Db) -> list[Any]:
    return service.list_rows(db, FinancialTransfer)


@router.post("/financial-transfers", response_model=GenericRead, status_code=201)
def post_transfer(payload: TransferCreate, db: Db, actor: Actor = "human") -> Any:
    return _create(db, FinancialTransfer, payload, actor)


@router.get("/public-subsidies", response_model=list[GenericRead])
def subsidies(db: Db) -> list[Any]:
    return service.list_rows(db, PublicSubsidy)


@router.post("/public-subsidies", response_model=GenericRead, status_code=201)
def post_subsidy(payload: SubsidyCreate, db: Db, actor: Actor = "human") -> Any:
    return _create(db, PublicSubsidy, payload, actor)


@router.get("/multi-year-commitments", response_model=list[GenericRead])
def commitments(db: Db) -> list[Any]:
    return service.list_rows(db, MultiYearCommitment)


@router.post("/multi-year-commitments", response_model=GenericRead, status_code=201)
def post_commitment(payload: CommitmentCreate, db: Db, actor: Actor = "human") -> Any:
    return _create(db, MultiYearCommitment, payload, actor)


@router.get("/institutions/{institution_id}/debt", response_model=DebtMetrics)
def institution_debt(institution_id: uuid.UUID, db: Db) -> DebtMetrics:
    return service.metrics(db, institution_id)


@router.get("/institutions/{institution_id}/debt-service", response_model=DebtMetrics)
def debt_service(institution_id: uuid.UUID, db: Db) -> DebtMetrics:
    return service.metrics(db, institution_id)


@router.get("/institutions/{institution_id}/debt-history", response_model=list[GenericRead])
def debt_history(institution_id: uuid.UUID, db: Db) -> list[Any]:
    ids = select(DebtInstrument.id).where(DebtInstrument.debtor_institution_id == institution_id)
    return list(db.scalars(select(DebtVersion).where(DebtVersion.new_entity_id.in_(ids))))


@router.get("/institutions/{institution_id}/fiscal-risks", response_model=list[GenericRead])
def risks(institution_id: uuid.UUID, db: Db) -> list[Any]:
    return service.list_rows(db, FiscalRiskFinding, institution_id=institution_id)


@router.get("/institutions/{institution_id}/transfers", response_model=list[GenericRead])
def institution_transfers(institution_id: uuid.UUID, db: Db) -> list[Any]:
    return service.transfers(db, institution_id)


@router.get("/institutions/{institution_id}/obligations", response_model=list[GenericRead])
def institution_obligations(institution_id: uuid.UUID, db: Db) -> list[Any]:
    return service.list_rows(db, PublicObligation, institution_id=institution_id)


@router.get("/fiscal-risk-findings", response_model=list[GenericRead])
def findings(db: Db, finding_type: str | None = None, severity: str | None = None) -> list[Any]:
    return service.list_rows(db, FiscalRiskFinding, finding_type=finding_type, severity=severity)


@router.get("/fiscal-risk-findings/{item_id}", response_model=GenericRead)
def finding(item_id: uuid.UUID, db: Db) -> Any:
    return _get(db, FiscalRiskFinding, item_id)


@router.patch("/fiscal-risk-findings/{item_id}/review", response_model=GenericRead)
def review(item_id: uuid.UUID, payload: FindingReview, db: Db) -> Any:
    row = finding(item_id, db)
    row.status, row.reviewer_notes = payload.status, payload.reviewer_notes
    db.commit()
    db.refresh(row)
    return row
