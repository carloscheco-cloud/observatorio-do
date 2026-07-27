import uuid
from decimal import Decimal
from typing import Any, cast

from pydantic import BaseModel
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.modules.budget.models import BudgetAppropriation
from app.modules.evidence.models import Evidence
from app.modules.organizational_units.models import OrganizationalUnit
from app.modules.procurement_processes.models import (
    ContractAmendment,
    ContractPayment,
    ProcurementAward,
    ProcurementBid,
    ProcurementContract,
    ProcurementItem,
    ProcurementLot,
    ProcurementProcess,
    ProcurementVersion,
)
from app.modules.procurement_processes.schemas import ProcurementMetrics

CANONICAL_MODELS = (
    ProcurementProcess,
    ProcurementLot,
    ProcurementItem,
    ProcurementBid,
    ProcurementAward,
    ProcurementContract,
    ContractAmendment,
    ContractPayment,
)


def _trace(db: Session, payload: Any) -> None:
    evidence = db.get(Evidence, payload.evidence_id)
    if evidence is None or evidence.source_id != payload.source_id:
        raise ValueError("Evidence must exist and belong to the selected source")


def _create[T](db: Session, model: type[T], payload: BaseModel, actor_type: str) -> T:
    if actor_type.lower() == "ai":
        raise PermissionError("AI actors cannot write canonical procurement data")
    _trace(db, payload)
    values = payload.model_dump()
    if "actor_type" in cast(Any, model).__table__.columns:
        values["actor_type"] = actor_type
    row = cast(Any, model)(**values)
    db.add(row)
    db.commit()
    db.refresh(row)
    return cast(T, row)


def create_process(db: Session, payload: Any, actor_type: str = "human") -> ProcurementProcess:
    unit_id = getattr(payload, "organizational_unit_id", None)
    unit = db.get(OrganizationalUnit, unit_id) if unit_id else None
    if unit and unit.institution_id != payload.institution_id:
        raise ValueError("Organizational unit belongs to another institution")
    appropriation_id = getattr(payload, "budget_appropriation_id", None)
    appropriation = db.get(BudgetAppropriation, appropriation_id) if appropriation_id else None
    if appropriation and (
        appropriation.institution_id != payload.institution_id
        or appropriation.budget_cycle_id != payload.budget_cycle_id
    ):
        raise ValueError("Budget origin is incompatible with process")
    return _create(db, ProcurementProcess, payload, actor_type)


def create_lot(db: Session, payload: Any, actor_type: str = "human") -> ProcurementLot:
    if db.get(ProcurementProcess, payload.procurement_process_id) is None:
        raise ValueError("Procurement process does not exist")
    return _create(db, ProcurementLot, payload, actor_type)


def create_item(db: Session, payload: Any, actor_type: str = "human") -> ProcurementItem:
    lot = db.get(ProcurementLot, payload.lot_id) if payload.lot_id else None
    if lot and lot.procurement_process_id != payload.procurement_process_id:
        raise ValueError("Lot belongs to another process")
    return _create(db, ProcurementItem, payload, actor_type)


def create_bid(db: Session, payload: Any, actor_type: str = "human") -> ProcurementBid:
    lot = db.get(ProcurementLot, payload.lot_id) if payload.lot_id else None
    if lot and lot.procurement_process_id != payload.procurement_process_id:
        raise ValueError("Bid lot belongs to another process")
    return _create(db, ProcurementBid, payload, actor_type)


def create_award(db: Session, payload: Any, actor_type: str = "human") -> ProcurementAward:
    bid = db.get(ProcurementBid, payload.bid_id) if payload.bid_id else None
    if bid and (
        bid.procurement_process_id != payload.procurement_process_id
        or bid.supplier_id != payload.supplier_id
        or bid.lot_id != payload.lot_id
    ):
        raise ValueError("Award is incompatible with bid")
    lot = db.get(ProcurementLot, payload.lot_id) if payload.lot_id else None
    if lot and payload.awarded_amount > lot.estimated_amount and not lot.multiple_awards:
        raise ValueError("Award exceeds documented lot amount")
    return _create(db, ProcurementAward, payload, actor_type)


def create_contract(db: Session, payload: Any, actor_type: str = "human") -> ProcurementContract:
    process = db.get(ProcurementProcess, payload.procurement_process_id)
    award = db.get(ProcurementAward, payload.award_id)
    if (
        process is None
        or award is None
        or (
            process.institution_id != payload.institution_id
            or award.procurement_process_id != process.id
            or award.supplier_id != payload.supplier_id
        )
    ):
        raise ValueError("Contract is incompatible with process or award")
    return _create(db, ProcurementContract, payload, actor_type)


def create_amendment(db: Session, payload: Any, actor_type: str = "human") -> ContractAmendment:
    contract = db.get(ProcurementContract, payload.contract_id)
    if contract is None or payload.previous_amount != contract.current_amount:
        raise ValueError("Amendment previous amount does not match contract")
    return _create(db, ContractAmendment, payload, actor_type)


def create_payment(db: Session, payload: Any, actor_type: str = "human") -> ContractPayment:
    contract = db.get(ProcurementContract, payload.contract_id)
    if contract is None or (
        contract.institution_id != payload.institution_id
        or contract.supplier_id != payload.supplier_id
        or contract.currency != payload.currency
    ):
        raise ValueError("Payment parties or currency are incompatible with contract")
    total = Decimal(
        db.scalar(
            select(func.coalesce(func.sum(ContractPayment.net_amount), 0)).where(
                ContractPayment.contract_id == payload.contract_id
            )
        )
        or 0
    )
    if total + payload.net_amount > contract.current_amount and not payload.exception_documented:
        raise ValueError("Accumulated payments exceed contract amount")
    return _create(db, ContractPayment, payload, actor_type)


def list_rows[T](db: Session, model: type[T], **filters: object) -> list[T]:
    query = select(model)
    for key, value in filters.items():
        if value is not None:
            query = query.where(getattr(model, key) == value)
    return list(db.scalars(query))


def history(db: Session, entity_id: uuid.UUID) -> list[ProcurementVersion]:
    return list(
        db.scalars(
            select(ProcurementVersion)
            .where(
                (ProcurementVersion.previous_entity_id == entity_id)
                | (ProcurementVersion.new_entity_id == entity_id)
            )
            .order_by(ProcurementVersion.effective_date)
        )
    )


def metrics(db: Session, institution_id: uuid.UUID) -> ProcurementMetrics:
    process_count, estimated = db.execute(
        select(func.count(), func.coalesce(func.sum(ProcurementProcess.estimated_amount), 0)).where(
            ProcurementProcess.institution_id == institution_id
        )
    ).one()
    awarded = db.scalar(
        select(func.coalesce(func.sum(ProcurementAward.awarded_amount), 0))
        .join(ProcurementProcess)
        .where(ProcurementProcess.institution_id == institution_id)
    )
    contracted, current, paid = db.execute(
        select(
            func.coalesce(func.sum(ProcurementContract.original_amount), 0),
            func.coalesce(func.sum(ProcurementContract.current_amount), 0),
            func.coalesce(func.sum(ProcurementContract.paid_amount), 0),
        ).where(ProcurementContract.institution_id == institution_id)
    ).one()
    bid_counts = (
        select(
            ProcurementBid.procurement_process_id,
            func.count(distinct(ProcurementBid.supplier_id)).label("count"),
        )
        .join(ProcurementProcess)
        .where(ProcurementProcess.institution_id == institution_id)
        .group_by(ProcurementBid.procurement_process_id)
        .subquery()
    )
    average, single = db.execute(
        select(
            func.coalesce(func.avg(bid_counts.c.count), 0),
            func.count().filter(bid_counts.c.count == 1),
        )
    ).one()
    expired = db.scalar(
        select(func.count()).where(
            ProcurementContract.institution_id == institution_id,
            ProcurementContract.contract_status == "expired",
        )
    )
    current_d, paid_d = Decimal(current), Decimal(paid)
    return ProcurementMetrics(
        process_count=process_count,
        estimated_amount=Decimal(estimated),
        awarded_amount=Decimal(awarded or 0),
        contracted_amount=Decimal(contracted),
        modified_amount=current_d - Decimal(contracted),
        paid_amount=paid_d,
        estimated_award_difference=Decimal(estimated) - Decimal(awarded or 0),
        average_competition=Decimal(average),
        single_bidder_processes=single,
        expired_contracts=expired or 0,
        execution_percentage=paid_d / current_d * 100 if current_d else Decimal(0),
    )


def supplier_concentration(db: Session, institution_id: uuid.UUID) -> list[dict[str, object]]:
    rows = db.execute(
        select(
            ProcurementAward.supplier_id,
            func.count(ProcurementAward.id),
            func.sum(ProcurementAward.awarded_amount),
        )
        .join(ProcurementProcess)
        .where(ProcurementProcess.institution_id == institution_id)
        .group_by(ProcurementAward.supplier_id)
        .order_by(func.sum(ProcurementAward.awarded_amount).desc())
    )
    return [
        {"supplier_id": supplier, "award_count": count, "awarded_amount": str(amount)}
        for supplier, count, amount in rows
    ]
