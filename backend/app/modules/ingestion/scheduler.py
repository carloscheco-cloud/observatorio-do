from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.ingestion.models import IngestionJob, IngestionSchedule


class Scheduler:
    """Passive scheduler contract. Application startup never starts it implicitly."""

    def enqueue_due(self, db: Session, now: datetime | None = None) -> int:
        current = now or datetime.now(UTC)
        due = db.scalars(
            select(IngestionSchedule)
            .where(
                IngestionSchedule.enabled.is_(True),
                IngestionSchedule.next_run_at <= current,
            )
            .with_for_update(skip_locked=True)
        )
        count = 0
        for schedule in due:
            advisory_key = f"schedule:{schedule.id}:{schedule.next_run_at}"
            exists = db.scalar(
                select(IngestionJob.id).where(
                    IngestionJob.payload["idempotency_key"].as_string() == advisory_key
                )
            )
            if exists:
                continue
            configured_attempts = schedule.retry_policy.get("max_attempts", 3)
            max_attempts = configured_attempts if isinstance(configured_attempts, int) else 3
            db.add(
                IngestionJob(
                    id=uuid.uuid4(),
                    source_catalog_id=schedule.source_catalog_id,
                    job_type="scheduled_ingestion",
                    priority=100,
                    status="queued",
                    scheduled_at=current,
                    max_attempts=max_attempts,
                    payload={"idempotency_key": advisory_key, "schedule_id": str(schedule.id)},
                )
            )
            schedule.last_run_at = current
            count += 1
        return count
