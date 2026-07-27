import uuid
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.budget import service
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
    AppropriationRead,
    BudgetCycleCreate,
    BudgetCycleRead,
    BudgetMetrics,
    ClassifierCreate,
    ClassifierRead,
    ExecutionCreate,
    ExecutionRead,
    FindingReview,
    ModificationCreate,
    ModificationRead,
    ProgramCreate,
    ProgramRead,
    RevenueCreate,
    RevenueRead,
    TransferCreate,
    TransferRead,
)

router = APIRouter(tags=["public budget"])
Db = Annotated[Session, Depends(get_db)]
Actor = Annotated[str, Header(alias="X-Actor-Type")]


def _create(call: Any, db: Session, payload: Any, actor: str) -> Any:
    try:
        return call(db, payload, actor_type=actor)
    except (ValueError, PermissionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/budget-cycles", response_model=list[BudgetCycleRead])
def cycles(db: Db) -> list[BudgetCycle]:
    return service.list_rows(db, BudgetCycle)


@router.post("/budget-cycles", response_model=BudgetCycleRead, status_code=201)
def post_cycle(payload: BudgetCycleCreate, db: Db, x_actor_type: Actor = "human") -> BudgetCycle:
    return cast(BudgetCycle, _create(service.create_cycle, db, payload, x_actor_type))


@router.get("/budget-cycles/{item_id}", response_model=BudgetCycleRead)
def cycle(item_id: uuid.UUID, db: Db) -> BudgetCycle:
    row = db.get(BudgetCycle, item_id)
    if row is None:
        raise HTTPException(404, "Budget cycle not found")
    return row


@router.get("/budget-classifiers", response_model=list[ClassifierRead])
def classifiers(db: Db) -> list[BudgetClassifier]:
    return service.list_rows(db, BudgetClassifier)


@router.post("/budget-classifiers", response_model=ClassifierRead, status_code=201)
def post_classifier(payload: ClassifierCreate, db: Db, x_actor_type: Actor = "human") -> Any:
    return _create(service.create_classifier, db, payload, x_actor_type)


@router.get("/budget-programs", response_model=list[ProgramRead])
def programs(db: Db) -> list[BudgetProgram]:
    return service.list_rows(db, BudgetProgram)


@router.post("/budget-programs", response_model=ProgramRead, status_code=201)
def post_program(payload: ProgramCreate, db: Db, x_actor_type: Actor = "human") -> Any:
    return _create(service.create_program, db, payload, x_actor_type)


@router.get("/budget-appropriations", response_model=list[AppropriationRead])
def appropriations(db: Db, institution_id: uuid.UUID | None = None) -> list[BudgetAppropriation]:
    return service.list_rows(db, BudgetAppropriation, institution_id=institution_id)


@router.post("/budget-appropriations", response_model=AppropriationRead, status_code=201)
def post_appropriation(payload: AppropriationCreate, db: Db, x_actor_type: Actor = "human") -> Any:
    return _create(service.create_appropriation, db, payload, x_actor_type)


@router.get("/budget-appropriations/{item_id}", response_model=AppropriationRead)
def appropriation(item_id: uuid.UUID, db: Db) -> BudgetAppropriation:
    row = db.get(BudgetAppropriation, item_id)
    if row is None:
        raise HTTPException(404, "Appropriation not found")
    return row


@router.get("/budget-appropriations/{item_id}/history", response_model=list[AppropriationRead])
def appropriation_history(item_id: uuid.UUID, db: Db) -> list[BudgetAppropriation]:
    row = db.get(BudgetAppropriation, item_id)
    return [] if row is None else service.list_rows(db, BudgetAppropriation, checksum=row.checksum)


@router.get("/budget-modifications", response_model=list[ModificationRead])
def modifications(db: Db) -> list[BudgetModification]:
    return service.list_rows(db, BudgetModification)


@router.post("/budget-modifications", response_model=ModificationRead, status_code=201)
def post_modification(payload: ModificationCreate, db: Db, x_actor_type: Actor = "human") -> Any:
    return _create(service.create_modification, db, payload, x_actor_type)


@router.get("/budget-execution-records", response_model=list[ExecutionRead])
def executions(db: Db, institution_id: uuid.UUID | None = None) -> list[BudgetExecutionRecord]:
    return service.list_rows(db, BudgetExecutionRecord, institution_id=institution_id)


@router.post("/budget-execution-records", response_model=ExecutionRead, status_code=201)
def post_execution(payload: ExecutionCreate, db: Db, x_actor_type: Actor = "human") -> Any:
    return _create(service.create_execution, db, payload, x_actor_type)


@router.get("/budget-execution-records/{item_id}", response_model=ExecutionRead)
def execution(item_id: uuid.UUID, db: Db) -> BudgetExecutionRecord:
    row = db.get(BudgetExecutionRecord, item_id)
    if row is None:
        raise HTTPException(404, "Execution record not found")
    return row


@router.get("/budget-revenues", response_model=list[RevenueRead])
def revenues(db: Db) -> list[BudgetRevenue]:
    return service.list_rows(db, BudgetRevenue)


@router.post("/budget-revenues", response_model=RevenueRead, status_code=201)
def post_revenue(payload: RevenueCreate, db: Db, x_actor_type: Actor = "human") -> Any:
    return _create(
        lambda session, data, actor_type: service._canonical_create(
            session, BudgetRevenue, data, actor_type
        ),
        db,
        payload,
        x_actor_type,
    )


@router.get("/interinstitutional-transfers", response_model=list[TransferRead])
def transfers(db: Db) -> list[InterinstitutionalTransfer]:
    return service.list_rows(db, InterinstitutionalTransfer)


@router.post("/interinstitutional-transfers", response_model=TransferRead, status_code=201)
def post_transfer(payload: TransferCreate, db: Db, x_actor_type: Actor = "human") -> Any:
    return _create(
        lambda session, data, actor_type: service._canonical_create(
            session, InterinstitutionalTransfer, data, actor_type
        ),
        db,
        payload,
        x_actor_type,
    )


@router.get("/institutions/{institution_id}/budget-metrics", response_model=BudgetMetrics)
@router.get("/institutions/{institution_id}/budget", response_model=BudgetMetrics)
def institution_metrics(institution_id: uuid.UUID, db: Db) -> BudgetMetrics:
    return service.metrics(db, institution_id)


@router.get("/institutions/{institution_id}/budget-history", response_model=list[AppropriationRead])
@router.get(
    "/institutions/{institution_id}/budget-evolution", response_model=list[AppropriationRead]
)
def institution_history(institution_id: uuid.UUID, db: Db) -> list[BudgetAppropriation]:
    return service.list_rows(db, BudgetAppropriation, institution_id=institution_id)


@router.get("/institutions/{institution_id}/budget-execution", response_model=list[ExecutionRead])
def institution_execution(institution_id: uuid.UUID, db: Db) -> list[BudgetExecutionRecord]:
    return service.list_rows(db, BudgetExecutionRecord, institution_id=institution_id)


@router.post("/budget-cycles/{item_id}/compare/{comparison_id}")
def compare(item_id: uuid.UUID, comparison_id: uuid.UUID, db: Db) -> list[dict[str, object]]:
    return [
        {"id": row.id, "finding_type": row.finding_type, "explanation": row.explanation}
        for row in service.compare_cycles(db, item_id, comparison_id)
    ]


@router.get("/budget-findings", response_model=None)
@router.get("/institutions/{institution_id}/budget-findings", response_model=None)
def findings(db: Db, institution_id: uuid.UUID | None = None) -> list[BudgetFinding]:
    return service.list_rows(db, BudgetFinding, institution_id=institution_id)


@router.get("/budget-findings/{item_id}", response_model=None)
def finding(item_id: uuid.UUID, db: Db) -> BudgetFinding:
    row = db.get(BudgetFinding, item_id)
    if row is None:
        raise HTTPException(404, "Finding not found")
    return row


@router.patch("/budget-findings/{item_id}/review", response_model=None)
def review(item_id: uuid.UUID, payload: FindingReview, db: Db) -> BudgetFinding:
    row = finding(item_id, db)
    row.status = payload.status
    row.reviewer_notes = payload.reviewer_notes
    db.commit()
    db.refresh(row)
    return row
