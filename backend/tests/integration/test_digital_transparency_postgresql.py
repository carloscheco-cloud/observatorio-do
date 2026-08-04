import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.modules.digital_transparency.loader import load, recalculate, rollback
from app.modules.digital_transparency.models import (
    AssessmentComponent,
    DocumentResource,
    InformationRequest,
    ManualResearchTask,
    TransparencyAssessment,
    TransparencyObservation,
    VerificationStatus,
)
from app.modules.executive_authorities.loader import load_authorities
from app.modules.executive_inventory.loader import load_inventory
from tests.integration.test_postgresql_guards import migrate

pytestmark = pytest.mark.integration


def test_pe05_postgresql_load_recalculate_and_rollback(postgres_url: str) -> None:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with Session(engine) as db:
        load_inventory(db)
        load_authorities(db)
        preview = load(db, dry_run=True)
        assert preview.created == 258
        first = load(db)
        second = load(db)
        assert first.created == 258 and second.unchanged == 258
        assert db.scalar(select(func.count()).select_from(TransparencyAssessment)) == 25
        assert db.scalar(select(func.count()).select_from(AssessmentComponent)) == 75
        assert db.scalar(select(func.count()).select_from(DocumentResource)) == 72
        assert db.scalar(select(func.count()).select_from(TransparencyObservation)) == 75
        assert db.scalar(select(func.count()).select_from(ManualResearchTask)) == 3
        assert db.scalar(select(func.count()).select_from(InformationRequest)) == 0
        pending = db.scalar(
            select(func.count())
            .select_from(TransparencyObservation)
            .where(
                TransparencyObservation.verification_status
                == VerificationStatus.NOT_LOCATED_IN_REVIEWED_SOURCES
            )
        )
        assert pending == 3
        assessments = list(db.scalars(select(TransparencyAssessment)))
        assert all(item.coverage_percentage == 45 for item in assessments)
        assert all(item.maturity_status == "partial" for item in assessments)
        assert all(item.classification_public == "evaluación parcial" for item in assessments)
        assert all(item.rank is None and item.comparison_position is None for item in assessments)
        components = list(db.scalars(select(AssessmentComponent)))
        assert all(
            item.dimension
            and item.weight == item.maximum_score
            and item.verification_status
            and item.observation_id
            and item.evidence_id
            and item.methodology_version == "OED-TD-1.0"
            and item.calculation_reason
            for item in components
        )
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
        assert recalculate(db).unchanged == 25
        rollback(db)
        assert db.scalar(select(func.count()).select_from(TransparencyAssessment)) == 0
        assert db.scalar(select(func.count()).select_from(AssessmentComponent)) == 0
        assert db.scalar(select(func.count()).select_from(InformationRequest)) == 0
