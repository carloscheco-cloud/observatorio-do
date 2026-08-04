import copy
import json
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.evidence.models import Evidence
from app.modules.executive_dependencies.loader import (
    InvalidManifest,
    load_dependencies,
    read_manifest,
    rollback_dependencies,
    validate_manifest,
)
from app.modules.executive_dependencies.models import ExecutiveDependencyLoadRecord
from app.modules.executive_inventory.loader import load_inventory
from app.modules.institutions.models import Institution, InstitutionRelationship
from app.modules.sources.models import Source


def test_manifest_has_separated_traceability_and_unique_slugs() -> None:
    manifest = read_manifest()
    assert set(manifest) >= {
        "sources",
        "institutions",
        "institution_evidence",
        "relationships",
        "relationship_evidence",
    }
    assert len({item["slug"] for item in manifest["institutions"]}) == 2
    assert len(manifest["institution_evidence"]) == len(manifest["institutions"])
    assert len(manifest["relationship_evidence"]) == len(manifest["relationships"])


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda data: data["sources"].pop("map_inap"), "known source"),
        (lambda data: data["institution_evidence"].pop(), "individual evidence"),
        (
            lambda data: data["institutions"].append(copy.deepcopy(data["institutions"][0])),
            "unique",
        ),
        (lambda data: data["relationship_evidence"].pop(), "specific evidence"),
        (
            lambda data: data["relationships"].append(copy.deepcopy(data["relationships"][0])),
            "duplicate",
        ),
    ],
)
def test_manifest_rejects_invalid_traceability(mutation: object, message: str) -> None:
    manifest = read_manifest()
    assert callable(mutation)
    mutation(manifest)
    with pytest.raises(InvalidManifest, match=message):
        validate_manifest(manifest)


def test_manifest_rejects_self_relation_bad_dates_and_missing_unknown_date_note() -> None:
    manifest = read_manifest()
    manifest["relationships"][0]["parent"] = manifest["relationships"][0]["child"]
    with pytest.raises(InvalidManifest, match="self"):
        validate_manifest(manifest)
    manifest = read_manifest()
    manifest["relationships"][1]["valid_from"] = "2016-07-05"
    manifest["relationships"][1]["valid_to"] = "2010-01-01"
    with pytest.raises(InvalidManifest, match="valid_to"):
        validate_manifest(manifest)
    manifest = read_manifest()
    manifest["relationships"][0]["notes"] = ""
    with pytest.raises(InvalidManifest, match="explicit note"):
        validate_manifest(manifest)


def test_load_is_atomic_idempotent_and_dry_run_does_not_persist(db: Session) -> None:
    load_inventory(db)
    baseline = db.scalar(select(func.count()).select_from(Institution))
    preview = load_dependencies(db, dry_run=True)
    assert preview.created == 4
    assert db.scalar(select(func.count()).select_from(Institution)) == baseline
    first = load_dependencies(db)
    counts = (
        db.scalar(select(func.count()).select_from(Institution)),
        db.scalar(select(func.count()).select_from(Source)),
        db.scalar(select(func.count()).select_from(Evidence)),
        db.scalar(select(func.count()).select_from(InstitutionRelationship)),
    )
    second = load_dependencies(db)
    assert first.created == 4
    assert second.unchanged == 4
    assert second.created == second.updated == second.skipped == second.errors == 0
    assert counts == (
        db.scalar(select(func.count()).select_from(Institution)),
        db.scalar(select(func.count()).select_from(Source)),
        db.scalar(select(func.count()).select_from(Evidence)),
        db.scalar(select(func.count()).select_from(InstitutionRelationship)),
    )


def test_confirmed_divergence_is_skipped_without_new_relationship(db: Session) -> None:
    load_inventory(db)
    load_dependencies(db)
    institution = db.scalar(
        select(Institution).where(
            Institution.slug == "instituto-nacional-de-administracion-publica"
        )
    )
    assert institution is not None
    institution.kind = "divergent"
    db.commit()
    result = load_dependencies(db)
    assert result.skipped >= 1


def test_rollback_is_idempotent_and_dry_run_preserves_pe02(db: Session) -> None:
    load_inventory(db)
    pe02_institutions = db.scalar(select(func.count()).select_from(Institution))
    load_dependencies(db)
    ownership = db.scalar(select(func.count()).select_from(ExecutiveDependencyLoadRecord))
    assert ownership == 14
    preview = rollback_dependencies(db, dry_run=True)
    assert preview.removed == 14
    assert db.scalar(select(func.count()).select_from(ExecutiveDependencyLoadRecord)) == 14
    actual = rollback_dependencies(db)
    assert actual.removed == 14
    assert db.scalar(select(func.count()).select_from(Institution)) == pe02_institutions
    assert db.scalar(select(func.count()).select_from(InstitutionRelationship)) == 0
    again = rollback_dependencies(db)
    assert again.unchanged == 1


def test_fatal_error_rolls_back_sources_evidence_and_institutions(
    db: Session, tmp_path: Path
) -> None:
    load_inventory(db)
    manifest = read_manifest()
    manifest["relationships"][1]["parent"] = "institucion-ausente"
    manifest["relationship_evidence"][1]["parent"] = "institucion-ausente"
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    before = db.scalar(select(func.count()).select_from(Source))
    with pytest.raises(InvalidManifest, match="parent institution"):
        load_dependencies(db, path=path)
    assert db.scalar(select(func.count()).select_from(Source)) == before
    assert (
        db.scalar(
            select(func.count())
            .select_from(Institution)
            .where(Institution.slug == "instituto-nacional-de-administracion-publica")
        )
        == 0
    )
