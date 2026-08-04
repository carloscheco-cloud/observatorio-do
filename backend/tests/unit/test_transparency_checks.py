from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.digital_transparency.checks import (
    MANIFEST_VERSION,
    checks_report,
    rollback_checks,
    validate_manifest,
)
from app.modules.digital_transparency.loader import load
from app.modules.digital_transparency.models import (
    DigitalTransparencyLoadRecord,
    DocumentResource,
    ResourceCheck,
    ResourceCheckStatus,
    ResourceCheckType,
    SearchabilityCheck,
    SearchabilityMethod,
    SearchabilityResult,
    TransparencyAssessment,
)
from app.modules.digital_transparency.resource_checks import create_resource_check
from app.modules.digital_transparency.schemas import (
    ResourceCheckCreate,
    SearchabilityCheckCreate,
)
from app.modules.digital_transparency.searchability_checks import create_searchability_check
from app.modules.executive_authorities.loader import load_authorities
from app.modules.executive_inventory.loader import load_inventory

NOW = datetime(2026, 8, 3, 12, tzinfo=UTC)


def _resource(db: Session) -> DocumentResource:
    load_inventory(db)
    load_authorities(db)
    load(db)
    resource = db.scalar(select(DocumentResource).limit(1))
    assert resource is not None
    return resource


def _http(resource: DocumentResource, **changes: object) -> ResourceCheckCreate:
    values: dict[str, object] = {
        "resource_id": str(resource.id),
        "checked_at": NOW,
        "check_type": ResourceCheckType.HTTP_AVAILABILITY,
        "status": ResourceCheckStatus.AVAILABLE,
        "http_status": 200,
        "attempt_number": 1,
        "user_agent": "OED-technical-fixture/1.0",
        "timeout_seconds": 10,
        "tool_name": "pytest-fixture",
        "tool_version": "1",
        "notes": "Fixture técnico simulado; no es una comprobación productiva.",
    }
    values.update(changes)
    return ResourceCheckCreate.model_validate(values)


def test_taxonomies_and_empty_productive_manifest() -> None:
    assert {item.value for item in ResourceCheckType} == {
        "http_availability",
        "redirect_resolution",
        "content_metadata",
    }
    assert len(ResourceCheckStatus) == 8
    assert len(SearchabilityMethod) == 4
    assert len(SearchabilityResult) == 5
    assert validate_manifest()["resource_checks"] == 0
    assert validate_manifest()["searchability_checks"] == 0


@pytest.mark.parametrize(
    ("http_status", "status"),
    [
        (200, ResourceCheckStatus.AVAILABLE),
        (403, ResourceCheckStatus.RESTRICTED),
        (429, ResourceCheckStatus.RATE_LIMITED),
        (404, ResourceCheckStatus.NOT_FOUND_PROVISIONAL),
        (500, ResourceCheckStatus.SOURCE_UNAVAILABLE),
        (503, ResourceCheckStatus.SOURCE_UNAVAILABLE),
    ],
)
def test_http_classifications(db: Session, http_status: int, status: ResourceCheckStatus) -> None:
    resource = _resource(db)
    item = create_resource_check(db, _http(resource, http_status=http_status, status=status))
    assert item.status == status and item.http_status == http_status


def test_redirect_timeout_dns_and_technical_error(db: Session) -> None:
    resource = _resource(db)
    redirected = create_resource_check(
        db,
        _http(
            resource,
            status=ResourceCheckStatus.AVAILABLE_WITH_REDIRECT,
            final_url="https://example.test/final",
            redirect_count=1,
        ),
    )
    assert redirected.final_url and redirected.redirect_count == 1
    for attempt, error in enumerate(("timeout", "dns"), start=2):
        item = create_resource_check(
            db,
            _http(
                resource,
                checked_at=NOW + timedelta(minutes=attempt),
                attempt_number=attempt,
                status=ResourceCheckStatus.SOURCE_UNAVAILABLE,
                http_status=None,
                error_type=error,
            ),
        )
        assert item.http_status is None
    certificate = create_resource_check(
        db,
        _http(
            resource,
            checked_at=NOW + timedelta(minutes=4),
            attempt_number=4,
            status=ResourceCheckStatus.TECHNICAL_ERROR,
            http_status=None,
            error_type="invalid_certificate",
        ),
    )
    assert certificate.status == ResourceCheckStatus.TECHNICAL_ERROR


def test_broken_link_confirmation_rules(db: Session) -> None:
    resource = _resource(db)
    with pytest.raises(ValueError, match="requires 410 or two"):
        create_resource_check(
            db,
            _http(
                resource,
                status=ResourceCheckStatus.BROKEN_LINK_CONFIRMED,
                http_status=404,
            ),
        )
    first = create_resource_check(
        db,
        _http(resource, status=ResourceCheckStatus.NOT_FOUND_PROVISIONAL, http_status=404),
    )
    second = create_resource_check(
        db,
        _http(
            resource,
            checked_at=NOW + timedelta(days=1),
            attempt_number=2,
            status=ResourceCheckStatus.BROKEN_LINK_CONFIRMED,
            http_status=404,
        ),
    )
    assert first.status == ResourceCheckStatus.NOT_FOUND_PROVISIONAL
    assert second.status == ResourceCheckStatus.BROKEN_LINK_CONFIRMED
    other = next(item for item in db.scalars(select(DocumentResource)) if item.id != resource.id)
    assert (
        create_resource_check(
            db,
            _http(
                other,
                status=ResourceCheckStatus.BROKEN_LINK_CONFIRMED,
                http_status=410,
            ),
        ).http_status
        == 410
    )


def test_history_duplicate_and_immutability(db: Session) -> None:
    resource = _resource(db)
    first = create_resource_check(db, _http(resource))
    db.commit()
    second = create_resource_check(
        db, _http(resource, checked_at=NOW + timedelta(hours=1), attempt_number=2)
    )
    db.commit()
    assert first.id != second.id
    first.notes = "mutated"
    with pytest.raises(ValueError, match="immutable"):
        db.commit()
    db.rollback()
    with pytest.raises(IntegrityError):
        create_resource_check(db, _http(resource))
    db.rollback()


def test_searchability_requires_observed_text_and_never_ocr(db: Session) -> None:
    resource = _resource(db)
    base = {
        "resource_id": str(resource.id),
        "checked_at": NOW,
        "method": SearchabilityMethod.PDF_TEXT_EXTRACTION,
        "result": SearchabilityResult.INCONCLUSIVE,
        "tool_name": "pytest-fixture",
        "tool_version": "1",
        "notes": "Fixture técnico simulado; no es una comprobación productiva.",
    }
    inconclusive = create_searchability_check(db, SearchabilityCheckCreate.model_validate(base))
    assert inconclusive.text_detected is None and inconclusive.selectable_text is None
    with pytest.raises(ValueError, match="extension is insufficient"):
        create_searchability_check(
            db,
            SearchabilityCheckCreate.model_validate(
                {**base, "result": SearchabilityResult.SEARCHABLE}
            ),
        )
    searchable = create_searchability_check(
        db,
        SearchabilityCheckCreate.model_validate(
            {
                **base,
                "checked_at": NOW + timedelta(minutes=1),
                "result": SearchabilityResult.SEARCHABLE,
                "text_detected": True,
                "selectable_text": True,
                "extracted_character_count": 42,
            }
        ),
    )
    assert searchable.text_detected is True and searchable.selectable_text is True
    with pytest.raises(ValueError, match="OCR"):
        create_searchability_check(
            db,
            SearchabilityCheckCreate.model_validate({**base, "tool_name": "OCR fixture"}),
        )


def test_pe06a_rollback_only_owned_checks_and_preserves_pe05(db: Session) -> None:
    resource = _resource(db)
    pe05_count = db.scalar(select(func.count()).select_from(TransparencyAssessment))
    owned = create_resource_check(db, _http(resource))
    unowned = create_searchability_check(
        db,
        SearchabilityCheckCreate(
            resource_id=str(resource.id),
            checked_at=NOW,
            method=SearchabilityMethod.MANUAL_REVIEW,
            result=SearchabilityResult.INCONCLUSIVE,
            tool_name="pytest-fixture",
            tool_version="1",
        ),
    )
    db.add(
        DigitalTransparencyLoadRecord(
            manifest_version=MANIFEST_VERSION,
            record_type="resource_check",
            record_id=owned.id,
        )
    )
    db.commit()
    preview = rollback_checks(db, dry_run=True)
    assert preview.removed == 2 and db.get(ResourceCheck, owned.id) is not None
    rollback_checks(db)
    assert db.get(ResourceCheck, owned.id) is None
    assert db.get(SearchabilityCheck, unowned.id) is not None
    assert db.scalar(select(func.count()).select_from(TransparencyAssessment)) == pe05_count == 25
    assert checks_report(db)["owned_by_pe06a"] == 0
