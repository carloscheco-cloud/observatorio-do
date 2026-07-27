import pytest
from sqlalchemy.orm import Session

from app.modules.evidence.models import Evidence
from app.modules.institutions.models import InstitutionStatus
from app.modules.institutions.schemas import InstitutionCreate
from app.modules.institutions.service import create_institution, evidence_ids
from app.modules.sources.models import Source
from app.modules.territories.models import Territory, TerritoryType


def prerequisites(db: Session) -> tuple[Territory, Evidence]:
    territory = Territory(name="Bonao", code="DO-2801", type=TerritoryType.MUNICIPALITY)
    source = Source(
        name="Fuente oficial",
        url="https://example.gob.do",
        publisher="Gobierno",
        is_official=True,
    )
    evidence = Evidence(
        source=source,
        title="Directorio",
        excerpt="Ayuntamiento de Bonao",
        locator="https://example.gob.do/directorio",
        content_hash="a" * 64,
    )
    db.add_all([territory, evidence])
    db.commit()
    return territory, evidence


def test_create_institution_always_links_evidence(db: Session) -> None:
    territory, evidence = prerequisites(db)
    item = create_institution(
        db,
        InstitutionCreate(
            name="Ayuntamiento Municipal de Bonao",
            kind="municipal_government",
            territory_id=territory.id,
            evidence_id=evidence.id,
        ),
    )
    assert item.status is InstitutionStatus.CONFIRMED
    assert evidence_ids(db, item.id) == [evidence.id]


def test_ai_cannot_write_canonical_institution(db: Session) -> None:
    territory, evidence = prerequisites(db)
    with pytest.raises(PermissionError):
        create_institution(
            db,
            InstitutionCreate(
                name="No permitida",
                kind="municipal_government",
                territory_id=territory.id,
                evidence_id=evidence.id,
            ),
            actor_type="ai",
        )
