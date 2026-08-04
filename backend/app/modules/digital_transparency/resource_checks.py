from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.digital_transparency.models import (
    ResourceCheck,
    ResourceCheckStatus,
)
from app.modules.digital_transparency.schemas import ResourceCheckCreate


def validate_resource_check(
    data: ResourceCheckCreate, prior_statuses: list[int] | None = None
) -> None:
    prior_statuses = prior_statuses or []
    if data.attempt_number < 1 or data.timeout_seconds < 1:
        raise ValueError("attempt_number and timeout_seconds must be positive")
    if not data.user_agent.strip() or not data.tool_name.strip() or not data.tool_version.strip():
        raise ValueError("user_agent, tool_name and tool_version are required")
    if data.http_status is None and data.final_url is not None:
        raise ValueError("final_url requires an observed HTTP response")
    if data.http_status is None and data.status in {
        ResourceCheckStatus.AVAILABLE,
        ResourceCheckStatus.AVAILABLE_WITH_REDIRECT,
        ResourceCheckStatus.RESTRICTED,
        ResourceCheckStatus.RATE_LIMITED,
        ResourceCheckStatus.NOT_FOUND_PROVISIONAL,
        ResourceCheckStatus.BROKEN_LINK_CONFIRMED,
    }:
        raise ValueError("the selected status requires an HTTP response")
    expected = {
        ResourceCheckStatus.AVAILABLE: range(200, 300),
        ResourceCheckStatus.AVAILABLE_WITH_REDIRECT: range(200, 300),
        ResourceCheckStatus.RESTRICTED: (403,),
        ResourceCheckStatus.RATE_LIMITED: (429,),
        ResourceCheckStatus.NOT_FOUND_PROVISIONAL: (404,),
    }
    if data.status in expected and data.http_status not in expected[data.status]:
        raise ValueError("HTTP status is inconsistent with the technical classification")
    if data.status == ResourceCheckStatus.AVAILABLE_WITH_REDIRECT and not (
        data.final_url and data.redirect_count and data.redirect_count > 0
    ):
        raise ValueError("available_with_redirect requires an observed redirect")
    if data.http_status == 403 and data.status != ResourceCheckStatus.RESTRICTED:
        raise ValueError("403 must be classified as restricted")
    if data.http_status == 429 and data.status != ResourceCheckStatus.RATE_LIMITED:
        raise ValueError("429 must be classified as rate_limited")
    if data.http_status == 404 and data.status not in {
        ResourceCheckStatus.NOT_FOUND_PROVISIONAL,
        ResourceCheckStatus.BROKEN_LINK_CONFIRMED,
    }:
        raise ValueError("a single 404 is provisional")
    if data.status == ResourceCheckStatus.BROKEN_LINK_CONFIRMED:
        unequivocal = data.http_status == 410
        repeated = (
            data.http_status in {404, 410}
            and sum(status in {404, 410} for status in prior_statuses) >= 1
        )
        if not (unequivocal or repeated):
            raise ValueError("broken_link_confirmed requires 410 or two 404/410 checks")
    if (
        data.http_status is not None
        and 500 <= data.http_status <= 599
        and data.status != ResourceCheckStatus.SOURCE_UNAVAILABLE
    ):
        raise ValueError("5xx must be classified as source_unavailable")


def create_resource_check(db: Session, data: ResourceCheckCreate) -> ResourceCheck:
    prior = list(
        db.scalars(
            select(ResourceCheck.http_status).where(
                ResourceCheck.resource_id == uuid.UUID(data.resource_id)
            )
        )
    )
    validate_resource_check(data, [code for code in prior if code is not None])
    item = ResourceCheck(
        id=uuid.uuid4(),
        **data.model_dump(exclude={"resource_id", "evidence_id"}),
        resource_id=uuid.UUID(data.resource_id),
        evidence_id=uuid.UUID(data.evidence_id) if data.evidence_id else None,
    )
    db.add(item)
    db.flush()
    return item


def resource_check_counts(db: Session) -> dict[str, int]:
    rows = db.execute(select(ResourceCheck.status, func.count()).group_by(ResourceCheck.status))
    return {status.value: count for status, count in rows}
