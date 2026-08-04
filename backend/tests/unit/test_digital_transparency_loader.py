from datetime import timedelta
from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.appointments.models import Appointment
from app.modules.digital_transparency.loader import (
    audit_report,
    create_historical_assessment,
    load,
    recalculate,
    rollback,
)
from app.modules.digital_transparency.models import (
    AssessmentComponent,
    DigitalTransparencyLoadRecord,
    DocumentRequirement,
    DocumentResource,
    InformationRequest,
    ManualResearchTask,
    TransparencyAssessment,
    TransparencyObservation,
    VerificationStatus,
)
from app.modules.executive_authorities.loader import load_authorities
from app.modules.executive_inventory.loader import load_inventory
from app.modules.institutions.models import Institution
from app.modules.persons.models import Person


def test_load_dry_run_idempotence_recalculate_and_rollback(db: Session) -> None:
    load_inventory(db)
    load_authorities(db)
    preview = load(db, dry_run=True)
    assert preview.created > 0
    assert db.scalar(select(func.count()).select_from(DigitalTransparencyLoadRecord)) == 0
    first = load(db)
    second = load(db)
    assert first.created > 0 and second.created == 0
    assert db.scalar(select(func.count()).select_from(TransparencyAssessment)) == 25
    assert db.scalar(select(func.count()).select_from(AssessmentComponent)) == 75
    assert db.scalar(select(func.count()).select_from(TransparencyObservation)) == 75
    assert db.scalar(select(func.count()).select_from(ManualResearchTask)) == 3
    assert db.scalar(select(func.count()).select_from(InformationRequest)) == 0
    assert (
        db.scalar(
            select(func.count())
            .select_from(DocumentResource)
            .where(
                (DocumentResource.is_searchable.is_not(None))
                | (DocumentResource.has_ocr.is_not(None))
                | (DocumentResource.http_status.is_not(None))
                | (DocumentResource.checksum.is_not(None))
                | (DocumentResource.has_metadata.is_not(None))
            )
        )
        == 0
    )
    assert (
        db.scalar(
            select(func.count())
            .select_from(TransparencyObservation)
            .where(
                TransparencyObservation.verification_status
                == VerificationStatus.NOT_LOCATED_IN_REVIEWED_SOURCES
            )
        )
        == 3
    )
    tasks = list(db.scalars(select(ManualResearchTask)))
    task_people = {
        db.get(Person, db.get(Appointment, task.related_entity_id).person_id).full_name
        for task in tasks
    }
    assert task_people == {
        "Kelvin Antonio Cruz Cáceres",
        "Joel Adrián Santos Echavarría",
        "José Ignacio Paliza",
    }
    assert all(
        task.related_entity_type == "appointment"
        and task.document_type == "individual_appointment_act"
        and task.status.value == "open"
        and task.priority == "normal"
        and "no se presume que el acto no exista" in task.description
        and task.searched_sources
        and task.searched_sources[0]["reviewed_at"] == "2026-08-03T00:00:00-04:00"
        and db.get(Institution, task.institution_id).id
        == db.get(Appointment, task.related_entity_id).institution_id
        for task in tasks
    )
    assessment = db.scalar(select(TransparencyAssessment).limit(1))
    assert assessment is not None
    correct_score = assessment.score
    assessment.score = Decimal("0")
    db.commit()
    assert recalculate(db).created == 1
    assert db.get(TransparencyAssessment, assessment.id).score == correct_score
    report = audit_report(db)
    assert len(report) == 25
    assert all(item["coverage_percentage"] == "45.000" for item in report)
    assert all(item["classification_public"] == "evaluación parcial" for item in report)
    assert all(item["rank"] is None and item["comparison_position"] is None for item in report)
    assert all(len(item["evaluated_dimensions"]) == 3 for item in report)
    assert all(len(item["pending_dimensions"]) == 5 for item in report)
    existing_institutions = db.scalar(
        select(func.count()).select_from(
            __import__("app.modules.institutions.models", fromlist=["Institution"]).Institution
        )
    )
    rollback_preview = rollback(db, dry_run=True)
    assert (
        rollback_preview.removed > 0
        and db.scalar(select(func.count()).select_from(TransparencyAssessment)) == 25
    )
    rollback(db)
    assert db.scalar(select(func.count()).select_from(TransparencyAssessment)) == 0
    assert (
        db.scalar(
            select(func.count()).select_from(
                __import__("app.modules.institutions.models", fromlist=["Institution"]).Institution
            )
        )
        == existing_institutions
    )


def test_new_observation_creates_history_without_overwriting(db: Session) -> None:
    load_inventory(db)
    load_authorities(db)
    load(db)
    previous = db.scalar(
        select(TransparencyAssessment).where(TransparencyAssessment.unresolved_count == 1).limit(1)
    )
    assert previous is not None
    component = db.scalar(
        select(AssessmentComponent).where(
            AssessmentComponent.assessment_id == previous.id,
            AssessmentComponent.dimension == "appointment_acts",
        )
    )
    assert component is not None
    old_observation = db.get(TransparencyObservation, component.observation_id)
    assert old_observation is not None
    improved = TransparencyObservation(
        institution_id=old_observation.institution_id,
        requirement_id=old_observation.requirement_id,
        resource_id=None,
        verification_status=VerificationStatus.VERIFIED_DIGITALLY,
        observed_at=old_observation.observed_at + timedelta(days=1),
        reviewer_type=old_observation.reviewer_type,
        search_scope="Prueba controlada de historia; no es una observación de producción.",
        finding="Mejora simulada respaldada por la evidencia existente solo para probar historia.",
        confidence=old_observation.confidence,
        evidence_id=old_observation.evidence_id,
        methodology_version=old_observation.methodology_version,
    )
    db.add(improved)
    db.commit()
    original_score = previous.score
    historical = create_historical_assessment(
        db,
        previous.id,
        previous.assessment_date + timedelta(days=1),
        {"appointment_acts": (Decimal("16"), improved)},
    )
    assert historical.id != previous.id
    assert historical.score > original_score
    assert db.get(TransparencyAssessment, previous.id).score == original_score
    assert db.get(TransparencyObservation, old_observation.id) is not None
    assert (
        create_historical_assessment(
            db,
            previous.id,
            previous.assessment_date + timedelta(days=1),
            {"appointment_acts": (Decimal("16"), improved)},
        ).id
        == historical.id
    )
    previous.status = "published"
    previous.score = Decimal("0")
    db.commit()
    with pytest.raises(ValueError, match="published assessments are immutable"):
        recalculate(db)


def test_loaded_methodology_is_immutable(db: Session) -> None:
    load_inventory(db)
    load_authorities(db)
    load(db)
    requirement = db.scalar(
        select(DocumentRequirement).where(DocumentRequirement.code == "institutional_identity")
    )
    assert requirement is not None
    requirement.weight = Decimal("11")
    db.commit()
    with pytest.raises(ValueError, match="immutable"):
        load(db)
