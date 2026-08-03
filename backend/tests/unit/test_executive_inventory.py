import json
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.evidence.models import Evidence
from app.modules.executive_inventory.loader import (
    InvalidManifest,
    load_inventory,
    read_manifest,
    validate_manifest,
)
from app.modules.institutions.models import (
    Institution,
    InstitutionEvidence,
    InstitutionRelationship,
)
from app.modules.sources.models import Source
from app.modules.territories.models import Territory


def test_manifest_is_valid_traceable_and_has_unique_slugs() -> None:
    manifest = read_manifest()
    assert len(manifest["institutions"]) == 25
    assert len({item["slug"] for item in manifest["institutions"]}) == 25
    assert all(source["url"].startswith("https://") for source in manifest["sources"].values())
    assert all(source["source_type"] for source in manifest["sources"].values())
    assert set(manifest["sources"]) == {"constitution", "coedom"}
    ministry_locators = [
        item["locator"]
        for item in manifest["institutions"]
        if item.get("source", manifest["default_institution_source"]) == "coedom"
    ]
    assert len(ministry_locators) == 23
    assert len(set(ministry_locators)) == 23
    assert all("/COEDOM/Home/Details/" in locator for locator in ministry_locators)
    assert all(
        len(item.get("functions_summary") or item.get("sector", "")) < 200
        for item in manifest["institutions"]
    )


def test_manifest_rejects_missing_evidence_and_invalid_relationship() -> None:
    manifest = read_manifest()
    manifest["institutions"][0].pop("excerpt")
    with pytest.raises(InvalidManifest, match="missing evidence"):
        validate_manifest(manifest)
    manifest = read_manifest()
    manifest["relationships"] = [{"parent": "missing", "child": "ministerio-de-turismo"}]
    with pytest.raises(InvalidManifest, match="unknown institution"):
        validate_manifest(manifest)
    manifest = read_manifest()
    manifest["institutions"][2].pop("locator")
    with pytest.raises(InvalidManifest, match="individual COEDOM locator"):
        validate_manifest(manifest)


def test_load_is_idempotent_and_dry_run_does_not_persist(db: Session) -> None:
    preview = load_inventory(db, dry_run=True)
    assert preview.created == 25
    assert db.scalar(select(func.count()).select_from(Institution)) == 0
    first = load_inventory(db)
    second = load_inventory(db)
    assert first.created == 25
    assert second.unchanged == 25
    assert second.created == second.updated == second.errors == 0
    assert db.scalar(select(func.count()).select_from(Institution)) == 25
    assert db.scalar(select(func.count()).select_from(Source)) == 2
    assert db.scalar(select(func.count()).select_from(Evidence)) == 25
    assert db.scalar(select(func.count()).select_from(InstitutionEvidence)) == 25
    assert db.scalar(select(func.count()).select_from(InstitutionRelationship)) == 0
    assert db.scalar(select(func.count(Evidence.content_hash.distinct()))) == 25


def test_existing_divergence_is_skipped_without_orphan_evidence(db: Session) -> None:
    load_inventory(db)
    institution = db.scalar(select(Institution).where(Institution.slug == "ministerio-de-turismo"))
    assert institution is not None
    institution.official_website = "https://example.invalid/"
    db.commit()
    before = db.scalar(select(func.count()).select_from(Evidence))
    result = load_inventory(db)
    assert result.skipped == 1
    assert result.unchanged == 24
    assert db.scalar(select(func.count()).select_from(Evidence)) == before


def test_load_rolls_back_atomically_on_database_error(db: Session, tmp_path: Path) -> None:
    manifest = read_manifest()
    manifest["institutions"][1]["name"] = manifest["institutions"][0]["name"]
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(IntegrityError):
        load_inventory(db, path=path)
    assert db.scalar(select(func.count()).select_from(Territory)) == 0
    assert db.scalar(select(func.count()).select_from(Source)) == 0
    assert db.scalar(select(func.count()).select_from(Evidence)) == 0
    assert db.scalar(select(func.count()).select_from(Institution)) == 0
