import json
from decimal import Decimal
from pathlib import Path

import pytest

from app.modules.digital_transparency.methodology_v1_1 import RULE_BY_CODE
from app.modules.digital_transparency.pe06d import EXPECTED_DIMENSIONS, read_manifest

EXPECTED = {
    "ministerio-de-administracion-publica": (9, 3, 10, 8, 5),
    "ministerio-de-hacienda-y-economia": (12, 15, 8, 10, 5),
    "ministerio-de-educacion": (12, 9, 6, 10, 5),
    "ministerio-de-salud-publica-y-asistencia-social": (6, 3, 4, 10, 4),
    "ministerio-de-medio-ambiente-y-recursos-naturales": (12, 15, 10, 8, 5),
}
ORDER = (
    "legal_framework",
    "organizational_structure",
    "official_contact_information",
    "document_searchability",
    "stable_links",
)


def test_manifest_has_five_explicit_representative_selections() -> None:
    data = read_manifest()
    assert len(data["institutions"]) == 5
    for institution in data["institutions"]:
        selections = institution["dimensions"]
        assert tuple(item["dimension"] for item in selections) == ORDER
        assert len({item["dimension"] for item in selections}) == 5
        assert all(item["calculation_reason"] and item["limitations"] for item in selections)
        assert all(item["contradictions"] for item in selections)


@pytest.mark.parametrize("slug", EXPECTED)
def test_five_institution_rule_codes_and_scores_are_discrete(slug: str) -> None:
    institution = next(item for item in read_manifest()["institutions"] if item["slug"] == slug)
    scores = tuple(
        int(RULE_BY_CODE[item["rule_code"]].awarded_score) for item in institution["dimensions"]
    )
    assert scores == EXPECTED[slug]
    assert (
        sum(
            (RULE_BY_CODE[item["rule_code"]].maximum_score for item in institution["dimensions"]),
            Decimal(),
        )
        == 55
    )


def test_mispas_redirect_loop_is_reconciled_and_never_zero() -> None:
    institution = next(item for item in read_manifest()["institutions"] if "salud" in item["slug"])
    stable = next(item for item in institution["dimensions"] if item["dimension"] == "stable_links")
    assert stable["rule_code"] == "TD11-STABLE_LINKS-04"
    assert "technical_error" in stable["calculation_reason"]
    assert "recursos distintos" in stable["contradictions"]


def test_manifest_rejects_invalid_rule_and_incomplete_traceability(tmp_path: Path) -> None:
    data = read_manifest()
    data["institutions"][0]["dimensions"][0]["rule_code"] = "TD11-LEGAL_FRAMEWORK-11"
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="rule_code"):
        read_manifest(path)
    data = read_manifest()
    data["institutions"][0]["dimensions"][0]["limitations"] = ""
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="traceability"):
        read_manifest(path)


def test_expected_accumulated_dimensions_are_exactly_eight() -> None:
    assert len(EXPECTED_DIMENSIONS) == 8
