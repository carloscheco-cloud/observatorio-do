from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.ingestion.models import (
    DataQualityIssue,
    ImportSchema,
    IngestionRun,
    IngestionSchedule,
    QuarantineRecord,
    RawArtifact,
    SourceCatalog,
    StagingBatch,
    StagingRecord,
)
from app.modules.ingestion.schemas import SourceCatalogCreate, SourceCatalogPatch
from app.modules.ingestion.security import validate_public_url


def list_models[T](db: Session, model: type[T]) -> list[T]:
    return list(db.scalars(select(model)))


def get_or_404[T](db: Session, model: type[T], identifier: uuid.UUID) -> T:
    value = db.get(model, identifier)
    if value is None:
        raise LookupError(f"{model.__name__} not found")
    return value


def create_source(db: Session, payload: SourceCatalogCreate) -> SourceCatalog:
    values = payload.model_dump(mode="python")
    values["base_url"] = str(values["base_url"]) if values["base_url"] else None
    values["metadata_"] = values.pop("metadata")
    if values["base_url"]:
        validate_public_url(values["base_url"])
    source = SourceCatalog(**values)
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def patch_source(db: Session, source: SourceCatalog, payload: SourceCatalogPatch) -> SourceCatalog:
    values = payload.model_dump(exclude_unset=True)
    if "metadata" in values:
        values["metadata_"] = values.pop("metadata")
    for key, value in values.items():
        setattr(source, key, value)
    db.commit()
    db.refresh(source)
    return source


def start_run(
    db: Session, source: SourceCatalog, trigger: str, actor_type: str, *, dry_run: bool = False
) -> IngestionRun:
    run = IngestionRun(
        run_code=f"{source.stable_code}-{uuid.uuid4().hex[:12]}",
        source_catalog_id=source.id,
        connector_type=source.access_method,
        trigger_type=trigger,
        status="completed" if dry_run else "queued",
        requested_by_actor_type=actor_type,
        attempt_number=1,
        configuration_snapshot=source.configuration,
        engine_version="11.0",
        completed_at=datetime.now(UTC) if dry_run else None,
        metadata_={"dry_run": dry_run},
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def retry_run(db: Session, previous: IngestionRun, actor_type: str) -> IngestionRun:
    source = get_or_404(db, SourceCatalog, previous.source_catalog_id)
    run = start_run(db, source, "retry", actor_type)
    run.parent_run_id = previous.id
    run.attempt_number = previous.attempt_number + 1
    db.commit()
    return run


def metrics(db: Session) -> dict[str, object]:
    statuses = db.execute(
        select(IngestionRun.status, func.count()).group_by(IngestionRun.status)
    ).all()
    pending = db.scalar(
        select(func.count()).select_from(IngestionRun).where(IngestionRun.status == "queued")
    )
    return {
        "runs_by_status": {row[0]: row[1] for row in statuses},
        "pending_runs": pending or 0,
    }


READ_MODELS: dict[str, type[Any]] = {
    "runs": IngestionRun,
    "artifacts": RawArtifact,
    "batches": StagingBatch,
    "records": StagingRecord,
    "quality": DataQualityIssue,
    "quarantine": QuarantineRecord,
    "schemas": ImportSchema,
    "schedules": IngestionSchedule,
}
