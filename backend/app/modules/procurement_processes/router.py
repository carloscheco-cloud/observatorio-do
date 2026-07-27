import uuid
from datetime import date
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.procurement_processes import service
from app.modules.procurement_processes.models import (
    ContractAmendment,
    ContractDelivery,
    ContractPayment,
    ProcurementAward,
    ProcurementBid,
    ProcurementContract,
    ProcurementFinding,
    ProcurementItem,
    ProcurementLot,
    ProcurementProcess,
    ProcurementVersion,
)
from app.modules.procurement_processes.schemas import (
    AmendmentCreate,
    AmendmentRead,
    AwardCreate,
    AwardRead,
    BidCreate,
    BidRead,
    ContractCreate,
    ContractRead,
    FindingRead,
    FindingReview,
    ItemRead,
    LotRead,
    PaymentCreate,
    PaymentRead,
    ProcessCreate,
    ProcessRead,
    ProcurementMetrics,
)

router = APIRouter(tags=["public procurement"])
Db = Annotated[Session, Depends(get_db)]
Actor = Annotated[str, Header(alias="X-Actor-Type")]


def _create(call: Any, db: Session, payload: Any, actor: str) -> Any:
    try:
        return call(db, payload, actor)
    except (ValueError, PermissionError) as exc:
        raise HTTPException(422, str(exc)) from exc


def _get(db: Session, model: type[Any], item_id: uuid.UUID, label: str) -> Any:
    row = db.get(model, item_id)
    if row is None:
        raise HTTPException(404, f"{label} not found")
    return row


@router.get("/procurement-processes", response_model=list[ProcessRead])
def processes(
    db: Db,
    institution_id: uuid.UUID | None = None,
    supplier_id: uuid.UUID | None = None,
    year: int | None = None,
    procedure_type: str | None = None,
    procurement_type: str | None = None,
    status: str | None = None,
    territory_id: uuid.UUID | None = None,
    organizational_unit_id: uuid.UUID | None = None,
) -> list[ProcurementProcess]:
    query = select(ProcurementProcess)
    filters = {
        "institution_id": institution_id,
        "fiscal_year": year,
        "procedure_type": procedure_type,
        "procurement_type": procurement_type,
        "process_status": status,
        "territory_id": territory_id,
        "organizational_unit_id": organizational_unit_id,
    }
    for key, value in filters.items():
        if value is not None:
            query = query.where(getattr(ProcurementProcess, key) == value)
    if supplier_id:
        query = query.join(ProcurementBid).where(ProcurementBid.supplier_id == supplier_id)
    return list(db.scalars(query.distinct()))


@router.post("/procurement-processes", response_model=ProcessRead, status_code=201)
def post_process(payload: ProcessCreate, db: Db, actor: Actor = "human") -> Any:
    return _create(service.create_process, db, payload, actor)


@router.get("/procurement-processes/{item_id}", response_model=ProcessRead)
def process(item_id: uuid.UUID, db: Db) -> ProcurementProcess:
    return cast(ProcurementProcess, _get(db, ProcurementProcess, item_id, "Process"))


@router.get("/procurement-processes/{item_id}/history", response_model=None)
def process_history(item_id: uuid.UUID, db: Db) -> list[ProcurementVersion]:
    return service.history(db, item_id)


def _children(db: Session, model: type[Any], process_id: uuid.UUID) -> list[Any]:
    return list(db.scalars(select(model).where(model.procurement_process_id == process_id)))


@router.get("/procurement-processes/{item_id}/lots", response_model=list[LotRead])
def lots(item_id: uuid.UUID, db: Db) -> list[Any]:
    return _children(db, ProcurementLot, item_id)


@router.get("/procurement-processes/{item_id}/items", response_model=list[ItemRead])
def items(item_id: uuid.UUID, db: Db) -> list[Any]:
    return _children(db, ProcurementItem, item_id)


@router.get("/procurement-processes/{item_id}/bids", response_model=list[BidRead])
def bids_for_process(item_id: uuid.UUID, db: Db) -> list[Any]:
    return _children(db, ProcurementBid, item_id)


@router.get("/procurement-processes/{item_id}/awards", response_model=list[AwardRead])
def awards_for_process(item_id: uuid.UUID, db: Db) -> list[Any]:
    return _children(db, ProcurementAward, item_id)


@router.get("/procurement-processes/{item_id}/contracts", response_model=list[ContractRead])
def contracts_for_process(item_id: uuid.UUID, db: Db) -> list[Any]:
    return _children(db, ProcurementContract, item_id)


@router.get("/procurement-bids", response_model=list[BidRead])
def bids(db: Db) -> list[ProcurementBid]:
    return service.list_rows(db, ProcurementBid)


@router.post("/procurement-bids", response_model=BidRead, status_code=201)
def post_bid(payload: BidCreate, db: Db, actor: Actor = "human") -> Any:
    return _create(service.create_bid, db, payload, actor)


@router.get("/procurement-awards", response_model=list[AwardRead])
def awards(db: Db) -> list[ProcurementAward]:
    return service.list_rows(db, ProcurementAward)


@router.post("/procurement-awards", response_model=AwardRead, status_code=201)
def post_award(payload: AwardCreate, db: Db, actor: Actor = "human") -> Any:
    return _create(service.create_award, db, payload, actor)


@router.get("/procurement-contracts", response_model=list[ContractRead])
def contracts(db: Db) -> list[ProcurementContract]:
    return service.list_rows(db, ProcurementContract)


@router.post("/procurement-contracts", response_model=ContractRead, status_code=201)
def post_contract(payload: ContractCreate, db: Db, actor: Actor = "human") -> Any:
    return _create(service.create_contract, db, payload, actor)


@router.get("/procurement-contracts/{item_id}", response_model=ContractRead)
def contract(item_id: uuid.UUID, db: Db) -> ProcurementContract:
    return cast(ProcurementContract, _get(db, ProcurementContract, item_id, "Contract"))


@router.get("/procurement-contracts/{item_id}/history", response_model=None)
def contract_history(item_id: uuid.UUID, db: Db) -> list[ProcurementVersion]:
    return service.history(db, item_id)


@router.get("/procurement-contracts/{item_id}/amendments", response_model=list[AmendmentRead])
def contract_amendments(item_id: uuid.UUID, db: Db) -> list[ContractAmendment]:
    return service.list_rows(db, ContractAmendment, contract_id=item_id)


@router.get("/procurement-contracts/{item_id}/payments", response_model=list[PaymentRead])
def contract_payments(item_id: uuid.UUID, db: Db) -> list[ContractPayment]:
    return service.list_rows(db, ContractPayment, contract_id=item_id)


@router.get("/procurement-contracts/{item_id}/deliveries", response_model=None)
def contract_deliveries(item_id: uuid.UUID, db: Db) -> list[ContractDelivery]:
    return service.list_rows(db, ContractDelivery, contract_id=item_id)


@router.get("/contract-amendments", response_model=list[AmendmentRead])
def amendments(db: Db) -> list[ContractAmendment]:
    return service.list_rows(db, ContractAmendment)


@router.post("/contract-amendments", response_model=AmendmentRead, status_code=201)
def post_amendment(payload: AmendmentCreate, db: Db, actor: Actor = "human") -> Any:
    return _create(service.create_amendment, db, payload, actor)


@router.get("/contract-payments", response_model=list[PaymentRead])
def payments(db: Db) -> list[ContractPayment]:
    return service.list_rows(db, ContractPayment)


@router.post("/contract-payments", response_model=PaymentRead, status_code=201)
def post_payment(payload: PaymentCreate, db: Db, actor: Actor = "human") -> Any:
    return _create(service.create_payment, db, payload, actor)


@router.get("/procurement-findings", response_model=list[FindingRead])
def findings(db: Db) -> list[ProcurementFinding]:
    return service.list_rows(db, ProcurementFinding)


@router.get("/procurement-findings/{item_id}", response_model=FindingRead)
def finding(item_id: uuid.UUID, db: Db) -> ProcurementFinding:
    return cast(ProcurementFinding, _get(db, ProcurementFinding, item_id, "Finding"))


@router.patch("/procurement-findings/{item_id}/review", response_model=FindingRead)
def review(item_id: uuid.UUID, payload: FindingReview, db: Db) -> ProcurementFinding:
    row = finding(item_id, db)
    row.status = payload.status
    row.reviewer_notes = payload.reviewer_notes
    db.commit()
    db.refresh(row)
    return row


@router.get("/institutions/{institution_id}/procurement-metrics", response_model=ProcurementMetrics)
@router.get("/institutions/{institution_id}/procurement", response_model=ProcurementMetrics)
def institution_metrics(institution_id: uuid.UUID, db: Db) -> ProcurementMetrics:
    return service.metrics(db, institution_id)


@router.get("/institutions/{institution_id}/supplier-concentration")
def concentration(institution_id: uuid.UUID, db: Db) -> list[dict[str, object]]:
    return service.supplier_concentration(db, institution_id)


@router.get("/institutions/{institution_id}/active-contracts", response_model=list[ContractRead])
def active_contracts(
    institution_id: uuid.UUID, db: Db, as_of: date | None = None
) -> list[ProcurementContract]:
    target = as_of or date.today()
    return list(
        db.scalars(
            select(ProcurementContract).where(
                ProcurementContract.institution_id == institution_id,
                ProcurementContract.start_date <= target,
                ProcurementContract.end_date >= target,
                ProcurementContract.contract_status.in_(("signed", "active", "suspended")),
            )
        )
    )
