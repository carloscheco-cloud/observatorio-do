import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base

Json = JSON().with_variant(JSONB(), "postgresql")


class Timestamps:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class RiskDomain(Timestamps, Base):
    __tablename__ = "risk_domains"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stable_code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    official_name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="active")
    valid_from: Mapped[date] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class RiskCategory(Timestamps, Base):
    __tablename__ = "risk_categories"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stable_code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    official_name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="active")
    valid_from: Mapped[date] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class RiskType(Timestamps, Base):
    __tablename__ = "risk_types"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stable_code: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    official_name: Mapped[str] = mapped_column(String(250))
    description: Mapped[str] = mapped_column(Text)
    domain: Mapped[str] = mapped_column(String(60), index=True)
    category: Mapped[str] = mapped_column(String(60), index=True)
    default_severity: Mapped[str] = mapped_column(String(40))
    public_explanation_template: Mapped[str | None] = mapped_column(Text)
    internal_explanation_template: Mapped[str | None] = mapped_column(Text)
    recommended_review_action: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="active")
    valid_from: Mapped[date] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    source_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sources.id"))
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("evidence.id"))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class RiskIndicator(Timestamps, Base):
    __tablename__ = "risk_indicators"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stable_code: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    official_name: Mapped[str] = mapped_column(String(250))
    description: Mapped[str] = mapped_column(Text)
    domain: Mapped[str] = mapped_column(String(60), index=True)
    category: Mapped[str] = mapped_column(String(60), index=True)
    default_severity: Mapped[str] = mapped_column(String(40))
    risk_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("risk_types.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="active")
    valid_from: Mapped[date] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    source_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sources.id"))
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("evidence.id"))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class RiskRule(Timestamps, Base):
    __tablename__ = "risk_rules"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stable_code: Mapped[str] = mapped_column(String(150), index=True)
    name: Mapped[str] = mapped_column(String(250))
    description: Mapped[str] = mapped_column(Text)
    domain: Mapped[str] = mapped_column(String(60), index=True)
    risk_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("risk_types.id"), index=True)
    rule_type: Mapped[str] = mapped_column(String(40))
    version: Mapped[int] = mapped_column(Integer)
    severity: Mapped[str] = mapped_column(String(40))
    threshold_config: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    evaluation_window: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    required_fields: Mapped[list[object]] = mapped_column(Json, default=list)
    supported_entity_types: Mapped[list[object]] = mapped_column(Json, default=list)
    public_message_template: Mapped[str] = mapped_column(Text)
    internal_message_template: Mapped[str] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    valid_from: Mapped[date] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    requires_human_review: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_actor_type: Mapped[str] = mapped_column(String(30))
    source_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sources.id"))
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("evidence.id"))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class RiskEvaluationRun(Base):
    __tablename__ = "risk_evaluation_runs"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_code: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    trigger_type: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scope: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    rules_requested: Mapped[int] = mapped_column(Integer, default=0)
    rules_executed: Mapped[int] = mapped_column(Integer, default=0)
    records_evaluated: Mapped[int] = mapped_column(Integer, default=0)
    findings_created: Mapped[int] = mapped_column(Integer, default=0)
    findings_updated: Mapped[int] = mapped_column(Integer, default=0)
    findings_suppressed: Mapped[int] = mapped_column(Integer, default=0)
    errors_count: Mapped[int] = mapped_column(Integer, default=0)
    error_summary: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    engine_version: Mapped[str] = mapped_column(String(80))
    initiated_by_actor_type: Mapped[str] = mapped_column(String(30))
    initiated_by_actor_id: Mapped[uuid.UUID | None]
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RiskFinding(Timestamps, Base):
    __tablename__ = "risk_findings"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    finding_code: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    deduplication_fingerprint: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    risk_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("risk_types.id"), index=True)
    risk_rule_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("risk_rules.id"), index=True)
    evaluation_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("risk_evaluation_runs.id"), index=True
    )
    domain: Mapped[str] = mapped_column(String(60), index=True)
    entity_type: Mapped[str] = mapped_column(String(80), index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(index=True)
    institution_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("institutions.id"), index=True
    )
    person_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("persons.id"), index=True)
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("suppliers.id"), index=True)
    territory_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("territories.id"), index=True)
    period_start: Mapped[date | None] = mapped_column(Date, index=True)
    period_end: Mapped[date | None] = mapped_column(Date)
    observed_value: Mapped[dict[str, object]] = mapped_column(Json)
    comparison_value: Mapped[dict[str, object] | None] = mapped_column(Json)
    threshold_value: Mapped[dict[str, object] | None] = mapped_column(Json)
    title: Mapped[str] = mapped_column(String(300))
    public_explanation: Mapped[str] = mapped_column(Text)
    internal_explanation: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(40), index=True)
    confidence_level: Mapped[str] = mapped_column(String(30), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    first_detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    last_detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    occurrence_count: Mapped[int] = mapped_column(Integer, default=1)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    requires_human_review: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    reviewer_notes: Mapped[str | None] = mapped_column(Text)
    reviewed_by_actor_id: Mapped[uuid.UUID | None]
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolution_type: Mapped[str | None] = mapped_column(String(50))
    resolution_summary: Mapped[str | None] = mapped_column(Text)
    visibility: Mapped[str] = mapped_column(String(30), default="internal", index=True)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class FindingEvidenceLink(Base):
    __tablename__ = "finding_evidence_links"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    finding_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("risk_findings.id"), index=True)
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"))
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"))
    relationship_type: Mapped[str] = mapped_column(String(40))
    relevance_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    excerpt: Mapped[str | None] = mapped_column(Text)
    observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FindingEntityLink(Base):
    __tablename__ = "finding_entity_links"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    finding_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("risk_findings.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(80), index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(index=True)
    relationship_role: Mapped[str] = mapped_column(String(40))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FindingGroup(Timestamps, Base):
    __tablename__ = "finding_groups"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stable_code: Mapped[str] = mapped_column(String(160), unique=True)
    title: Mapped[str] = mapped_column(String(300))
    domain: Mapped[str] = mapped_column(String(60), index=True)
    first_detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class FindingDuplicate(Base):
    __tablename__ = "finding_duplicates"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    finding_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("risk_findings.id"), unique=True)
    canonical_finding_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("risk_findings.id"))
    group_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("finding_groups.id"))
    relationship_type: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FindingReview(Base):
    __tablename__ = "finding_reviews"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    finding_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("risk_findings.id"), index=True)
    reviewer_actor_id: Mapped[uuid.UUID] = mapped_column(index=True)
    review_action: Mapped[str] = mapped_column(String(40))
    previous_status: Mapped[str] = mapped_column(String(40))
    new_status: Mapped[str] = mapped_column(String(40))
    review_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str] = mapped_column(Text)
    evidence_added_count: Mapped[int] = mapped_column(Integer, default=0)
    severity_before: Mapped[str] = mapped_column(String(40))
    severity_after: Mapped[str] = mapped_column(String(40))
    public_explanation_before: Mapped[str | None] = mapped_column(Text)
    public_explanation_after: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RiskSuppression(Base):
    __tablename__ = "risk_suppressions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    risk_rule_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("risk_rules.id"))
    entity_type: Mapped[str | None] = mapped_column(String(80))
    entity_id: Mapped[uuid.UUID | None]
    institution_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("institutions.id"))
    reason: Mapped[str] = mapped_column(Text)
    valid_from: Mapped[date] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    approved_by_actor_id: Mapped[uuid.UUID] = mapped_column()
    source_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sources.id"))
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("evidence.id"))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RiskThreshold(Timestamps, Base):
    __tablename__ = "risk_thresholds"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    risk_rule_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("risk_rules.id"), index=True)
    scope_type: Mapped[str] = mapped_column(String(50))
    scope_id: Mapped[uuid.UUID | None]
    threshold_key: Mapped[str] = mapped_column(String(100))
    threshold_value: Mapped[dict[str, object]] = mapped_column(Json)
    valid_from: Mapped[date] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30))
    approved_by_actor_id: Mapped[uuid.UUID] = mapped_column()
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class RiskScore(Base):
    __tablename__ = "risk_scores"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(80), index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(index=True)
    calculation_date: Mapped[date] = mapped_column(Date, index=True)
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    total_score: Mapped[Decimal] = mapped_column(Numeric(7, 3))
    score_band: Mapped[str] = mapped_column(String(40), index=True)
    component_scores: Mapped[dict[str, object]] = mapped_column(Json)
    finding_count: Mapped[int] = mapped_column(Integer)
    high_priority_count: Mapped[int] = mapped_column(Integer)
    data_quality_penalty: Mapped[Decimal] = mapped_column(Numeric(7, 3))
    model_or_formula_version: Mapped[str] = mapped_column(String(80))
    evaluation_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("risk_evaluation_runs.id"))
    status: Mapped[str] = mapped_column(String(30))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    actor_type: Mapped[str] = mapped_column(String(30))
    actor_id: Mapped[uuid.UUID | None]
    action: Mapped[str] = mapped_column(String(60), index=True)
    entity_type: Mapped[str] = mapped_column(String(80), index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(index=True)
    previous_state: Mapped[dict[str, object] | None] = mapped_column(Json)
    new_state: Mapped[dict[str, object] | None] = mapped_column(Json)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    request_or_run_id: Mapped[uuid.UUID | None] = mapped_column(index=True)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
