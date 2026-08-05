from typing import Any

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.modules.digital_transparency.loader import load as load_pe05
from app.modules.digital_transparency.models import (
    AssessmentComponent,
    DigitalTransparencyLoadRecord,
    ResourceCheck,
    SearchabilityCheck,
    TransparencyAssessment,
    TransparencyMethodology,
    TransparencyObservation,
)
from app.modules.digital_transparency.pe06b import load as load_pe06b
from app.modules.digital_transparency.pe06d import (
    ASSESSOR,
    MANIFEST_VERSION,
    audit_report,
    load,
    recalculate,
    rollback,
)
from app.modules.evidence.models import Evidence
from app.modules.executive_authorities.loader import load_authorities
from app.modules.executive_dependencies.loader import load_dependencies
from app.modules.executive_inventory.loader import load_inventory
from app.modules.institutions.models import Institution
from tests.integration.test_postgresql_guards import migrate

pytestmark = pytest.mark.integration


def _count(db: Session, model: Any, *criteria: Any) -> int:
    return db.scalar(select(func.count()).select_from(model).where(*criteria)) or 0


def test_pe06d_round_trip_is_idempotent_and_preserves_history(postgres_url: str) -> None:
    migrate(postgres_url)
    with Session(create_engine(postgres_url)) as db:
        load_inventory(db)
        load_dependencies(db)
        load_authorities(db)
        load_pe05(db)
        load_pe06b(db)
        pilot_ids = set(
            db.scalars(
                select(Institution.id).where(
                    Institution.slug.in_(
                        [
                            "ministerio-de-administracion-publica",
                            "ministerio-de-hacienda-y-economia",
                            "ministerio-de-educacion",
                            "ministerio-de-salud-publica-y-asistencia-social",
                            "ministerio-de-medio-ambiente-y-recursos-naturales",
                        ]
                    )
                )
            )
        )
        pe05_assessments = list(
            db.scalars(
                select(TransparencyAssessment).where(
                    TransparencyAssessment.assessor == "PE-05 controlled loader",
                    TransparencyAssessment.institution_id.in_(pilot_ids),
                )
            )
        )
        pe05_components = list(
            db.scalars(
                select(AssessmentComponent).where(
                    AssessmentComponent.assessment_id.in_([item.id for item in pe05_assessments])
                )
            )
        )
        pe05_component_ids = {item.id for item in pe05_components}
        original_trace = {
            (assessment.institution_id, component.dimension): (
                component.observation_id,
                component.evidence_id,
                component.score,
                component.maximum_score,
            )
            for assessment in pe05_assessments
            for component in pe05_components
            if component.assessment_id == assessment.id
        }
        original_evidence_ids = {item.evidence_id for item in pe05_components}
        historical = (
            _count(
                db,
                TransparencyAssessment,
                TransparencyAssessment.assessor == "PE-05 controlled loader",
            ),
            _count(
                db,
                TransparencyAssessment,
                TransparencyAssessment.assessor == "PE-06B controlled pilot",
            ),
            _count(db, TransparencyObservation),
            _count(db, ResourceCheck),
            _count(db, SearchabilityCheck),
        )
        assert db.get(TransparencyMethodology, "OED-TD-1.1") is not None
        assert load(db, dry_run=True).created == 45
        assert _count(db, TransparencyAssessment, TransparencyAssessment.assessor == ASSESSOR) == 0
        assert load(db).created == 45
        second = load(db)
        assert second.created == 0 and second.unchanged == 45
        assessments = list(
            db.scalars(
                select(TransparencyAssessment).where(TransparencyAssessment.assessor == ASSESSOR)
            )
        )
        assert len(assessments) == 5
        assert (
            _count(
                db,
                TransparencyAssessment,
                TransparencyAssessment.assessor == "PE-05 controlled loader",
            )
            == 25
        )
        assert (
            _count(
                db,
                AssessmentComponent,
                AssessmentComponent.assessment_id.in_(
                    select(TransparencyAssessment.id).where(
                        TransparencyAssessment.assessor == "PE-05 controlled loader"
                    )
                ),
            )
            == 75
        )
        assert all(
            item.maximum_score == 100 and item.coverage_percentage == 100 for item in assessments
        )
        inherited_count = 0
        new_count = 0
        for assessment in assessments:
            components = list(
                db.scalars(
                    select(AssessmentComponent).where(
                        AssessmentComponent.assessment_id == assessment.id
                    )
                )
            )
            for component in components:
                if component.rule_code is None:
                    inherited_count += 1
                    assert (
                        component.observation_id,
                        component.evidence_id,
                        component.score,
                        component.maximum_score,
                    ) == original_trace[(assessment.institution_id, component.dimension)]
                else:
                    new_count += 1
        assert inherited_count == 15 and new_count == 25
        duplicate_assessments = db.execute(
            select(
                TransparencyAssessment.institution_id,
                TransparencyAssessment.methodology_version,
                TransparencyAssessment.assessment_date,
            )
            .group_by(
                TransparencyAssessment.institution_id,
                TransparencyAssessment.methodology_version,
                TransparencyAssessment.assessment_date,
            )
            .having(func.count() > 1)
        ).all()
        duplicate_components = db.execute(
            select(AssessmentComponent.assessment_id, AssessmentComponent.requirement_id)
            .group_by(AssessmentComponent.assessment_id, AssessmentComponent.requirement_id)
            .having(func.count() > 1)
        ).all()
        assert duplicate_assessments == [] and duplicate_components == []
        assert (
            _count(
                db,
                TransparencyAssessment,
                TransparencyAssessment.rank.is_not(None),
            )
            == 0
        )
        assert (
            _count(
                db,
                TransparencyAssessment,
                TransparencyAssessment.comparison_position.is_not(None),
            )
            == 0
        )
        owned_types = set(
            db.scalars(
                select(DigitalTransparencyLoadRecord.record_type).where(
                    DigitalTransparencyLoadRecord.manifest_version == MANIFEST_VERSION
                )
            )
        )
        assert owned_types == {"assessment", "component"}
        assert all(
            item.maturity_status == "complete"
            and item.rank is None
            and item.comparison_position is None
            for item in assessments
        )
        assert all(
            _count(db, AssessmentComponent, AssessmentComponent.assessment_id == item.id) == 8
            for item in assessments
        )
        assert recalculate(db).unchanged == 5
        report = audit_report(db)
        assert len(report) == 5
        assert all(
            isinstance(item["dimensions"], list) and len(item["dimensions"]) == 8 for item in report
        )
        assert rollback(db, dry_run=True).removed == 90
        assert rollback(db).removed == 90
        assert _count(db, TransparencyAssessment, TransparencyAssessment.assessor == ASSESSOR) == 0
        assert (
            _count(
                db,
                DigitalTransparencyLoadRecord,
                DigitalTransparencyLoadRecord.manifest_version == MANIFEST_VERSION,
            )
            == 0
        )
        assert set(db.scalars(select(AssessmentComponent.id))).issuperset(pe05_component_ids)
        assert set(db.scalars(select(Evidence.id))).issuperset(original_evidence_ids)
        assert historical == (
            _count(
                db,
                TransparencyAssessment,
                TransparencyAssessment.assessor == "PE-05 controlled loader",
            ),
            _count(
                db,
                TransparencyAssessment,
                TransparencyAssessment.assessor == "PE-06B controlled pilot",
            ),
            _count(db, TransparencyObservation),
            _count(db, ResourceCheck),
            _count(db, SearchabilityCheck),
        )
        assert load(db).created == 45
        assert load(db).unchanged == 45
