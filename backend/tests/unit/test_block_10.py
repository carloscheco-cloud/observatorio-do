import uuid
from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.risk_engine.engine import (
    DeduplicationService,
    FindingCandidate,
    RiskScoreCalculator,
    structured_explanation,
)
from app.modules.risk_engine.schemas import RuleCreate
from app.modules.risk_engine.seed import CATEGORIES, DOMAINS, RULES


def candidate(**changes: object) -> FindingCandidate:
    values: dict[str, object] = {
        "rule_id": uuid.UUID(int=1),
        "risk_type_id": uuid.UUID(int=2),
        "domain": "cross_domain",
        "entity_type": "institution",
        "entity_id": uuid.UUID(int=3),
        "title": "Observable difference",
        "observed_value": {"amount": 10},
        "public_explanation": "Observable signal requiring review.",
        "internal_explanation": "Compared structured values.",
        "severity": "review_required",
        "confidence_level": "deterministic",
    }
    values.update(changes)
    return FindingCandidate(**values)  # type: ignore[arg-type]


def test_taxonomy_contains_required_values() -> None:
    assert {"payroll", "procurement", "cross_domain", "data_quality"} <= set(DOMAINS)
    assert {"missing_information", "duplication", "concentration"} <= set(CATEGORIES)


def test_initial_rules_cover_every_domain_family() -> None:
    assert sum(len(codes) for codes in RULES.values()) >= 60
    assert "payroll_without_active_employment" in RULES["cross_domain"]
    assert "payment_above_contract" in RULES["procurement"]


def test_deduplication_is_stable_and_observed_value_sensitive() -> None:
    first = DeduplicationService.fingerprint(candidate())
    assert first == DeduplicationService.fingerprint(candidate())
    assert first != DeduplicationService.fingerprint(candidate(observed_value={"amount": 11}))


def test_score_separates_missing_data_from_substantive_risk() -> None:
    calculator = RiskScoreCalculator()
    assert calculator.calculate(["critical_data_quality"], 1) == (
        Decimal("0"),
        "insufficient_data",
    )
    score, band = calculator.calculate(["high_priority", "unusual"], 0)
    assert score == Decimal("40")
    assert band == "elevated"


def test_explanation_contains_limits_and_reproducible_parts() -> None:
    text = structured_explanation(
        observation="10",
        rule="monthly growth",
        threshold="5",
        comparison="previous month",
        difference="5",
        period="2099-01",
        evidence="controlled evidence",
    )
    assert "Umbral: 5" in text
    assert "Evidencia: controlled evidence" in text
    assert "no permite concluir fraude" in text


def test_template_injection_is_rejected() -> None:
    with pytest.raises(ValidationError):
        RuleCreate(
            stable_code="test.rule",
            name="Test",
            description="Test",
            domain="data_quality",
            risk_type_id=uuid.uuid4(),
            rule_type="deterministic",
            severity="review_required",
            public_message_template="{{ unsafe }}",
            internal_message_template="safe {value}",
            valid_from=date(2099, 1, 1),
        )


def test_candidate_defaults_are_safe() -> None:
    item = candidate()
    assert item.evidence_ids == ()
    assert item.metadata == {}
