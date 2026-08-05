# ruff: noqa: E501
from decimal import Decimal

import pytest

from app.modules.digital_transparency.methodology import VERSION as HISTORICAL_VERSION
from app.modules.digital_transparency.methodology import WEIGHTS
from app.modules.digital_transparency.methodology_v1_1 import (
    RULES,
    SCALES,
    VERSION,
    EvaluatedComponent,
    calculate_components,
    consolidate_representative,
    evaluate_rule,
)


def component(
    dimension: str, score: int, reason: str = "Evidencia verificada"
) -> EvaluatedComponent:
    return EvaluatedComponent(
        dimension,
        f"TD11-{dimension.upper()}-{score:02d}",
        "evaluated",
        f"obs-{score}",
        f"ev-{score}",
        reason,
    )


def test_versions_weights_unique_rules_and_discrete_scores() -> None:
    assert HISTORICAL_VERSION == "OED-TD-1.0"
    assert VERSION == "OED-TD-1.1"
    assert sum(WEIGHTS.values()) == Decimal(100)
    keys = {(rule.methodology_version, rule.dimension, rule.rule_code) for rule in RULES}
    assert len(keys) == len(RULES) == 30
    for dimension, scores in SCALES.items():
        assert {int(rule.awarded_score) for rule in RULES if rule.dimension == dimension} == set(
            scores
        )


@pytest.mark.parametrize(
    ("dimension", "scores"),
    [
        ("legal_framework", [15, 9, 3]),
        ("organizational_structure", [15, 12, 9, 3]),
        ("official_contact_information", [10, 6, 4]),
        ("document_searchability", [10, 4]),
        ("stable_links", [5, 4, 2, 0]),
    ],
)
def test_requested_scale_levels_are_allowed(dimension: str, scores: list[int]) -> None:
    assert [evaluate_rule(component(dimension, score)).awarded_score for score in scores] == scores


def test_unlisted_score_pending_and_not_applicable() -> None:
    with pytest.raises(ValueError, match="unknown"):
        evaluate_rule(component("stable_links", 6))
    pending = EvaluatedComponent(
        "stable_links", None, "pending_evaluation", None, None, "insuficiente"
    )
    assert evaluate_rule(pending) is None
    with pytest.raises(ValueError, match="pending_evaluation"):
        evaluate_rule(
            EvaluatedComponent(
                "stable_links", "TD11-STABLE_LINKS-00", "pending_evaluation", "obs", "ev", "x"
            )
        )
    na = EvaluatedComponent("stable_links", None, "not_applicable", None, None, "fuera de alcance")
    result = calculate_components([component("legal_framework", 12), na])
    assert result.raw_score == 12 and result.maximum_score == 15 and result.normalized_score == 80


def test_multiple_resources_require_explicit_selection_and_contradiction_reason() -> None:
    good = component("stable_links", 5)
    broken = component("stable_links", 0)
    with pytest.raises(ValueError, match="reconciliation"):
        consolidate_representative("stable_links", [good, broken], good.observation_id or "")
    explained = component(
        "stable_links", 5, "Contradictory checks reconciled: current representative is latest"
    )
    assert (
        consolidate_representative(
            "stable_links", [explained, broken], explained.observation_id or ""
        )
        == explained
    )


def test_ranking_is_not_part_of_methodology_result() -> None:
    result = calculate_components([component("stable_links", 5)])
    assert not hasattr(result, "rank")
