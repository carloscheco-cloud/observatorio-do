import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.modules.evidence.models import Evidence
from app.modules.executive_inventory.loader import load_inventory, read_manifest
from app.modules.institutions.models import (
    Institution,
    InstitutionEvidence,
    InstitutionRelationship,
)
from app.modules.sources.models import Source
from tests.integration.test_postgresql_guards import migrate

pytestmark = pytest.mark.integration


def test_official_inventory_is_idempotent_on_postgresql(postgres_url: str) -> None:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with Session(engine) as db:
        manifest = read_manifest()
        slugs = [item["slug"] for item in manifest["institutions"]]
        source_urls = [item["url"] for item in manifest["sources"].values()]
        first = load_inventory(db)
        second = load_inventory(db)
        assert first.created + first.unchanged == 25
        assert second.unchanged == 25
        assert (
            db.scalar(
                select(func.count()).select_from(Institution).where(Institution.slug.in_(slugs))
            )
            == 25
        )
        assert (
            db.scalar(select(func.count()).select_from(Source).where(Source.url.in_(source_urls)))
            == 2
        )
        manifest_evidence = select(Evidence.id).where(
            Evidence.metadata_["manifest_version"].as_string() == manifest["version"]
        )
        assert db.scalar(select(func.count()).select_from(manifest_evidence.subquery())) == 25
        assert (
            db.scalar(
                select(func.count())
                .select_from(InstitutionEvidence)
                .where(InstitutionEvidence.evidence_id.in_(manifest_evidence))
            )
            == 25
        )
        assert db.scalar(
            select(func.count()).select_from(Evidence).where(Evidence.id.in_(manifest_evidence))
        ) == db.scalar(
            select(func.count(Evidence.content_hash.distinct())).where(
                Evidence.id.in_(manifest_evidence)
            )
        )
        assert (
            db.scalar(
                select(func.count())
                .select_from(InstitutionRelationship)
                .join(Evidence, Evidence.id == InstitutionRelationship.evidence_id)
                .where(Evidence.metadata_["manifest_version"].as_string() == manifest["version"])
            )
            == 0
        )
