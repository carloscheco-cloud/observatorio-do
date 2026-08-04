from datetime import date

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from alembic import command
from app.modules.evidence.models import Evidence
from app.modules.executive_dependencies.loader import (
    load_dependencies,
    read_manifest,
    rollback_dependencies,
)
from app.modules.executive_dependencies.models import ExecutiveDependencyLoadRecord
from app.modules.executive_inventory.loader import load_inventory
from app.modules.executive_inventory.loader import read_manifest as read_pe02_manifest
from app.modules.institutions.models import (
    Institution,
    InstitutionEvidence,
    InstitutionRelationship,
    InstitutionRelationshipType,
)
from tests.integration.test_postgresql_guards import BACKEND_DIR, migrate

pytestmark = pytest.mark.integration


def test_dependencies_are_traceable_historical_and_idempotent(postgres_url: str) -> None:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with Session(engine) as db:
        load_inventory(db)
        first = load_dependencies(db)
        initial = db.scalar(select(func.count()).select_from(InstitutionRelationship))
        second = load_dependencies(db)
        assert first.created == 4
        assert second.unchanged == 4
        assert db.scalar(select(func.count()).select_from(InstitutionRelationship)) == initial == 2
        manifest = read_manifest()
        slugs = [item["slug"] for item in manifest["institutions"]]
        ids = select(Institution.id).where(Institution.slug.in_(slugs))
        assert (
            db.scalar(
                select(func.count())
                .select_from(InstitutionEvidence)
                .where(InstitutionEvidence.institution_id.in_(ids))
            )
            == 2
        )
        relationships = list(db.scalars(select(InstitutionRelationship)))
        assert all(db.get(Evidence, item.evidence_id) is not None for item in relationships)


def test_change_of_attachment_preserves_closed_history(postgres_url: str) -> None:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with Session(engine) as db:
        load_inventory(db)
        load_dependencies(db)
        relation = db.scalar(
            select(InstitutionRelationship).where(
                InstitutionRelationship.relationship_type == InstitutionRelationshipType.ATTACHED
            )
        )
        assert relation is not None
        relation.valid_to = date(2098, 12, 31)
        db.commit()
        simulated = InstitutionRelationship(
            parent_institution_id=relation.parent_institution_id,
            child_institution_id=relation.child_institution_id,
            relationship_type=relation.relationship_type,
            valid_from=date(2099, 1, 1),
            valid_to=None,
            notes="Cambio simulado exclusivamente para probar preservación histórica.",
            evidence_id=relation.evidence_id,
        )
        db.add(simulated)
        db.commit()
        assert (
            db.scalar(
                select(func.count())
                .select_from(InstitutionRelationship)
                .where(
                    InstitutionRelationship.child_institution_id == relation.child_institution_id
                )
            )
            == 2
        )
        db.delete(simulated)
        relation.valid_to = None
        db.commit()


def test_complete_data_rollback_and_schema_reversibility(postgres_url: str) -> None:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with Session(engine) as db:
        rollback_dependencies(db)
        load_inventory(db)
        pe02_manifest = read_pe02_manifest()
        pe02_slugs = select(Institution.id).where(
            Institution.slug.in_([item["slug"] for item in pe02_manifest["institutions"]])
        )
        pe02_count = db.scalar(select(func.count()).select_from(pe02_slugs.subquery()))
        assert pe02_count == 25
        first = load_dependencies(db)
        assert first.created == 4
        assert db.scalar(select(func.count()).select_from(ExecutiveDependencyLoadRecord)) == 14
        assert db.scalar(select(func.count()).select_from(InstitutionRelationship)) == 2
        preview = rollback_dependencies(db, dry_run=True)
        assert preview.removed == 14
        assert db.scalar(select(func.count()).select_from(InstitutionRelationship)) == 2
        removed = rollback_dependencies(db)
        assert removed.removed == 14
        assert db.scalar(select(func.count()).select_from(InstitutionRelationship)) == 0
        assert db.scalar(select(func.count()).select_from(pe02_slugs.subquery())) == pe02_count
    engine.dispose()

    config = Config(BACKEND_DIR / "alembic.ini")
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", postgres_url)
    command.downgrade(config, "0012")
    command.upgrade(config, "head")

    engine = create_engine(postgres_url)
    with Session(engine) as db:
        reloaded = load_dependencies(db)
        unchanged = load_dependencies(db)
        assert reloaded.created == 4
        assert unchanged.unchanged == 4
        duplicate_slugs = (
            select(Institution.slug)
            .where(Institution.slug.is_not(None))
            .group_by(Institution.slug)
            .having(func.count() > 1)
        )
        duplicate_relationships = (
            select(
                InstitutionRelationship.parent_institution_id,
                InstitutionRelationship.child_institution_id,
                InstitutionRelationship.relationship_type,
                InstitutionRelationship.valid_from,
            )
            .group_by(
                InstitutionRelationship.parent_institution_id,
                InstitutionRelationship.child_institution_id,
                InstitutionRelationship.relationship_type,
                InstitutionRelationship.valid_from,
            )
            .having(func.count() > 1)
        )
        assert db.scalar(select(func.count()).select_from(duplicate_slugs.subquery())) == 0
        assert db.scalar(select(func.count()).select_from(duplicate_relationships.subquery())) == 0
