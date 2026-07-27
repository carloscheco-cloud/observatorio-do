import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class EvaluationContext:
    run_id: uuid.UUID
    as_of: date
    domain: str | None = None
    institution_id: uuid.UUID | None = None
    period_start: date | None = None
    period_end: date | None = None
    dry_run: bool = False
    batch_size: int = 500


@dataclass(frozen=True)
class FindingCandidate:
    rule_id: uuid.UUID
    risk_type_id: uuid.UUID
    domain: str
    entity_type: str
    entity_id: uuid.UUID
    title: str
    observed_value: dict[str, object]
    public_explanation: str
    internal_explanation: str
    severity: str
    confidence_level: str
    institution_id: uuid.UUID | None = None
    comparison_value: dict[str, object] | None = None
    threshold_value: dict[str, object] | None = None
    evidence_ids: tuple[uuid.UUID, ...] = ()
    evidence_links: tuple[tuple[uuid.UUID, uuid.UUID, str], ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class RuleResult:
    candidates: tuple[FindingCandidate, ...] = ()
    records_evaluated: int = 0
    errors: tuple[str, ...] = ()


class RuleEvaluator(Protocol):
    def evaluate(self, context: EvaluationContext) -> RuleResult: ...


class FindingPersister(Protocol):
    def persist(self, candidate: FindingCandidate, context: EvaluationContext) -> object: ...


class DeduplicationService:
    @staticmethod
    def fingerprint(candidate: FindingCandidate) -> str:
        payload = {
            "rule": str(candidate.rule_id),
            "entity_type": candidate.entity_type,
            "entity": str(candidate.entity_id),
            "institution": str(candidate.institution_id) if candidate.institution_id else None,
            "observed": candidate.observed_value,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(encoded.encode()).hexdigest()


class RiskScoreCalculator:
    WEIGHTS = {
        "informational": Decimal("2"),
        "review_required": Decimal("8"),
        "unusual": Decimal("15"),
        "high_priority": Decimal("25"),
        "critical_data_quality": Decimal("0"),
    }

    def calculate(self, severities: list[str], data_quality_count: int) -> tuple[Decimal, str]:
        substantive = sum((self.WEIGHTS.get(item, Decimal("0")) for item in severities), Decimal())
        score = min(Decimal("100"), substantive)
        if not severities or data_quality_count == len(severities):
            return Decimal("0"), "insufficient_data"
        if score < 10:
            band = "low"
        elif score < 30:
            band = "moderate"
        elif score < 60:
            band = "elevated"
        else:
            band = "high_review_priority"
        return score, band


def structured_explanation(
    *,
    observation: str,
    rule: str,
    threshold: str,
    comparison: str,
    difference: str,
    period: str,
    evidence: str,
) -> str:
    return (
        f"Se observó: {observation}. Regla aplicada: {rule}. Umbral: {threshold}. "
        f"Comparación: {comparison}. Diferencia: {difference}. Período: {period}. "
        f"Evidencia: {evidence}. Requiere revisión humana. Esta señal por sí sola no permite "
        "concluir fraude, corrupción, ilegalidad, culpabilidad ni intención."
    )
