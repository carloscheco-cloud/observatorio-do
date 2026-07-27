import uuid
from decimal import Decimal
from typing import Any, cast

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.budget.models import (
    BudgetAppropriation,
    BudgetClassifier,
    BudgetCycle,
    BudgetExecutionRecord,
    BudgetFinding,
    BudgetModification,
    BudgetProgram,
    BudgetRevenue,
    InterinstitutionalTransfer,
)
from app.modules.budget.schemas import (
    AppropriationCreate,
    BudgetCycleCreate,
    BudgetMetrics,
    ClassifierCreate,
    ExecutionCreate,
    ModificationCreate,
    ProgramCreate,
)
from app.modules.evidence.models import Evidence


def _canonical_create[T](db: Session, model: type[T], payload: BaseModel, actor_type: str) -> T:
    if actor_type.lower() == "ai":
        raise PermissionError("AI actors cannot write canonical budget data")
    values = payload.model_dump()
    evidence_id = values.get("evidence_id")
    source_id = values.get("source_id")
    if evidence_id:
        evidence = db.get(Evidence, evidence_id)
        if evidence is None or evidence.source_id != source_id:
            raise ValueError("Evidence must exist and belong to the selected source")
    constructor = cast(Any, model)
    item = constructor(**values, actor_type=actor_type)
    db.add(item)
    db.commit()
    db.refresh(item)
    return cast(T, item)


def create_cycle(db: Session, payload: BudgetCycleCreate, actor_type: str = "human") -> BudgetCycle:
    return _canonical_create(db, BudgetCycle, payload, actor_type)


def create_classifier(
    db: Session, payload: ClassifierCreate, actor_type: str = "human"
) -> BudgetClassifier:
    parent_id = getattr(payload, "parent_id", None)
    if parent_id and db.get(BudgetClassifier, parent_id) is None:
        raise ValueError("Classifier parent does not exist")
    return _canonical_create(db, BudgetClassifier, payload, actor_type)


def create_program(db: Session, payload: ProgramCreate, actor_type: str = "human") -> BudgetProgram:
    cycle = db.get(BudgetCycle, payload.budget_cycle_id)
    parent_id = getattr(payload, "parent_id", None)
    parent = db.get(BudgetProgram, parent_id) if parent_id else None
    if cycle is None:
        raise ValueError("Budget cycle does not exist")
    if parent and (
        parent.institution_id != payload.institution_id or parent.budget_cycle_id != cycle.id
    ):
        raise ValueError("Parent program is incompatible")
    return _canonical_create(db, BudgetProgram, payload, actor_type)


def create_appropriation(
    db: Session, payload: AppropriationCreate, actor_type: str = "human"
) -> BudgetAppropriation:
    program_id = getattr(payload, "program_id", None)
    program = db.get(BudgetProgram, program_id) if program_id else None
    if program and (
        program.institution_id != payload.institution_id
        or program.budget_cycle_id != payload.budget_cycle_id
    ):
        raise ValueError("Program is incompatible with appropriation")
    return _canonical_create(db, BudgetAppropriation, payload, actor_type)


def create_modification(
    db: Session, payload: ModificationCreate, actor_type: str = "human"
) -> BudgetModification:
    source_id = getattr(payload, "source_appropriation_id", None)
    destination_id = getattr(payload, "destination_appropriation_id", None)
    if payload.modification_type in {
        "transfer_in",
        "transfer_out",
        "reallocation",
    } and (not source_id or not destination_id or source_id == destination_id):
        raise ValueError("Transfers require distinct source and destination")
    if payload.resulting_balance < 0:
        raise ValueError("Modification cannot produce a negative balance")
    return _canonical_create(db, BudgetModification, payload, actor_type)


def create_execution(
    db: Session, payload: ExecutionCreate, actor_type: str = "human"
) -> BudgetExecutionRecord:
    appropriation = db.get(BudgetAppropriation, payload.appropriation_id)
    if appropriation is None or (
        appropriation.institution_id != payload.institution_id
        or appropriation.budget_cycle_id != payload.budget_cycle_id
    ):
        raise ValueError("Appropriation is incompatible with execution")
    values = payload.model_dump()
    values["reconciliation_flag"] = (
        values["current_budget"] != appropriation.current_amount
        or values["available_balance"] != values["current_budget"] - values["committed_amount"]
    )
    return _canonical_create(db, BudgetExecutionRecord, _Payload(**values), actor_type)


class _Payload(BaseModel):
    model_config = {"extra": "allow"}


def list_rows[T](db: Session, model: type[T], **filters: object) -> list[T]:
    query = select(model)
    for name, value in filters.items():
        if value is not None:
            query = query.where(getattr(model, name) == value)
    return list(db.scalars(query))


def metrics(db: Session, institution_id: uuid.UUID) -> BudgetMetrics:
    approved, current = db.execute(
        select(
            func.coalesce(func.sum(BudgetAppropriation.approved_amount), 0),
            func.coalesce(func.sum(BudgetAppropriation.current_amount), 0),
        ).where(BudgetAppropriation.institution_id == institution_id)
    ).one()
    committed, accrued, paid, available = db.execute(
        select(
            func.coalesce(func.sum(BudgetExecutionRecord.committed_amount), 0),
            func.coalesce(func.sum(BudgetExecutionRecord.accrued_amount), 0),
            func.coalesce(func.sum(BudgetExecutionRecord.paid_amount), 0),
            func.coalesce(func.sum(BudgetExecutionRecord.available_balance), 0),
        ).where(BudgetExecutionRecord.institution_id == institution_id)
    ).one()
    current_d = Decimal(current)
    paid_d = Decimal(paid)
    return BudgetMetrics(
        approved=Decimal(approved),
        current=current_d,
        committed=Decimal(committed),
        accrued=Decimal(accrued),
        paid=paid_d,
        available=Decimal(available),
        execution_percentage=(paid_d / current_d * 100 if current_d else Decimal(0)),
        net_modifications=current_d - Decimal(approved),
    )


def compare_cycles(
    db: Session, cycle_id: uuid.UUID, comparison_id: uuid.UUID
) -> list[BudgetFinding]:
    cycles = (db.get(BudgetCycle, cycle_id), db.get(BudgetCycle, comparison_id))
    if None in cycles:
        raise ValueError("Both cycles must exist")
    totals: list[Decimal] = []
    for identifier in (cycle_id, comparison_id):
        value = db.scalar(
            select(func.coalesce(func.sum(BudgetAppropriation.current_amount), 0)).where(
                BudgetAppropriation.budget_cycle_id == identifier
            )
        )
        totals.append(Decimal(value or 0))
    current = cycles[0]
    assert current is not None
    finding = BudgetFinding(
        finding_type="rapid_budget_growth" if totals[0] > totals[1] else "rapid_budget_reduction",
        severity="review_required",
        institution_id=db.scalar(
            select(BudgetAppropriation.institution_id).where(
                BudgetAppropriation.budget_cycle_id == cycle_id
            )
        ),
        budget_cycle_id=cycle_id,
        comparison_cycle_id=comparison_id,
        observed_value={"current": str(totals[0])},
        expected_or_previous_value={"previous": str(totals[1])},
        explanation="Observable change between controlled budget cycles; requires review.",
        metadata_={"analytical": True},
    )
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return [finding]


CANONICAL_MODELS: tuple[type[Any], ...] = (
    BudgetCycle,
    BudgetClassifier,
    BudgetProgram,
    BudgetAppropriation,
    BudgetModification,
    BudgetExecutionRecord,
    BudgetRevenue,
    InterinstitutionalTransfer,
)
