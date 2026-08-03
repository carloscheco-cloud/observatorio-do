import uuid

import pytest
from pydantic import ValidationError

from app.modules.institutions.models import (
    CoverageLevel,
    InstitutionType,
    OperationalStatus,
    StateBranch,
)
from app.modules.institutions.schemas import InstitutionCreate


def valid_payload() -> dict[str, object]:
    return {
        "name": "Ministerio de Ejemplo",
        "kind": "ministerio",
        "territory_id": uuid.uuid4(),
        "evidence_id": uuid.uuid4(),
        "acronym": "ME",
        "slug": "ministerio-de-ejemplo",
        "state_branch": StateBranch.EXECUTIVE,
        "institution_type": InstitutionType.MINISTRY,
        "operational_status": OperationalStatus.ACTIVE,
        "coverage_level": CoverageLevel.BASIC,
        "official_website": "https://example.gob.do",
    }


def test_accepts_executive_institution_fields() -> None:
    payload = InstitutionCreate.model_validate(valid_payload())

    assert payload.state_branch is StateBranch.EXECUTIVE
    assert payload.institution_type is InstitutionType.MINISTRY
    assert payload.slug == "ministerio-de-ejemplo"


def test_rejects_non_canonical_slug() -> None:
    data = valid_payload()
    data["slug"] = "Ministerio de Ejemplo"

    with pytest.raises(ValidationError):
        InstitutionCreate.model_validate(data)


def test_legacy_payload_remains_compatible() -> None:
    payload = InstitutionCreate.model_validate(
        {
            "name": "Institución heredada",
            "kind": "otro",
            "territory_id": uuid.uuid4(),
            "evidence_id": uuid.uuid4(),
        }
    )

    assert payload.state_branch is None
    assert payload.institution_type is None
    assert payload.operational_status is OperationalStatus.UNKNOWN
    assert payload.coverage_level is CoverageLevel.NONE
