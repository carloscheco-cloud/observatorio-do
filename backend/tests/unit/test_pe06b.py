from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.digital_transparency.loader import load as load_pe05
from app.modules.digital_transparency.models import (
    AssessmentComponent,
    DigitalTransparencyLoadRecord,
    InformationRequest,
    ResourceCheck,
    ResourceCheckStatus,
    SearchabilityCheck,
    TransparencyAssessment,
    TransparencyObservation,
)
from app.modules.digital_transparency.pe06b import (
    MANIFEST_VERSION,
    audit_report,
    load,
    read_manifest,
    recalculate,
    rollback,
)
from app.modules.executive_authorities.loader import load_authorities
from app.modules.executive_inventory.loader import load_inventory


def _prepare(db: Session) -> None:
    load_inventory(db)
    load_authorities(db)
    load_pe05(db)


def test_manifest_has_exact_attribution_and_documental_fields() -> None:
    data = read_manifest()
    assert len(data["institutions"]) == 5
    assert all("presidencia" not in item["slug"] for item in data["institutions"])
    expected_hosts = {
        "map.gob.do",
        "hacienda.gob.do",
        "minerd.gob.do",
        "msp.gob.do",
        "ambiente.gob.do",
    }
    portals = {item["portal"].split("//", 1)[1].strip("/") for item in data["institutions"]}
    assert portals == expected_hosts
    for institution in data["institutions"]:
        dimensions = {item["dimension"] for item in institution["resources"]}
        assert dimensions == {
            "legal_framework",
            "organizational_structure",
            "official_contact_information",
        }
        assert all(
            item["excerpt"] and item["http"]["status"] == 200 for item in institution["resources"]
        )
    pdfs = [
        item
        for institution in data["institutions"]
        for item in institution["resources"]
        if item["type"] == "pdf"
    ]
    assert pdfs and all(item["search"]["method"] == "pdf_text_extraction" for item in pdfs)
    assert all(item["search"]["result"] == "searchable" for item in pdfs)
    technical = data["technical_checks"]
    assert len(technical) == 1
    assert technical[0]["http"]["error_type"] == "too_many_redirects"


def test_pe06b_history_coverage_ranking_and_rollback(db: Session) -> None:
    _prepare(db)
    pe05_ids = set(
        db.scalars(
            select(TransparencyAssessment.id).where(
                TransparencyAssessment.assessment_date == date(2026, 8, 3)
            )
        )
    )
    pe05_count = len(pe05_ids)
    preview = load(db, dry_run=True)
    assert preview.created > 0
    assert (
        db.scalar(
            select(func.count())
            .select_from(DigitalTransparencyLoadRecord)
            .where(DigitalTransparencyLoadRecord.manifest_version == MANIFEST_VERSION)
        )
        == 0
    )
    first = load(db)
    second = load(db)
    assert first.created > 0 and second.unchanged > 0
    assert db.scalar(select(func.count()).select_from(ResourceCheck)) == 16
    assert db.scalar(select(func.count()).select_from(SearchabilityCheck)) == 15
    assert db.scalar(select(func.count()).select_from(TransparencyObservation)) == 75 + 25
    assert (
        db.scalar(
            select(func.count())
            .select_from(ResourceCheck)
            .where(ResourceCheck.status == ResourceCheckStatus.TECHNICAL_ERROR)
        )
        == 1
    )
    assessments = list(
        db.scalars(
            select(TransparencyAssessment).where(
                TransparencyAssessment.assessor == "PE-06B controlled pilot"
            )
        )
    )
    assert len(assessments) == 5
    assert all(item.coverage_percentage == Decimal("45") for item in assessments)
    assert all(item.maturity_status == "partial" for item in assessments)
    assert all(item.rank is None and item.comparison_position is None for item in assessments)
    assert (
        db.scalar(
            select(func.count())
            .select_from(AssessmentComponent)
            .where(AssessmentComponent.assessment_id.in_([item.id for item in assessments]))
        )
        == 15
    )
    assert db.scalar(select(func.count()).select_from(AssessmentComponent)) == 90
    for assessment in assessments:
        components = list(
            db.scalars(
                select(AssessmentComponent).where(
                    AssessmentComponent.assessment_id == assessment.id
                )
            )
        )
        assert {item.dimension for item in components} == {
            "institutional_identity",
            "current_authorities",
            "appointment_acts",
        }
        assert all(
            "Heredado sin alteración de PE-05" in item.calculation_reason for item in components
        )
    assert db.scalar(select(func.count()).select_from(InformationRequest)) == 0
    assert recalculate(db).unchanged == 5
    report = audit_report(db)
    assert len(report) == 5 and all(
        item["rank"] is None and item["saip_requests"] == 0 for item in report
    )
    preview_rollback = rollback(db, dry_run=True)
    assert preview_rollback.removed > 0
    rollback(db)
    remaining_pe05 = set(
        db.scalars(
            select(TransparencyAssessment.id).where(
                TransparencyAssessment.assessment_date == date(2026, 8, 3)
            )
        )
    )
    assert remaining_pe05 == pe05_ids and len(remaining_pe05) == pe05_count == 25


def test_checks_are_append_only_history(db: Session) -> None:
    _prepare(db)
    load(db)
    check = db.scalar(select(ResourceCheck).limit(1))
    assert check is not None
    check.notes = "mutation is forbidden"
    try:
        db.flush()
    except ValueError as exc:
        db.rollback()
        assert "immutable historical records" in str(exc)
    else:  # pragma: no cover - invariant guard
        raise AssertionError("historical check mutation was accepted")
