# ruff: noqa: B008
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.ingestion import service
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
from app.modules.ingestion.schemas import (
    ArtifactRead,
    BatchRead,
    GenericRead,
    RecordRead,
    RunRead,
    ScheduleCreate,
    SourceCatalogCreate,
    SourceCatalogPatch,
    SourceCatalogRead,
)

router = APIRouter(prefix="/internal", tags=["controlled ingestion"])


def actor(x_actor_type: str = Header(default="human")) -> str:
    if x_actor_type not in {"human", "system", "service"}:
        raise HTTPException(403, "authorized internal actor required")
    return x_actor_type


def found[T](db: Session, model: type[T], identifier: uuid.UUID) -> T:
    try:
        return service.get_or_404(db, model, identifier)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/source-catalog", response_model=list[SourceCatalogRead])
def source_list(db: Session = Depends(get_db), _: str = Depends(actor)) -> list[SourceCatalog]:
    return service.list_models(db, SourceCatalog)


@router.post("/source-catalog", response_model=SourceCatalogRead, status_code=201)
def source_create(
    payload: SourceCatalogCreate, db: Session = Depends(get_db), _: str = Depends(actor)
) -> SourceCatalog:
    return service.create_source(db, payload)


@router.get("/source-catalog/{identifier}", response_model=SourceCatalogRead)
def source_get(
    identifier: uuid.UUID, db: Session = Depends(get_db), _: str = Depends(actor)
) -> object:
    return found(db, SourceCatalog, identifier)


@router.patch("/source-catalog/{identifier}", response_model=SourceCatalogRead)
def source_patch(
    identifier: uuid.UUID,
    payload: SourceCatalogPatch,
    db: Session = Depends(get_db),
    _: str = Depends(actor),
) -> SourceCatalog:
    return service.patch_source(db, found(db, SourceCatalog, identifier), payload)


@router.post("/source-catalog/{identifier}/test", response_model=RunRead)
@router.post("/source-catalog/{identifier}/discover", response_model=RunRead)
@router.post("/source-catalog/{identifier}/ingest", response_model=RunRead)
def source_action(
    identifier: uuid.UUID,
    dry_run: bool = Query(False),
    db: Session = Depends(get_db),
    current_actor: str = Depends(actor),
) -> IngestionRun:
    return service.start_run(
        db, found(db, SourceCatalog, identifier), "manual", current_actor, dry_run=dry_run
    )


@router.get("/ingestion-runs", response_model=list[RunRead])
def run_list(db: Session = Depends(get_db), _: str = Depends(actor)) -> list[IngestionRun]:
    return service.list_models(db, IngestionRun)


@router.get("/ingestion-runs/{identifier}", response_model=RunRead)
def run_get(
    identifier: uuid.UUID, db: Session = Depends(get_db), _: str = Depends(actor)
) -> object:
    return found(db, IngestionRun, identifier)


@router.post("/ingestion-runs/{identifier}/retry", response_model=RunRead)
def run_retry(
    identifier: uuid.UUID, db: Session = Depends(get_db), current_actor: str = Depends(actor)
) -> IngestionRun:
    return service.retry_run(db, found(db, IngestionRun, identifier), current_actor)


@router.post("/ingestion-runs/{identifier}/cancel", response_model=RunRead)
def run_cancel(
    identifier: uuid.UUID, db: Session = Depends(get_db), _: str = Depends(actor)
) -> IngestionRun:
    run = found(db, IngestionRun, identifier)
    if run.status in {
        "completed",
        "completed_with_warnings",
        "failed",
        "cancelled",
        "skipped_unchanged",
        "quarantined",
    }:
        raise HTTPException(409, "closed run cannot be cancelled")
    run.status = "cancelled"
    db.commit()
    return run


@router.get("/ingestion-runs/{identifier}/artifacts", response_model=list[ArtifactRead])
def artifacts(
    identifier: uuid.UUID, db: Session = Depends(get_db), _: str = Depends(actor)
) -> list[RawArtifact]:
    return list(db.scalars(select(RawArtifact).where(RawArtifact.ingestion_run_id == identifier)))


@router.get("/ingestion-runs/{identifier}/quality-issues", response_model=list[GenericRead])
def quality(
    identifier: uuid.UUID, db: Session = Depends(get_db), _: str = Depends(actor)
) -> list[DataQualityIssue]:
    return list(
        db.scalars(select(DataQualityIssue).where(DataQualityIssue.ingestion_run_id == identifier))
    )


@router.get("/staging-batches", response_model=list[BatchRead])
def batches(db: Session = Depends(get_db), _: str = Depends(actor)) -> list[StagingBatch]:
    return service.list_models(db, StagingBatch)


@router.get("/staging-batches/{identifier}", response_model=BatchRead)
def batch(identifier: uuid.UUID, db: Session = Depends(get_db), _: str = Depends(actor)) -> object:
    return found(db, StagingBatch, identifier)


@router.get("/staging-batches/{identifier}/records", response_model=list[RecordRead])
def records(
    identifier: uuid.UUID, db: Session = Depends(get_db), _: str = Depends(actor)
) -> list[StagingRecord]:
    return list(
        db.scalars(select(StagingRecord).where(StagingRecord.staging_batch_id == identifier))
    )


@router.post("/staging-records/{identifier}/approve-match", response_model=RecordRead)
@router.post("/staging-records/{identifier}/reject", response_model=RecordRead)
def review_record(
    identifier: uuid.UUID, db: Session = Depends(get_db), _: str = Depends(actor)
) -> StagingRecord:
    record = found(db, StagingRecord, identifier)
    record.validation_status = "rejected"
    record.canonical_action = "reject"
    db.commit()
    return record


@router.post("/staging-batches/{identifier}/canonicalize", response_model=BatchRead)
def canonicalize(
    identifier: uuid.UUID, db: Session = Depends(get_db), _: str = Depends(actor)
) -> StagingBatch:
    batch = found(db, StagingBatch, identifier)
    batch.status = "canonicalizing"
    db.commit()
    return batch


@router.get("/quarantine", response_model=list[GenericRead])
def quarantine(db: Session = Depends(get_db), _: str = Depends(actor)) -> list[QuarantineRecord]:
    return service.list_models(db, QuarantineRecord)


@router.post("/quarantine/{identifier}/review", response_model=GenericRead)
def review_quarantine(
    identifier: uuid.UUID, db: Session = Depends(get_db), _: str = Depends(actor)
) -> QuarantineRecord:
    item = found(db, QuarantineRecord, identifier)
    item.status = "reviewed"
    db.commit()
    return item


@router.get("/import-schemas", response_model=list[GenericRead])
def schemas(db: Session = Depends(get_db), _: str = Depends(actor)) -> list[ImportSchema]:
    return service.list_models(db, ImportSchema)


@router.post("/import-schemas", response_model=GenericRead, status_code=status.HTTP_201_CREATED)
@router.patch("/import-schemas/{identifier}", response_model=GenericRead)
def schema_write(
    identifier: uuid.UUID | None = None, db: Session = Depends(get_db), _: str = Depends(actor)
) -> object:
    if identifier:
        return found(db, ImportSchema, identifier)
    raise HTTPException(422, "schema body is required")


@router.get("/ingestion-schedules", response_model=list[GenericRead])
def schedules(db: Session = Depends(get_db), _: str = Depends(actor)) -> list[IngestionSchedule]:
    return service.list_models(db, IngestionSchedule)


@router.post("/ingestion-schedules", response_model=GenericRead, status_code=201)
def schedule_create(
    payload: ScheduleCreate, db: Session = Depends(get_db), _: str = Depends(actor)
) -> IngestionSchedule:
    item = IngestionSchedule(**payload.model_dump(), retry_policy={}, metadata_={})
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/ingestion-schedules/{identifier}", response_model=GenericRead)
def schedule_patch(
    identifier: uuid.UUID, db: Session = Depends(get_db), _: str = Depends(actor)
) -> object:
    return found(db, IngestionSchedule, identifier)


@router.get("/ingestion-metrics")
def ingestion_metrics(db: Session = Depends(get_db), _: str = Depends(actor)) -> dict[str, object]:
    return service.metrics(db)
