import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RiskTypeRead(OrmModel):
    id: uuid.UUID
    stable_code: str
    official_name: str
    description: str
    domain: str
    category: str
    default_severity: str
    status: str


class RiskRuleRead(OrmModel):
    id: uuid.UUID
    stable_code: str
    name: str
    description: str
    domain: str
    risk_type_id: uuid.UUID
    rule_type: str
    version: int
    severity: str
    threshold_config: dict[str, object]
    enabled: bool
    requires_human_review: bool


class RuleCreate(BaseModel):
    stable_code: str = Field(pattern=r"^[a-z0-9_.-]+$")
    name: str
    description: str
    domain: str
    risk_type_id: uuid.UUID
    rule_type: str
    severity: str
    threshold_config: dict[str, object] = Field(default_factory=dict)
    evaluation_window: dict[str, object] = Field(default_factory=dict)
    required_fields: list[object] = Field(default_factory=list)
    supported_entity_types: list[object] = Field(default_factory=list)
    public_message_template: str
    internal_message_template: str
    enabled: bool = False
    valid_from: date
    requires_human_review: bool = True
    created_by_actor_type: str = "human"

    @field_validator("public_message_template", "internal_message_template")
    @classmethod
    def safe_template(cls, value: str) -> str:
        if "__" in value or "{%" in value or "{{" in value:
            raise ValueError("Only simple named placeholders are allowed")
        return value


class FindingRead(OrmModel):
    id: uuid.UUID
    finding_code: str
    risk_type_id: uuid.UUID
    risk_rule_id: uuid.UUID
    evaluation_run_id: uuid.UUID
    domain: str
    entity_type: str
    entity_id: uuid.UUID
    institution_id: uuid.UUID | None
    person_id: uuid.UUID | None
    supplier_id: uuid.UUID | None
    territory_id: uuid.UUID | None
    period_start: date | None
    period_end: date | None
    observed_value: dict[str, object]
    comparison_value: dict[str, object] | None
    threshold_value: dict[str, object] | None
    title: str
    public_explanation: str
    severity: str
    confidence_level: str
    status: str
    first_detected_at: datetime
    last_detected_at: datetime
    occurrence_count: int
    evidence_count: int
    requires_human_review: bool
    visibility: str


class FindingInternalRead(FindingRead):
    internal_explanation: str
    reviewer_notes: str | None
    resolution_type: str | None
    resolution_summary: str | None


class ReviewCreate(BaseModel):
    reviewer_actor_id: uuid.UUID
    review_action: Literal[
        "confirm",
        "dismiss",
        "request_more_evidence",
        "change_severity",
        "merge_duplicate",
        "mark_resolved",
        "reopen",
        "suppress",
        "publish",
        "restrict",
        "other",
    ]
    new_status: str
    notes: str = Field(min_length=1, max_length=5000)
    severity: str | None = None
    public_explanation: str | None = None


class EvaluationRequest(BaseModel):
    trigger_type: str = "manual"
    domain: str | None = None
    institution_id: uuid.UUID | None = None
    rule_id: uuid.UUID | None = None
    period_start: date | None = None
    period_end: date | None = None
    dry_run: bool = False
    backfill: bool = False


class EvaluationRead(OrmModel):
    id: uuid.UUID
    run_code: str
    trigger_type: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    rules_requested: int
    rules_executed: int
    records_evaluated: int
    findings_created: int
    findings_updated: int
    findings_suppressed: int
    errors_count: int
    error_summary: dict[str, object]
    engine_version: str


class ScoreRead(OrmModel):
    entity_type: str
    entity_id: uuid.UUID
    calculation_date: date
    period_start: date
    period_end: date
    total_score: Decimal
    score_band: str
    component_scores: dict[str, object]
    finding_count: int
    high_priority_count: int
    data_quality_penalty: Decimal
    model_or_formula_version: str


class EvidenceLinkCreate(BaseModel):
    evidence_id: uuid.UUID
    source_id: uuid.UUID
    relationship_type: str = "supporting"
    relevance_score: Decimal | None = Field(default=None, ge=0, le=1)
    excerpt: str | None = Field(default=None, max_length=1000)


class RulePatch(BaseModel):
    enabled: bool | None = None
    valid_to: date | None = None


class SuppressionCreate(BaseModel):
    reviewer_actor_id: uuid.UUID
    reason: str = Field(min_length=1, max_length=5000)
    valid_to: date | None = None


class ScoreRequest(BaseModel):
    entity_type: str
    entity_id: uuid.UUID
    evaluation_run_id: uuid.UUID
    period_start: date
    period_end: date
