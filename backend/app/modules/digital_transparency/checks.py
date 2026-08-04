from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.digital_transparency.models import (
    DigitalTransparencyLoadRecord,
    ResourceCheck,
    SearchabilityCheck,
)
from app.modules.digital_transparency.resource_checks import validate_resource_check
from app.modules.digital_transparency.schemas import (
    ResourceCheckCreate,
    SearchabilityCheckCreate,
)
from app.modules.digital_transparency.searchability_checks import validate_searchability_check

MANIFEST_PATH = Path(__file__).with_name("checks_manifest.json")
MANIFEST_VERSION = "PE-06A-2026-08-03"


@dataclass
class CheckRollbackSummary:
    removed: int = 0
    unchanged: int = 0
    errors: int = 0


def read_checks_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != MANIFEST_VERSION or data.get("schema_version") != "1":
        raise ValueError("unsupported PE-06A checks manifest")
    resource_checks = data.get("resource_checks")
    searchability_checks = data.get("searchability_checks")
    if not isinstance(resource_checks, list) or not isinstance(searchability_checks, list):
        raise ValueError("check collections must be lists")
    for raw in resource_checks:
        validate_resource_check(ResourceCheckCreate.model_validate(raw))
    for raw in searchability_checks:
        validate_searchability_check(SearchabilityCheckCreate.model_validate(raw))
    return data


def validate_manifest(path: Path = MANIFEST_PATH) -> dict[str, object]:
    data = read_checks_manifest(path)
    return {
        "version": data["version"],
        "schema_version": data["schema_version"],
        "resource_checks": len(data["resource_checks"]),
        "searchability_checks": len(data["searchability_checks"]),
        "valid": True,
    }


def checks_report(db: Session) -> dict[str, object]:
    owned = db.scalar(
        select(func.count())
        .select_from(DigitalTransparencyLoadRecord)
        .where(DigitalTransparencyLoadRecord.manifest_version == MANIFEST_VERSION)
    )
    return {
        "manifest": validate_manifest(),
        "resource_checks": db.scalar(select(func.count()).select_from(ResourceCheck)),
        "searchability_checks": db.scalar(select(func.count()).select_from(SearchabilityCheck)),
        "owned_by_pe06a": owned,
    }


def rollback_checks(db: Session, *, dry_run: bool = False) -> CheckRollbackSummary:
    records = list(
        db.scalars(
            select(DigitalTransparencyLoadRecord).where(
                DigitalTransparencyLoadRecord.manifest_version == MANIFEST_VERSION,
                DigitalTransparencyLoadRecord.record_type.in_(
                    ["resource_check", "searchability_check"]
                ),
            )
        )
    )
    result = CheckRollbackSummary()
    for kind, model in (
        ("resource_check", ResourceCheck),
        ("searchability_check", SearchabilityCheck),
    ):
        ids = [record.record_id for record in records if record.record_type == kind]
        if ids:
            db.execute(delete(model).where(model.id.in_(ids)))
            result.removed += len(ids)
    if records:
        db.execute(
            delete(DigitalTransparencyLoadRecord).where(
                DigitalTransparencyLoadRecord.id.in_([record.id for record in records])
            )
        )
        result.removed += len(records)
    else:
        result.unchanged = 1
    db.rollback() if dry_run else db.commit()
    return result


def summary_dict(value: CheckRollbackSummary) -> dict[str, int]:
    return asdict(value)
