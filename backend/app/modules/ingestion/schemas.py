from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SourceCatalogCreate(BaseModel):
    source_id: uuid.UUID
    stable_code: str = Field(min_length=2, max_length=100)
    official_name: str
    source_type: str
    base_url: HttpUrl | None = None
    jurisdiction: str
    data_domains: list[str] = Field(default_factory=list)
    access_method: str
    authentication_type: str = "none"
    update_frequency: str
    expected_formats: list[str] = Field(default_factory=list)
    active: bool = True
    priority: int = 100
    reliability_level: str = "unknown"
    configuration: dict[str, object] = Field(default_factory=dict)
    metadata: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def no_secrets(self) -> SourceCatalogCreate:
        forbidden = {"password", "token", "secret", "api_key", "authorization", "cookie"}
        if forbidden & {key.lower() for key in self.configuration}:
            raise ValueError("configuration must reference secrets through environment variables")
        return self


class SourceCatalogPatch(BaseModel):
    official_name: str | None = None
    active: bool | None = None
    priority: int | None = None
    update_frequency: str | None = None
    configuration: dict[str, object] | None = None
    metadata: dict[str, object] | None = None


class SourceCatalogRead(OrmModel):
    id: uuid.UUID
    stable_code: str
    official_name: str
    source_type: str
    base_url: str | None
    access_method: str
    active: bool


class RunRead(OrmModel):
    id: uuid.UUID
    run_code: str
    source_catalog_id: uuid.UUID
    status: str
    started_at: datetime
    completed_at: datetime | None
    valid_records: int
    invalid_records: int
    warnings_count: int
    errors_count: int


class ArtifactRead(OrmModel):
    id: uuid.UUID
    artifact_type: str
    storage_key: str
    mime_type_detected: str
    size_bytes: int
    checksum_sha256: str
    is_quarantined: bool


class BatchRead(OrmModel):
    id: uuid.UUID
    ingestion_run_id: uuid.UUID
    domain: str
    entity_type: str
    status: str
    total_records: int


class RecordRead(OrmModel):
    id: uuid.UUID
    row_number: int | None
    validation_status: str
    canonical_action: str
    normalized_data: dict[str, object] | None


class GenericRead(OrmModel):
    id: uuid.UUID
    status: str | None = None


class ScheduleCreate(BaseModel):
    source_catalog_id: uuid.UUID
    schedule_type: str
    cron_expression: str | None = None
    interval_minutes: int | None = Field(default=None, gt=0)
    timezone: str = "America/Santo_Domingo"
    enabled: bool = False
    overlap_policy: str = "skip"
    maximum_runtime_seconds: int = Field(default=3600, gt=0)

    @model_validator(mode="after")
    def valid_schedule(self) -> ScheduleCreate:
        if (self.cron_expression is None) == (self.interval_minutes is None):
            raise ValueError("exactly one schedule expression is required")
        return self
