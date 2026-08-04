from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.digital_transparency.models import SearchabilityCheck, SearchabilityResult
from app.modules.digital_transparency.schemas import SearchabilityCheckCreate


def validate_searchability_check(data: SearchabilityCheckCreate) -> None:
    if not data.tool_name.strip() or not data.tool_version.strip():
        raise ValueError("tool_name and tool_version are required")
    if data.selectable_text is True and data.text_detected is not True:
        raise ValueError("selectable_text requires detected text")
    if data.result == SearchabilityResult.SEARCHABLE and data.text_detected is not True:
        raise ValueError("searchable requires observed text; a PDF extension is insufficient")
    if data.extracted_character_count is not None and data.text_detected is not True:
        raise ValueError("extracted characters require detected text")
    if data.page_count is not None and data.page_count < 0:
        raise ValueError("page_count cannot be negative")
    if data.extracted_character_count is not None and data.extracted_character_count < 0:
        raise ValueError("extracted_character_count cannot be negative")
    if "ocr" in data.method.value or "ocr" in data.tool_name.casefold():
        raise ValueError("PE-06A does not permit OCR")


def create_searchability_check(db: Session, data: SearchabilityCheckCreate) -> SearchabilityCheck:
    validate_searchability_check(data)
    item = SearchabilityCheck(
        id=uuid.uuid4(),
        **data.model_dump(exclude={"resource_id", "evidence_id"}),
        resource_id=uuid.UUID(data.resource_id),
        evidence_id=uuid.UUID(data.evidence_id) if data.evidence_id else None,
    )
    db.add(item)
    db.flush()
    return item


def searchability_check_counts(db: Session) -> dict[str, int]:
    rows = db.execute(
        select(SearchabilityCheck.result, func.count()).group_by(SearchabilityCheck.result)
    )
    return {result.value: count for result, count in rows}
