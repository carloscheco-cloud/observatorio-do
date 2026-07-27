from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.ingestion.models import IngestionJob


def claim_next_job(db: Session, worker_id: str) -> IngestionJob | None:
    job = db.scalar(
        select(IngestionJob)
        .where(
            IngestionJob.status.in_(("queued", "retry")),
            IngestionJob.scheduled_at <= datetime.now(UTC),
            IngestionJob.attempts < IngestionJob.max_attempts,
        )
        .order_by(IngestionJob.priority, IngestionJob.scheduled_at)
        .with_for_update(skip_locked=True)
        .limit(1)
    )
    if job:
        job.status = "running"
        job.locked_by = worker_id
        job.locked_at = datetime.now(UTC)
        job.started_at = datetime.now(UTC)
        job.attempts += 1
        db.flush()
    return job


def retry_delay(attempt: int, maximum_seconds: int = 3600) -> timedelta:
    return timedelta(seconds=min(30 * (2 ** max(attempt - 1, 0)), maximum_seconds))


def recover_abandoned(db: Session, older_than: timedelta) -> int:
    cutoff = datetime.now(UTC) - older_than
    jobs = db.scalars(
        select(IngestionJob).where(
            IngestionJob.status == "running", IngestionJob.locked_at < cutoff
        )
    )
    count = 0
    for job in jobs:
        job.status = "retry" if job.attempts < job.max_attempts else "failed"
        job.locked_by = None
        job.locked_at = None
        count += 1
    return count
