import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    event,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base

Json = JSON().with_variant(JSONB(), "postgresql")


class VerificationStatus(StrEnum):
    VERIFIED_DIGITALLY = "verified_digitally"
    VERIFIED_OFFLINE = "verified_offline"
    PARTIALLY_VERIFIED = "partially_verified"
    PENDING_MANUAL_SEARCH = "pending_manual_search"
    REQUESTED_VIA_SAIP = "requested_via_saip"
    NOT_LOCATED_IN_REVIEWED_SOURCES = "not_located_in_reviewed_sources"
    BROKEN_LINK = "broken_link"
    SOURCE_UNAVAILABLE = "source_unavailable"
    PUBLISHED_NOT_SEARCHABLE = "published_not_searchable"
    METADATA_INCOMPLETE = "metadata_incomplete"
    NOT_APPLICABLE = "not_applicable"


class ReviewerType(StrEnum):
    AUTOMATED = "automated"
    HUMAN = "human"
    HYBRID = "hybrid"


class ConfidenceLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ResearchTaskStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    AWAITING_RESPONSE = "awaiting_response"
    RESOLVED = "resolved"
    CLOSED_UNRESOLVED = "closed_unresolved"
    CANCELLED = "cancelled"


class InformationRequestStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    RESPONDED = "responded"
    PARTIALLY_RESPONDED = "partially_responded"
    DENIED = "denied"
    OVERDUE = "overdue"
    APPEALED = "appealed"
    CLOSED = "closed"


class ResourceCheckType(StrEnum):
    HTTP_AVAILABILITY = "http_availability"
    REDIRECT_RESOLUTION = "redirect_resolution"
    CONTENT_METADATA = "content_metadata"


class ResourceCheckStatus(StrEnum):
    AVAILABLE = "available"
    AVAILABLE_WITH_REDIRECT = "available_with_redirect"
    RESTRICTED = "restricted"
    RATE_LIMITED = "rate_limited"
    SOURCE_UNAVAILABLE = "source_unavailable"
    NOT_FOUND_PROVISIONAL = "not_found_provisional"
    BROKEN_LINK_CONFIRMED = "broken_link_confirmed"
    TECHNICAL_ERROR = "technical_error"


class SearchabilityMethod(StrEnum):
    HTML_TEXT_INSPECTION = "html_text_inspection"
    PDF_TEXT_EXTRACTION = "pdf_text_extraction"
    METADATA_INSPECTION = "metadata_inspection"
    MANUAL_REVIEW = "manual_review"


class SearchabilityResult(StrEnum):
    SEARCHABLE = "searchable"
    PARTIALLY_SEARCHABLE = "partially_searchable"
    NOT_SEARCHABLE = "not_searchable"
    INCONCLUSIVE = "inconclusive"
    TECHNICAL_ERROR = "technical_error"


class DocumentRequirement(Base):
    __tablename__ = "document_requirements"
    __table_args__ = (
        CheckConstraint("weight >= 0 AND weight <= 100"),
        CheckConstraint("active_to IS NULL OR active_to >= active_from"),
        UniqueConstraint("code", "methodology_version"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    scope: Mapped[str] = mapped_column(String(80), nullable=False)
    applicable_institution_types: Mapped[list[object]] = mapped_column(Json, default=list)
    weight: Mapped[Decimal] = mapped_column(Numeric(6, 3), nullable=False)
    required_by_law: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    legal_basis_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("legal_bases.id", ondelete="RESTRICT")
    )
    active_from: Mapped[date] = mapped_column(Date, nullable=False)
    active_to: Mapped[date | None] = mapped_column(Date)
    methodology_version: Mapped[str] = mapped_column(String(30), nullable=False)


class DocumentResource(Base):
    __tablename__ = "document_resources"
    __table_args__ = (UniqueConstraint("institution_id", "requirement_id", "canonical_url"),)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    requirement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("document_requirements.id", ondelete="RESTRICT"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(40), nullable=False)
    canonical_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False
    )
    publication_date: Mapped[date | None] = mapped_column(Date)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(150))
    language: Mapped[str | None] = mapped_column(String(20))
    checksum: Mapped[str | None] = mapped_column(String(64))
    is_downloadable: Mapped[bool | None] = mapped_column(Boolean)
    is_searchable: Mapped[bool | None] = mapped_column(Boolean)
    has_ocr: Mapped[bool | None] = mapped_column(Boolean)
    has_metadata: Mapped[bool | None] = mapped_column(Boolean)
    has_stable_url: Mapped[bool | None] = mapped_column(Boolean)
    http_status: Mapped[int | None] = mapped_column(Integer)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    archived_url: Mapped[str | None] = mapped_column(String(1000))
    notes: Mapped[str | None] = mapped_column(Text)


class ResourceCheck(Base):
    __tablename__ = "transparency_resource_checks"
    __table_args__ = (
        UniqueConstraint("resource_id", "checked_at", "check_type", "attempt_number"),
        CheckConstraint("attempt_number >= 1"),
        CheckConstraint("timeout_seconds > 0"),
        CheckConstraint("redirect_count IS NULL OR redirect_count >= 0"),
        CheckConstraint("response_time_ms IS NULL OR response_time_ms >= 0"),
        CheckConstraint("content_length IS NULL OR content_length >= 0"),
        CheckConstraint("http_status IS NULL OR (http_status >= 100 AND http_status <= 599)"),
        CheckConstraint("final_url IS NULL OR http_status IS NOT NULL"),
        CheckConstraint("status != 'RESTRICTED' OR http_status = 403"),
        CheckConstraint("status != 'RATE_LIMITED' OR http_status = 429"),
        CheckConstraint("status != 'NOT_FOUND_PROVISIONAL' OR http_status = 404"),
        CheckConstraint("status != 'BROKEN_LINK_CONFIRMED' OR http_status IN (404, 410)"),
        Index("ix_transparency_resource_checks_resource_checked", "resource_id", "checked_at"),
        Index("ix_transparency_resource_checks_status", "status"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    resource_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("document_resources.id", ondelete="RESTRICT"), nullable=False
    )
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    check_type: Mapped[ResourceCheckType] = mapped_column(Enum(ResourceCheckType), nullable=False)
    status: Mapped[ResourceCheckStatus] = mapped_column(Enum(ResourceCheckStatus), nullable=False)
    http_status: Mapped[int | None] = mapped_column(Integer)
    final_url: Mapped[str | None] = mapped_column(String(1000))
    redirect_count: Mapped[int | None] = mapped_column(Integer)
    response_time_ms: Mapped[int | None] = mapped_column(Integer)
    mime_type: Mapped[str | None] = mapped_column(String(150))
    content_length: Mapped[int | None] = mapped_column(Integer)
    error_type: Mapped[str | None] = mapped_column(String(80))
    error_message: Mapped[str | None] = mapped_column(Text)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    user_agent: Mapped[str] = mapped_column(String(300), nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tool_version: Mapped[str] = mapped_column(String(100), nullable=False)
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("evidence.id", ondelete="RESTRICT")
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class SearchabilityCheck(Base):
    __tablename__ = "transparency_searchability_checks"
    __table_args__ = (
        CheckConstraint("page_count IS NULL OR page_count >= 0"),
        CheckConstraint("extracted_character_count IS NULL OR extracted_character_count >= 0"),
        CheckConstraint("selectable_text IS NOT TRUE OR text_detected IS TRUE"),
        CheckConstraint("result != 'SEARCHABLE' OR text_detected IS TRUE"),
        Index("ix_transparency_searchability_checks_resource_checked", "resource_id", "checked_at"),
        Index("ix_transparency_searchability_checks_result", "result"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    resource_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("document_resources.id", ondelete="RESTRICT"), nullable=False
    )
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    method: Mapped[SearchabilityMethod] = mapped_column(Enum(SearchabilityMethod), nullable=False)
    result: Mapped[SearchabilityResult] = mapped_column(Enum(SearchabilityResult), nullable=False)
    text_detected: Mapped[bool | None] = mapped_column(Boolean)
    selectable_text: Mapped[bool | None] = mapped_column(Boolean)
    metadata_detected: Mapped[bool | None] = mapped_column(Boolean)
    title_detected: Mapped[bool | None] = mapped_column(Boolean)
    publication_date_detected: Mapped[bool | None] = mapped_column(Boolean)
    document_number_detected: Mapped[bool | None] = mapped_column(Boolean)
    page_count: Mapped[int | None] = mapped_column(Integer)
    extracted_character_count: Mapped[int | None] = mapped_column(Integer)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tool_version: Mapped[str] = mapped_column(String(100), nullable=False)
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("evidence.id", ondelete="RESTRICT")
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class TransparencyObservation(Base):
    __tablename__ = "transparency_observations"
    __table_args__ = (
        UniqueConstraint(
            "institution_id",
            "requirement_id",
            "evidence_id",
            "observed_at",
            "verification_status",
            name="uq_transparency_observation_logical",
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    requirement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("document_requirements.id", ondelete="RESTRICT"), nullable=False
    )
    resource_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("document_resources.id", ondelete="RESTRICT")
    )
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus), nullable=False
    )
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reviewer_type: Mapped[ReviewerType] = mapped_column(Enum(ReviewerType), nullable=False)
    search_scope: Mapped[str] = mapped_column(Text, nullable=False)
    finding: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[ConfidenceLevel] = mapped_column(Enum(ConfidenceLevel), nullable=False)
    evidence_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("evidence.id", ondelete="RESTRICT"), nullable=False
    )
    methodology_version: Mapped[str] = mapped_column(String(30), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class ManualResearchTask(Base):
    __tablename__ = "manual_research_tasks"
    __table_args__ = (
        UniqueConstraint(
            "institution_id",
            "related_entity_type",
            "related_entity_id",
            "document_type",
            name="uq_manual_research_task_logical",
        ),
        CheckConstraint("resolved_at IS NULL OR resolved_at >= created_at"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id", ondelete="RESTRICT"), nullable=False
    )
    related_entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    related_entity_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    document_type: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[ResearchTaskStatus] = mapped_column(Enum(ResearchTaskStatus), nullable=False)
    assigned_to: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    searched_sources: Mapped[list[object]] = mapped_column(Json, default=list, nullable=False)
    result_summary: Mapped[str | None] = mapped_column(Text)
    resolved_resource_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("document_resources.id", ondelete="RESTRICT")
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class InformationRequest(Base):
    __tablename__ = "information_requests"
    __table_args__ = (
        CheckConstraint("response_received_at IS NULL OR submitted_at IS NOT NULL"),
        CheckConstraint("legal_deadline IS NULL OR submitted_at IS NOT NULL"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id", ondelete="RESTRICT"), nullable=False
    )
    tracking_code: Mapped[str | None] = mapped_column(String(100))
    subject: Mapped[str] = mapped_column(String(300), nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    legal_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    response_received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[InformationRequestStatus] = mapped_column(
        Enum(InformationRequestStatus), nullable=False
    )
    response_summary: Mapped[str | None] = mapped_column(Text)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("document_resources.id", ondelete="RESTRICT")
    )
    public_contact_channel: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)


class TransparencyAssessment(Base):
    __tablename__ = "transparency_assessments"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= maximum_score"),
        CheckConstraint("normalized_score >= 0 AND normalized_score <= 100"),
        CheckConstraint("coverage_percentage >= 0 AND coverage_percentage <= 100"),
        CheckConstraint(
            "coverage_percentage >= 60 OR (maturity_status = 'partial' "
            "AND classification_public = 'evaluación parcial' AND rank IS NULL "
            "AND comparison_position IS NULL)",
            name="ck_partial_assessment_not_ranked",
        ),
        UniqueConstraint("institution_id", "methodology_version", "assessment_date"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    methodology_version: Mapped[str] = mapped_column(String(30), nullable=False)
    assessment_date: Mapped[date] = mapped_column(Date, nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(7, 3), nullable=False)
    maximum_score: Mapped[Decimal] = mapped_column(Numeric(7, 3), nullable=False)
    normalized_score: Mapped[Decimal] = mapped_column(Numeric(7, 3), nullable=False)
    coverage_percentage: Mapped[Decimal] = mapped_column(Numeric(6, 3), nullable=False)
    observations_count: Mapped[int] = mapped_column(Integer, nullable=False)
    verified_count: Mapped[int] = mapped_column(Integer, nullable=False)
    unresolved_count: Mapped[int] = mapped_column(Integer, nullable=False)
    broken_links_count: Mapped[int] = mapped_column(Integer, nullable=False)
    assessor: Mapped[str] = mapped_column(String(100), nullable=False)
    calculation_details: Mapped[dict[str, object]] = mapped_column(Json, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    maturity_status: Mapped[str] = mapped_column(String(30), nullable=False)
    classification_public: Mapped[str] = mapped_column(String(100), nullable=False)
    rank: Mapped[int | None] = mapped_column(Integer)
    comparison_position: Mapped[str | None] = mapped_column(String(100))


class TransparencyMethodology(Base):
    __tablename__ = "transparency_methodologies"
    __table_args__ = (CheckConstraint("status IN ('draft', 'published', 'retired')"),)
    version: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    supersedes_version: Mapped[str | None] = mapped_column(
        ForeignKey("transparency_methodologies.version", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    is_immutable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class TransparencyScoringRule(Base):
    __tablename__ = "transparency_scoring_rules"
    __table_args__ = (
        UniqueConstraint("methodology_version", "dimension", "rule_code"),
        CheckConstraint("awarded_score >= 0 AND awarded_score <= maximum_score"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    methodology_version: Mapped[str] = mapped_column(
        ForeignKey("transparency_methodologies.version", ondelete="RESTRICT"), nullable=False
    )
    dimension: Mapped[str] = mapped_column(String(80), nullable=False)
    rule_code: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    awarded_score: Mapped[Decimal] = mapped_column(Numeric(7, 3), nullable=False)
    maximum_score: Mapped[Decimal] = mapped_column(Numeric(7, 3), nullable=False)
    conditions_json: Mapped[dict[str, object]] = mapped_column(Json, nullable=False)
    public_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    quality_level: Mapped[str | None] = mapped_column(String(30))
    severity: Mapped[str | None] = mapped_column(String(30))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class AssessmentComponent(Base):
    __tablename__ = "transparency_assessment_components"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= maximum_score"),
        CheckConstraint("weight = maximum_score"),
        UniqueConstraint("assessment_id", "requirement_id"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transparency_assessments.id", ondelete="CASCADE"), nullable=False
    )
    requirement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("document_requirements.id", ondelete="RESTRICT"), nullable=False
    )
    dimension: Mapped[str] = mapped_column(String(80), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(7, 3), nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(7, 3), nullable=False)
    maximum_score: Mapped[Decimal] = mapped_column(Numeric(7, 3), nullable=False)
    is_applicable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    observation_ids: Mapped[list[object]] = mapped_column(Json, nullable=False)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus), nullable=False
    )
    observation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transparency_observations.id", ondelete="RESTRICT"), nullable=False
    )
    evidence_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("evidence.id", ondelete="RESTRICT"), nullable=False
    )
    methodology_version: Mapped[str] = mapped_column(String(30), nullable=False)
    calculation_reason: Mapped[str] = mapped_column(Text, nullable=False)
    rule_code: Mapped[str | None] = mapped_column(String(100))
    public_explanation: Mapped[str | None] = mapped_column(Text)


class DigitalTransparencyLoadRecord(Base):
    __tablename__ = "digital_transparency_load_records"
    __table_args__ = (
        UniqueConstraint("manifest_version", "record_type", "record_id"),
        Index("ix_digital_transparency_record_lookup", "manifest_version", "record_type"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    manifest_version: Mapped[str] = mapped_column(String(50), nullable=False)
    record_type: Mapped[str] = mapped_column(String(50), nullable=False)
    record_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


def _reject_historical_mutation(*_: object) -> None:
    raise ValueError("technical checks are immutable historical records")


def _reject_published_methodology_mutation(_: object, target: object, __: object) -> None:
    if isinstance(target, TransparencyMethodology) and target.is_immutable:
        raise ValueError("published methodologies are immutable")


for _historical_model in (ResourceCheck, SearchabilityCheck):
    event.listen(_historical_model, "before_update", _reject_historical_mutation)
    event.listen(_historical_model, "before_delete", _reject_historical_mutation)
for _operation in ("before_update", "before_delete"):
    event.listen(TransparencyMethodology, _operation, _reject_published_methodology_mutation)
