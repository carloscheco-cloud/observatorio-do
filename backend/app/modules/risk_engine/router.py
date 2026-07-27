import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.risk_engine import service
from app.modules.risk_engine.models import (
    FindingEvidenceLink,
    FindingReview,
    RiskEvaluationRun,
    RiskFinding,
    RiskRule,
    RiskScore,
)
from app.modules.risk_engine.schemas import (
    EvaluationRead,
    EvaluationRequest,
    EvidenceLinkCreate,
    FindingInternalRead,
    FindingRead,
    ReviewCreate,
    RiskRuleRead,
    RiskTypeRead,
    RuleCreate,
    RulePatch,
    ScoreRead,
    ScoreRequest,
    SuppressionCreate,
)

router = APIRouter(tags=["risk engine"])
Db = Annotated[Session, Depends(get_db)]
ActorType = Annotated[str, Header(alias="X-Actor-Type")]
ActorId = Annotated[uuid.UUID | None, Header(alias="X-Actor-Id")]


def _internal(actor_type: str) -> None:
    if actor_type.lower() not in {"human", "service", "admin"}:
        raise HTTPException(
            status_code=403, detail="Internal endpoint requires an authorized actor"
        )


@router.get("/risk-taxonomy", response_model=list[RiskTypeRead])
def taxonomy(db: Db) -> list[RiskTypeRead]:
    return [RiskTypeRead.model_validate(row) for row in service.list_taxonomy(db)]


@router.get("/risk-rules", response_model=list[RiskRuleRead])
def rules(db: Db, domain: str | None = None, enabled: bool | None = None) -> list[RiskRuleRead]:
    return [
        RiskRuleRead.model_validate(row)
        for row in service.list_rules(db, domain=domain, enabled=enabled)
    ]


@router.get("/risk-findings", response_model=list[FindingRead])
def findings(
    db: Db,
    domain: str | None = None,
    severity: str | None = None,
    finding_status: str | None = Query(default=None, alias="status"),
    institution_id: uuid.UUID | None = None,
    territory_id: uuid.UUID | None = None,
    person_id: uuid.UUID | None = None,
    supplier_id: uuid.UUID | None = None,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    visibility: str = "public",
    confidence: str | None = None,
    pending_review: bool | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[FindingRead]:
    rows = service.list_findings(
        db,
        domain=domain,
        severity=severity,
        status=finding_status,
        institution_id=institution_id,
        territory_id=territory_id,
        person_id=person_id,
        supplier_id=supplier_id,
        entity_type=entity_type,
        entity_id=entity_id,
        visibility=visibility,
        confidence=confidence,
        pending_review=pending_review,
        offset=offset,
        limit=limit,
    )
    return [FindingRead.model_validate(row) for row in rows]


@router.get("/risk-findings/{finding_id}", response_model=FindingRead)
def finding(finding_id: uuid.UUID, db: Db) -> FindingRead:
    row = db.get(RiskFinding, finding_id)
    if row is None or row.visibility != "public":
        raise HTTPException(status_code=404, detail="Finding not found")
    return FindingRead.model_validate(row)


@router.get("/risk-findings/{finding_id}/evidence", response_model=None)
def evidence(finding_id: uuid.UUID, db: Db) -> list[dict[str, object]]:
    rows = db.scalars(
        select(FindingEvidenceLink).where(FindingEvidenceLink.finding_id == finding_id)
    )
    return [
        {
            "evidence_id": row.evidence_id,
            "source_id": row.source_id,
            "relationship_type": row.relationship_type,
            "relevance_score": row.relevance_score,
            "observed_at": row.observed_at,
        }
        for row in rows
    ]


@router.get("/risk-findings/{finding_id}/history", response_model=None)
def history(finding_id: uuid.UUID, db: Db) -> list[dict[str, object]]:
    rows = db.scalars(select(FindingReview).where(FindingReview.finding_id == finding_id))
    return [
        {
            "review_action": row.review_action,
            "previous_status": row.previous_status,
            "new_status": row.new_status,
            "review_date": row.review_date,
            "severity_before": row.severity_before,
            "severity_after": row.severity_after,
        }
        for row in rows
    ]


def _entity_findings(db: Session, entity_type: str, entity_id: uuid.UUID) -> list[FindingRead]:
    return [
        FindingRead.model_validate(row)
        for row in service.list_findings(
            db, entity_type=entity_type, entity_id=entity_id, visibility="public"
        )
    ]


@router.get("/institutions/{entity_id}/risk-findings", response_model=list[FindingRead])
def institution_findings(entity_id: uuid.UUID, db: Db) -> list[FindingRead]:
    return [
        FindingRead.model_validate(row)
        for row in service.list_findings(db, institution_id=entity_id, visibility="public")
    ]


@router.get("/suppliers/{entity_id}/risk-findings", response_model=list[FindingRead])
def supplier_findings(entity_id: uuid.UUID, db: Db) -> list[FindingRead]:
    return [
        FindingRead.model_validate(row)
        for row in service.list_findings(db, supplier_id=entity_id, visibility="public")
    ]


@router.get("/persons/{entity_id}/risk-findings", response_model=list[FindingRead])
def person_findings(entity_id: uuid.UUID, db: Db) -> list[FindingRead]:
    return [
        FindingRead.model_validate(row)
        for row in service.list_findings(db, person_id=entity_id, visibility="public")
    ]


@router.get("/procurement-contracts/{entity_id}/risk-findings", response_model=list[FindingRead])
def contract_findings(entity_id: uuid.UUID, db: Db) -> list[FindingRead]:
    return _entity_findings(db, "procurement_contract", entity_id)


@router.get("/public-assets/{entity_id}/risk-findings", response_model=list[FindingRead])
def asset_findings(entity_id: uuid.UUID, db: Db) -> list[FindingRead]:
    return _entity_findings(db, "public_asset", entity_id)


@router.get("/debt-instruments/{entity_id}/risk-findings", response_model=list[FindingRead])
def debt_findings(entity_id: uuid.UUID, db: Db) -> list[FindingRead]:
    return _entity_findings(db, "debt_instrument", entity_id)


@router.get("/institutions/{entity_id}/risk-score", response_model=ScoreRead)
def institution_score(entity_id: uuid.UUID, db: Db) -> ScoreRead:
    row = db.scalar(
        select(RiskScore)
        .where(RiskScore.entity_type == "institution", RiskScore.entity_id == entity_id)
        .order_by(RiskScore.calculation_date.desc())
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Risk score not found")
    return ScoreRead.model_validate(row)


@router.get("/institutions/{entity_id}/risk-summary", response_model=None)
def institution_summary(entity_id: uuid.UUID, db: Db) -> dict[str, object]:
    rows = service.list_findings(db, institution_id=entity_id, visibility="public", limit=200)
    return {
        "institution_id": entity_id,
        "finding_count": len(rows),
        "by_severity": {
            severity: sum(row.severity == severity for row in rows)
            for severity in {row.severity for row in rows}
        },
        "disclaimer": "Las señales no equivalen a acusaciones.",
    }


@router.get("/territories/{entity_id}/risk-summary", response_model=None)
def territory_summary(entity_id: uuid.UUID, db: Db) -> dict[str, object]:
    rows = service.list_findings(db, territory_id=entity_id, visibility="public", limit=200)
    return {
        "territory_id": entity_id,
        "finding_count": len(rows),
        "disclaimer": "Las señales no equivalen a acusaciones.",
    }


@router.post("/internal/risk-evaluations", response_model=EvaluationRead)
def evaluate(
    payload: EvaluationRequest,
    db: Db,
    x_actor_type: ActorType = "service",
    x_actor_id: ActorId = None,
) -> EvaluationRead:
    _internal(x_actor_type)
    row = service.run_evaluation(db, payload, actor_type=x_actor_type, actor_id=x_actor_id)
    db.commit()
    db.refresh(row)
    return EvaluationRead.model_validate(row)


@router.get("/internal/risk-evaluations/{run_id}", response_model=EvaluationRead)
def evaluation(run_id: uuid.UUID, db: Db, x_actor_type: ActorType = "service") -> EvaluationRead:
    _internal(x_actor_type)
    row = db.get(RiskEvaluationRun, run_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return EvaluationRead.model_validate(row)


@router.post(
    "/internal/risk-rules", response_model=RiskRuleRead, status_code=status.HTTP_201_CREATED
)
def create_rule(payload: RuleCreate, db: Db, x_actor_type: ActorType = "human") -> RiskRuleRead:
    _internal(x_actor_type)
    try:
        row = service.create_rule(db, payload, actor_type=x_actor_type)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    db.commit()
    db.refresh(row)
    return RiskRuleRead.model_validate(row)


@router.patch("/internal/risk-rules/{rule_id}", response_model=RiskRuleRead)
def patch_rule(
    rule_id: uuid.UUID,
    payload: RulePatch,
    db: Db,
    x_actor_type: ActorType = "human",
) -> RiskRuleRead:
    _internal(x_actor_type)
    if x_actor_type.lower() != "human":
        raise HTTPException(status_code=403, detail="Rule activation requires human approval")
    row = db.get(RiskRule, rule_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return RiskRuleRead.model_validate(row)


@router.post("/internal/risk-findings/{finding_id}/review", response_model=FindingInternalRead)
def review(
    finding_id: uuid.UUID, payload: ReviewCreate, db: Db, x_actor_type: ActorType = "human"
) -> FindingInternalRead:
    _internal(x_actor_type)
    row = db.get(RiskFinding, finding_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    try:
        service.review_finding(db, row, payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    db.commit()
    db.refresh(row)
    return FindingInternalRead.model_validate(row)


@router.post("/internal/risk-findings/{finding_id}/evidence", response_model=None)
def add_evidence(
    finding_id: uuid.UUID, payload: EvidenceLinkCreate, db: Db, x_actor_type: ActorType = "human"
) -> FindingEvidenceLink:
    _internal(x_actor_type)
    row = db.get(RiskFinding, finding_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    link = service.add_evidence(db, row, **payload.model_dump())
    db.commit()
    return link


@router.post("/internal/risk-findings/{finding_id}/publish", response_model=FindingInternalRead)
def publish(
    finding_id: uuid.UUID, payload: ReviewCreate, db: Db, x_actor_type: ActorType = "human"
) -> FindingInternalRead:
    if payload.review_action != "publish":
        raise HTTPException(status_code=422, detail="Publish action required")
    return review(finding_id, payload, db, x_actor_type)


@router.post("/internal/risk-findings/{finding_id}/suppress", response_model=FindingInternalRead)
def suppress(
    finding_id: uuid.UUID,
    payload: SuppressionCreate,
    db: Db,
    x_actor_type: ActorType = "human",
) -> FindingInternalRead:
    return review(
        finding_id,
        ReviewCreate(
            reviewer_actor_id=payload.reviewer_actor_id,
            review_action="suppress",
            new_status="suppressed",
            notes=payload.reason,
        ),
        db,
        x_actor_type,
    )


@router.post("/internal/risk-scores/recalculate", response_model=ScoreRead)
def recalculate_score(
    payload: ScoreRequest,
    db: Db,
    x_actor_type: ActorType = "service",
) -> ScoreRead:
    _internal(x_actor_type)
    row = service.calculate_score(
        db,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        run_id=payload.evaluation_run_id,
        period_start=payload.period_start,
        period_end=payload.period_end,
    )
    db.commit()
    db.refresh(row)
    return ScoreRead.model_validate(row)
