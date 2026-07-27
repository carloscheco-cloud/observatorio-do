from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base

Json = JSON().with_variant(JSONB(), "postgresql")


class Timestamps:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class SourceCatalog(Timestamps, Base):
    __tablename__ = "source_catalog"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"), index=True)
    stable_code: Mapped[str] = mapped_column(String(100), unique=True)
    official_name: Mapped[str] = mapped_column(String(300))
    source_type: Mapped[str] = mapped_column(String(40))
    base_url: Mapped[str | None] = mapped_column(String(1000))
    jurisdiction: Mapped[str] = mapped_column(String(100))
    institution_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("institutions.id"))
    territory_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("territories.id"))
    data_domains: Mapped[list[object]] = mapped_column(Json, default=list)
    access_method: Mapped[str] = mapped_column(String(30))
    authentication_type: Mapped[str] = mapped_column(String(30), default="none")
    update_frequency: Mapped[str] = mapped_column(String(50))
    expected_formats: Mapped[list[object]] = mapped_column(Json, default=list)
    terms_or_license: Mapped[str | None] = mapped_column(Text)
    robots_policy: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(default=True)
    priority: Mapped[int] = mapped_column(Integer, default=100)
    reliability_level: Mapped[str] = mapped_column(String(30), default="unknown")
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_failure_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_expected_update_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), index=True
    )
    configuration: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_code: Mapped[str] = mapped_column(String(120), unique=True)
    source_catalog_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("source_catalog.id"), index=True
    )
    connector_type: Mapped[str] = mapped_column(String(50))
    trigger_type: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(40), index=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    requested_by_actor_type: Mapped[str] = mapped_column(String(30))
    requested_by_actor_id: Mapped[uuid.UUID | None]
    parent_run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ingestion_runs.id"))
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    configuration_snapshot: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    source_version: Mapped[str | None] = mapped_column(String(200))
    etag: Mapped[str | None] = mapped_column(String(500))
    last_modified: Mapped[str | None] = mapped_column(String(200))
    downloaded_files: Mapped[int] = mapped_column(Integer, default=0)
    discovered_records: Mapped[int] = mapped_column(Integer, default=0)
    parsed_records: Mapped[int] = mapped_column(Integer, default=0)
    valid_records: Mapped[int] = mapped_column(Integer, default=0)
    invalid_records: Mapped[int] = mapped_column(Integer, default=0)
    canonical_records_created: Mapped[int] = mapped_column(Integer, default=0)
    canonical_records_updated: Mapped[int] = mapped_column(Integer, default=0)
    canonical_records_unchanged: Mapped[int] = mapped_column(Integer, default=0)
    evidence_records_created: Mapped[int] = mapped_column(Integer, default=0)
    warnings_count: Mapped[int] = mapped_column(Integer, default=0)
    errors_count: Mapped[int] = mapped_column(Integer, default=0)
    error_summary: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    checksum: Mapped[str | None] = mapped_column(String(64), index=True)
    engine_version: Mapped[str] = mapped_column(String(30))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RawArtifact(Base):
    __tablename__ = "raw_artifacts"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ingestion_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ingestion_runs.id"), index=True)
    source_catalog_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("source_catalog.id"), index=True
    )
    artifact_type: Mapped[str] = mapped_column(String(30))
    original_filename: Mapped[str | None] = mapped_column(String(300))
    storage_key: Mapped[str] = mapped_column(String(700), unique=True)
    mime_type_detected: Mapped[str] = mapped_column(String(150))
    mime_type_reported: Mapped[str | None] = mapped_column(String(150))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    checksum_sha256: Mapped[str] = mapped_column(String(64), index=True)
    compression_type: Mapped[str | None] = mapped_column(String(30))
    encoding: Mapped[str | None] = mapped_column(String(50))
    downloaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    source_url: Mapped[str | None] = mapped_column(String(1000))
    http_status: Mapped[int | None]
    etag: Mapped[str | None] = mapped_column(String(500))
    last_modified: Mapped[str | None] = mapped_column(String(200))
    is_encrypted: Mapped[bool] = mapped_column(default=False)
    is_quarantined: Mapped[bool] = mapped_column(default=False)
    quarantine_reason: Mapped[str | None] = mapped_column(String(100))
    retention_policy: Mapped[str] = mapped_column(String(100))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())


class SourceDiscovery(Base):
    __tablename__ = "source_discoveries"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_catalog_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("source_catalog.id"), index=True
    )
    discovered_url: Mapped[str] = mapped_column(String(1000))
    title: Mapped[str | None] = mapped_column(String(400))
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    publication_date: Mapped[date | None] = mapped_column(Date, index=True)
    expected_period: Mapped[str | None] = mapped_column(String(100), index=True)
    format_hint: Mapped[str | None] = mapped_column(String(50))
    content_length: Mapped[int | None] = mapped_column(BigInteger)
    etag: Mapped[str | None] = mapped_column(String(500))
    last_modified: Mapped[str | None] = mapped_column(String(200))
    fingerprint: Mapped[str] = mapped_column(String(64), index=True)
    discovery_status: Mapped[str] = mapped_column(String(30), index=True)
    previous_discovery_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("source_discoveries.id")
    )
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class ImportSchema(Timestamps, Base):
    __tablename__ = "import_schemas"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stable_code: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(300))
    domain: Mapped[str] = mapped_column(String(80), index=True)
    version: Mapped[int]
    source_catalog_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("source_catalog.id"))
    target_entity_type: Mapped[str] = mapped_column(String(100), index=True)
    expected_columns: Mapped[list[object]] = mapped_column(Json, default=list)
    required_columns: Mapped[list[object]] = mapped_column(Json, default=list)
    optional_columns: Mapped[list[object]] = mapped_column(Json, default=list)
    column_aliases: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    data_types: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    transformations: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    validations: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    deduplication_config: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    canonical_service: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(30), index=True)
    valid_from: Mapped[date] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    approved_by_actor_id: Mapped[uuid.UUID | None]
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class ColumnMapping(Base):
    __tablename__ = "column_mappings"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    import_schema_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("import_schemas.id"), index=True)
    source_column: Mapped[str] = mapped_column(String(300))
    normalized_column: Mapped[str] = mapped_column(String(300))
    target_field: Mapped[str] = mapped_column(String(300))
    transformation_type: Mapped[str] = mapped_column(String(80))
    transformation_config: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    confidence_level: Mapped[str] = mapped_column(String(30))
    mapping_origin: Mapped[str] = mapped_column(String(30))
    approved: Mapped[bool] = mapped_column(default=False)
    approved_by_actor_id: Mapped[uuid.UUID | None]
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())


class StagingBatch(Timestamps, Base):
    __tablename__ = "staging_batches"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ingestion_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ingestion_runs.id"), index=True)
    import_schema_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("import_schemas.id"))
    domain: Mapped[str] = mapped_column(String(80), index=True)
    entity_type: Mapped[str] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(30), index=True)
    total_records: Mapped[int] = mapped_column(default=0)
    valid_records: Mapped[int] = mapped_column(default=0)
    invalid_records: Mapped[int] = mapped_column(default=0)
    duplicate_records: Mapped[int] = mapped_column(default=0)
    review_records: Mapped[int] = mapped_column(default=0)


class StagingRecord(Base):
    __tablename__ = "staging_records"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    staging_batch_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("staging_batches.id"), index=True
    )
    row_number: Mapped[int | None]
    source_path: Mapped[str | None] = mapped_column(String(1000))
    source_sheet: Mapped[str | None] = mapped_column(String(300))
    source_page: Mapped[int | None]
    raw_data: Mapped[dict[str, object]] = mapped_column(Json)
    normalized_data: Mapped[dict[str, object] | None] = mapped_column(Json)
    validation_status: Mapped[str] = mapped_column(String(30), index=True)
    validation_errors: Mapped[list[object]] = mapped_column(Json, default=list)
    validation_warnings: Mapped[list[object]] = mapped_column(Json, default=list)
    deduplication_key: Mapped[str | None] = mapped_column(String(300), index=True)
    matched_entity_id: Mapped[uuid.UUID | None]
    match_confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    canonical_action: Mapped[str] = mapped_column(String(20))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())


class DataQualityIssue(Timestamps, Base):
    __tablename__ = "data_quality_issues"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ingestion_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ingestion_runs.id"), index=True)
    staging_record_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("staging_records.id"), index=True
    )
    issue_code: Mapped[str] = mapped_column(String(100), index=True)
    domain: Mapped[str] = mapped_column(String(80), index=True)
    severity: Mapped[str] = mapped_column(String(30), index=True)
    issue_type: Mapped[str] = mapped_column(String(50))
    field_name: Mapped[str | None] = mapped_column(String(300))
    observed_value: Mapped[str | None] = mapped_column(Text)
    expected_value: Mapped[str | None] = mapped_column(Text)
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="open")
    resolution_notes: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class EntityMatchCandidate(Base):
    __tablename__ = "entity_match_candidates"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ingestion_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ingestion_runs.id"), index=True)
    staging_record_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("staging_records.id"), index=True
    )
    entity_type: Mapped[str] = mapped_column(String(100), index=True)
    candidate_entity_id: Mapped[uuid.UUID]
    match_method: Mapped[str] = mapped_column(String(50))
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 4))
    match_features: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    status: Mapped[str] = mapped_column(String(30), default="pending")
    reviewed_by_actor_id: Mapped[uuid.UUID | None]
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())


class DataLineageLink(Base):
    __tablename__ = "data_lineage_links"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ingestion_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ingestion_runs.id"), index=True)
    raw_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("raw_artifacts.id"), index=True
    )
    staging_record_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("staging_records.id"), index=True
    )
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("evidence.id"))
    canonical_entity_type: Mapped[str] = mapped_column(String(100), index=True)
    canonical_entity_id: Mapped[uuid.UUID] = mapped_column(index=True)
    canonical_field: Mapped[str | None] = mapped_column(String(300))
    lineage_type: Mapped[str] = mapped_column(String(30))
    transformation_path: Mapped[list[object]] = mapped_column(Json, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())


class IngestionVersion(Base):
    __tablename__ = "ingestion_versions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    previous_run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ingestion_runs.id"))
    new_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ingestion_runs.id"))
    source_catalog_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("source_catalog.id"))
    period: Mapped[str | None] = mapped_column(String(100))
    previous_checksum: Mapped[str | None] = mapped_column(String(64))
    new_checksum: Mapped[str] = mapped_column(String(64))
    rows_added: Mapped[int] = mapped_column(default=0)
    rows_removed: Mapped[int] = mapped_column(default=0)
    rows_modified: Mapped[int] = mapped_column(default=0)
    rows_unchanged: Mapped[int] = mapped_column(default=0)
    aggregate_differences: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())


class SourceQualityMetric(Base):
    __tablename__ = "source_quality_metrics"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_catalog_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("source_catalog.id"), index=True
    )
    calculation_date: Mapped[date] = mapped_column(Date, index=True)
    availability_score: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    timeliness_score: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    completeness_score: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    consistency_score: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    parseability_score: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    traceability_score: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    historical_stability_score: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    total_score: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    observations: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())


class IngestionSchedule(Timestamps, Base):
    __tablename__ = "ingestion_schedules"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_catalog_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("source_catalog.id"), index=True
    )
    schedule_type: Mapped[str] = mapped_column(String(30))
    cron_expression: Mapped[str | None] = mapped_column(String(100))
    interval_minutes: Mapped[int | None]
    timezone: Mapped[str] = mapped_column(String(80), default="America/Santo_Domingo")
    enabled: Mapped[bool] = mapped_column(default=False)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retry_policy: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    overlap_policy: Mapped[str] = mapped_column(String(30), default="skip")
    maximum_runtime_seconds: Mapped[int] = mapped_column(default=3600)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class IngestionJob(Timestamps, Base):
    __tablename__ = "ingestion_jobs"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ingestion_run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ingestion_runs.id"))
    source_catalog_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("source_catalog.id"), index=True
    )
    job_type: Mapped[str] = mapped_column(String(50))
    priority: Mapped[int] = mapped_column(default=100)
    status: Mapped[str] = mapped_column(String(30), index=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(default=0)
    max_attempts: Mapped[int] = mapped_column(default=3)
    locked_by: Mapped[str | None] = mapped_column(String(200))
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    last_error: Mapped[str | None] = mapped_column(Text)


class QuarantineRecord(Base):
    __tablename__ = "quarantine_records"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ingestion_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ingestion_runs.id"), index=True)
    raw_artifact_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("raw_artifacts.id"))
    staging_record_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("staging_records.id"))
    quarantine_reason: Mapped[str] = mapped_column(String(80))
    severity: Mapped[str] = mapped_column(String(30), index=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    status: Mapped[str] = mapped_column(String(30), default="pending")
    reviewed_by_actor_id: Mapped[uuid.UUID | None]
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolution: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
