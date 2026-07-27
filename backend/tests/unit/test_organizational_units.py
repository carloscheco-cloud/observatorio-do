from datetime import date

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.seed import seed
from app.modules.evidence.models import Evidence
from app.modules.institutions.models import Institution
from app.modules.legal_basis.models import LegalBasis
from app.modules.organizational_units.models import (
    OrganizationalEvent,
    OrganizationalUnit,
    UnitStatus,
    UnitType,
)
from app.modules.organizational_units.schemas import OrganizationalUnitCreate
from app.modules.organizational_units.service import (
    InvalidOrganizationalUnit,
    ancestors,
    create_unit,
    descendants,
    organizational_chart,
    path,
)
from app.modules.positions.models import Position
from app.modules.sources.models import Source


def _payload(db: Session, **changes: object) -> OrganizationalUnitCreate:
    seed(db)
    institution = db.scalar(select(Institution))
    legal = db.scalar(select(LegalBasis).where(LegalBasis.reference == "CONTROL-B4-LEGAL-001"))
    source = db.scalar(
        select(Source).where(Source.url == "controlled://block-4/organizational-structure")
    )
    evidence = db.scalar(
        select(Evidence).where(Evidence.source_id == source.id)  # type: ignore[union-attr]
    )
    assert institution and legal and source and evidence
    values: dict[str, object] = {
        "institution_id": institution.id,
        "official_name": "Unidad Nueva Ficticia",
        "normalized_name": "unidad nueva ficticia",
        "stable_code": "CONTROL-B4-NEW",
        "unit_type": UnitType.UNIT,
        "hierarchy_level": 0,
        "status": UnitStatus.CANONICAL,
        "valid_from": date(2026, 1, 1),
        "legal_basis_id": legal.id,
        "evidence_id": evidence.id,
        "source_id": source.id,
        "metadata_": {"controlled": True},
    }
    values.update(changes)
    return OrganizationalUnitCreate(**values)  # type: ignore[arg-type]


def test_valid_creation_and_ai_rejection(db: Session) -> None:
    payload = _payload(db)
    item = create_unit(db, payload)
    assert item.stable_code == "CONTROL-B4-NEW"
    with pytest.raises(PermissionError):
        create_unit(
            db, payload.model_copy(update={"stable_code": "CONTROL-B4-AI"}), actor_type="ai"
        )


def test_canonical_unit_requires_legal_basis_and_traceability(db: Session) -> None:
    with pytest.raises(ValidationError, match="legal_basis_id"):
        _payload(db, legal_basis_id=None)


def test_parent_must_have_same_institution_and_lower_level(db: Session) -> None:
    payload = _payload(db)
    institution = db.get(Institution, payload.institution_id)
    assert institution is not None
    other = Institution(
        name="Institución Ficticia Alterna",
        kind="test",
        territory_id=institution.territory_id,
    )
    db.add(other)
    db.flush()
    parent = OrganizationalUnit(
        institution_id=other.id,
        official_name="Raíz alterna",
        normalized_name="raiz alterna",
        stable_code="ALT-ROOT",
        unit_type=UnitType.OTHER,
        hierarchy_level=0,
        status=UnitStatus.DRAFT,
        valid_from=date(2025, 1, 1),
    )
    db.add(parent)
    db.commit()
    with pytest.raises(InvalidOrganizationalUnit, match="same institution"):
        create_unit(
            db,
            payload.model_copy(
                update={"stable_code": "CONTROL-B4-CROSS", "parent_unit_id": parent.id}
            ),
        )


def test_tree_queries_and_chart_as_of(db: Session) -> None:
    seed(db)
    division = db.scalar(
        select(OrganizationalUnit).where(OrganizationalUnit.stable_code == "CONTROL-B4-DIV-NOM")
    )
    institution = db.scalar(select(Institution))
    assert division and institution
    assert [item.stable_code for item in ancestors(db, division.id)] == [
        "CONTROL-B4-ROOT",
        "CONTROL-B4-DIR-ADM",
        "CONTROL-B4-DEP-RRHH",
    ]
    assert path(db, division.id)[-1] == division
    root = ancestors(db, division.id)[0]
    assert division in descendants(db, root.id)
    assert organizational_chart(db, institution.id, as_of=date(2024, 12, 31)) == []
    assert len(organizational_chart(db, institution.id, as_of=date(2025, 1, 1))) == 1


def test_seed_preserves_event_and_position_unit_history(db: Session) -> None:
    seed(db)
    seed(db)
    assert len(list(db.scalars(select(OrganizationalEvent)))) == 1
    position = db.scalar(select(Position).where(Position.code == "CONTROL-B4-DIRECTOR-ADM"))
    assert position is not None
    assert position.organizational_unit_id is not None
