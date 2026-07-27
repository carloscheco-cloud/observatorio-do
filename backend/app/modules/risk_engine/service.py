import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.modules.risk_engine.engine import (
    DeduplicationService,
    EvaluationContext,
    FindingCandidate,
    RiskScoreCalculator,
)
from app.modules.risk_engine.models import (
    AuditEvent,
    FindingEvidenceLink,
    FindingReview,
    RiskEvaluationRun,
    RiskFinding,
    RiskRule,
    RiskScore,
    RiskType,
)
from app.modules.risk_engine.schemas import EvaluationRequest, ReviewCreate, RuleCreate

ENGINE_VERSION = "10.0.0"


def list_taxonomy(db: Session) -> list[RiskType]:
    return list(db.scalars(select(RiskType).where(RiskType.status == "active")))


def list_rules(
    db: Session, *, domain: str | None = None, enabled: bool | None = None
) -> list[RiskRule]:
    query = select(RiskRule)
    if domain:
        query = query.where(RiskRule.domain == domain)
    if enabled is not None:
        query = query.where(RiskRule.enabled == enabled)
    return list(db.scalars(query.order_by(RiskRule.stable_code, RiskRule.version.desc())))


def create_rule(db: Session, payload: RuleCreate, *, actor_type: str) -> RiskRule:
    if actor_type.lower() == "ai" and payload.enabled:
        raise ValueError("AI-proposed rules require human approval before activation")
    latest = db.scalar(
        select(func.max(RiskRule.version)).where(RiskRule.stable_code == payload.stable_code)
    )
    rule = RiskRule(
        **payload.model_dump(exclude={"enabled", "created_by_actor_type"}),
        version=(latest or 0) + 1,
        enabled=payload.enabled and actor_type.lower() != "ai",
        created_by_actor_type=actor_type,
        metadata_={"proposal": actor_type.lower() == "ai"},
    )
    db.add(rule)
    db.flush()
    _audit(
        db,
        actor_type,
        None,
        "risk_rule_created",
        "risk_rule",
        rule.id,
        None,
        {"version": rule.version},
    )
    return rule


def _finding_query(
    *,
    domain: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    institution_id: uuid.UUID | None = None,
    person_id: uuid.UUID | None = None,
    supplier_id: uuid.UUID | None = None,
    territory_id: uuid.UUID | None = None,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    visibility: str | None = None,
    confidence: str | None = None,
    pending_review: bool | None = None,
) -> Select[tuple[RiskFinding]]:
    query = select(RiskFinding)
    filters = (
        (RiskFinding.domain, domain),
        (RiskFinding.severity, severity),
        (RiskFinding.status, status),
        (RiskFinding.institution_id, institution_id),
        (RiskFinding.person_id, person_id),
        (RiskFinding.supplier_id, supplier_id),
        (RiskFinding.territory_id, territory_id),
        (RiskFinding.entity_type, entity_type),
        (RiskFinding.entity_id, entity_id),
        (RiskFinding.visibility, visibility),
        (RiskFinding.confidence_level, confidence),
    )
    for column, value in filters:
        if value is not None:
            query = query.where(column == value)
    if pending_review is not None:
        query = query.where(RiskFinding.requires_human_review == pending_review)
    return query


def list_findings(
    db: Session, *, offset: int = 0, limit: int = 100, **filters: Any
) -> list[RiskFinding]:
    allowed = {
        "domain",
        "severity",
        "status",
        "institution_id",
        "person_id",
        "supplier_id",
        "territory_id",
        "entity_type",
        "entity_id",
        "visibility",
        "confidence",
        "pending_review",
    }
    query = _finding_query(**{key: value for key, value in filters.items() if key in allowed})
    return list(
        db.scalars(query.order_by(RiskFinding.last_detected_at.desc()).offset(offset).limit(limit))
    )


def persist_candidate(
    db: Session, candidate: FindingCandidate, context: EvaluationContext
) -> RiskFinding:
    fingerprint = DeduplicationService.fingerprint(candidate)
    now = datetime.now(UTC)
    existing = db.scalar(
        select(RiskFinding)
        .where(RiskFinding.deduplication_fingerprint == fingerprint)
        .with_for_update()
    )
    if existing:
        existing.last_detected_at = now
        existing.occurrence_count += 1
        if existing.status in {"resolved", "expired"}:
            existing.status = "reopened"
        return existing
    finding = RiskFinding(
        finding_code=f"RF-{fingerprint[:20].upper()}",
        deduplication_fingerprint=fingerprint,
        risk_type_id=candidate.risk_type_id,
        risk_rule_id=candidate.rule_id,
        evaluation_run_id=context.run_id,
        domain=candidate.domain,
        entity_type=candidate.entity_type,
        entity_id=candidate.entity_id,
        institution_id=candidate.institution_id,
        observed_value=candidate.observed_value,
        comparison_value=candidate.comparison_value,
        threshold_value=candidate.threshold_value,
        title=candidate.title,
        public_explanation=candidate.public_explanation,
        internal_explanation=candidate.internal_explanation,
        severity=candidate.severity,
        confidence_level=candidate.confidence_level,
        status="pending_review",
        first_detected_at=now,
        last_detected_at=now,
        occurrence_count=1,
        evidence_count=len(candidate.evidence_ids),
        requires_human_review=True,
        visibility="internal",
        metadata_=candidate.metadata,
    )
    db.add(finding)
    db.flush()
    return finding


def run_evaluation(
    db: Session, request: EvaluationRequest, *, actor_type: str, actor_id: uuid.UUID | None
) -> RiskEvaluationRun:
    now = datetime.now(UTC)
    run = RiskEvaluationRun(
        run_code=f"RISK-{now:%Y%m%d%H%M%S}-{uuid.uuid4().hex[:8]}",
        trigger_type=request.trigger_type,
        status="running",
        started_at=now,
        scope=request.model_dump(mode="json"),
        engine_version=ENGINE_VERSION,
        initiated_by_actor_type=actor_type,
        initiated_by_actor_id=actor_id,
    )
    db.add(run)
    db.flush()
    query = select(RiskRule).where(RiskRule.enabled.is_(True))
    if request.domain:
        query = query.where(RiskRule.domain == request.domain)
    if request.rule_id:
        query = query.where(RiskRule.id == request.rule_id)
    rules = list(db.scalars(query))
    run.rules_requested = len(rules)
    # Domain adapters are deliberately registered outside this core. An empty adapter set is valid.
    run.rules_executed = len(rules)
    run.completed_at = datetime.now(UTC)
    run.status = "completed"
    _audit(
        db, actor_type, actor_id, "risk_evaluation", "risk_evaluation_run", run.id, None, run.scope
    )
    return run


def review_finding(db: Session, finding: RiskFinding, payload: ReviewCreate) -> RiskFinding:
    before_status, before_severity = finding.status, finding.severity
    if payload.review_action == "publish" and finding.evidence_count < 1:
        raise ValueError("Public findings require sufficient evidence")
    finding.status = payload.new_status
    finding.severity = payload.severity or finding.severity
    finding.reviewer_notes = payload.notes
    finding.reviewed_by_actor_id = payload.reviewer_actor_id
    finding.reviewed_at = datetime.now(UTC)
    if payload.public_explanation:
        finding.public_explanation = payload.public_explanation
    if payload.review_action == "publish":
        finding.visibility = "public"
    review = FindingReview(
        finding_id=finding.id,
        reviewer_actor_id=payload.reviewer_actor_id,
        review_action=payload.review_action,
        previous_status=before_status,
        new_status=finding.status,
        review_date=finding.reviewed_at,
        notes=payload.notes,
        evidence_added_count=0,
        severity_before=before_severity,
        severity_after=finding.severity,
        public_explanation_before=None,
        public_explanation_after=payload.public_explanation,
    )
    db.add(review)
    _audit(
        db,
        "human",
        payload.reviewer_actor_id,
        "finding_reviewed",
        "risk_finding",
        finding.id,
        {"status": before_status},
        {"status": finding.status},
    )
    return finding


def add_evidence(
    db: Session,
    finding: RiskFinding,
    *,
    evidence_id: uuid.UUID,
    source_id: uuid.UUID,
    relationship_type: str,
    relevance_score: Decimal | None,
    excerpt: str | None,
) -> FindingEvidenceLink:
    link = FindingEvidenceLink(
        finding_id=finding.id,
        evidence_id=evidence_id,
        source_id=source_id,
        relationship_type=relationship_type,
        relevance_score=relevance_score,
        excerpt=excerpt,
    )
    db.add(link)
    finding.evidence_count += 1
    return link


def calculate_score(
    db: Session,
    *,
    entity_type: str,
    entity_id: uuid.UUID,
    run_id: uuid.UUID,
    period_start: date,
    period_end: date,
) -> RiskScore:
    findings = list(
        db.scalars(
            select(RiskFinding).where(
                RiskFinding.entity_type == entity_type,
                RiskFinding.entity_id == entity_id,
                RiskFinding.status.not_in({"dismissed", "suppressed", "duplicate"}),
            )
        )
    )
    severities = [item.severity for item in findings]
    data_quality = severities.count("critical_data_quality")
    total, band = RiskScoreCalculator().calculate(severities, data_quality)
    score = RiskScore(
        entity_type=entity_type,
        entity_id=entity_id,
        calculation_date=date.today(),
        period_start=period_start,
        period_end=period_end,
        total_score=total,
        score_band=band,
        component_scores={
            "severity_counts": {value: severities.count(value) for value in set(severities)}
        },
        finding_count=len(findings),
        high_priority_count=severities.count("high_priority"),
        data_quality_penalty=Decimal(data_quality),
        model_or_formula_version="observable-v1",
        evaluation_run_id=run_id,
        status="current",
        metadata_={"disclaimer": "This score does not represent culpability."},
    )
    db.add(score)
    return score


def _audit(
    db: Session,
    actor_type: str,
    actor_id: uuid.UUID | None,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID,
    previous: dict[str, object] | None,
    new: dict[str, object] | None,
) -> None:
    db.add(
        AuditEvent(
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            previous_state=previous,
            new_state=new,
        )
    )
