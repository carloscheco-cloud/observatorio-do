from dataclasses import dataclass
from decimal import Decimal

VERSION = "OED-TD-1.0"
PARTIAL_COVERAGE_THRESHOLD = Decimal("60")
COMPLETE_COVERAGE_THRESHOLD = Decimal("90")
PARTIAL_CLASSIFICATION = "evaluación parcial"

WEIGHTS = {
    "institutional_identity": Decimal("10"),
    "legal_framework": Decimal("15"),
    "organizational_structure": Decimal("15"),
    "current_authorities": Decimal("15"),
    "appointment_acts": Decimal("20"),
    "official_contact_information": Decimal("10"),
    "document_searchability": Decimal("10"),
    "stable_links": Decimal("5"),
}


@dataclass(frozen=True)
class ComponentInput:
    code: str
    score: Decimal
    applicable: bool = True


@dataclass(frozen=True)
class ScoreResult:
    raw_score: Decimal
    maximum_score: Decimal
    normalized_score: Decimal


def calculate(components: list[ComponentInput]) -> ScoreResult:
    if not components:
        raise ValueError("a score requires components")
    unknown = {item.code for item in components} - WEIGHTS.keys()
    if unknown or len({item.code for item in components}) != len(components):
        raise ValueError("components must be unique known dimensions")
    raw = Decimal("0")
    maximum = Decimal("0")
    for item in components:
        weight = WEIGHTS[item.code]
        if item.score < 0 or item.score > weight:
            raise ValueError(f"score outside dimension range: {item.code}")
        if item.applicable:
            raw += item.score
            maximum += weight
    if maximum == 0:
        raise ValueError("at least one dimension must be applicable")
    normalized = (raw * Decimal("100") / maximum).quantize(Decimal("0.001"))
    return ScoreResult(raw, maximum, normalized)


def appointment_act_score(
    *,
    act_located: bool,
    downloadable: bool = False,
    searchable: bool = False,
    has_metadata: bool = False,
    appointment_verified: bool = False,
    authority_verified: bool = False,
) -> Decimal:
    if act_located:
        return Decimal("20") if downloadable and searchable and has_metadata else Decimal("16")
    if appointment_verified:
        return Decimal("12")
    if authority_verified:
        return Decimal("6")
    return Decimal("0")


def classification(score: Decimal) -> str:
    if score < 0 or score > 100:
        raise ValueError("normalized score must be between 0 and 100")
    if score >= 90:
        return "disponibilidad digital avanzada"
    if score >= 75:
        return "disponibilidad digital alta"
    if score >= 60:
        return "disponibilidad digital intermedia"
    if score >= 40:
        return "disponibilidad digital limitada"
    return "disponibilidad digital muy limitada"


def maturity(coverage: Decimal) -> str:
    if coverage < 0 or coverage > 100:
        raise ValueError("coverage must be between 0 and 100")
    if coverage < PARTIAL_COVERAGE_THRESHOLD:
        return "partial"
    if coverage < COMPLETE_COVERAGE_THRESHOLD:
        return "provisional"
    return "complete"


def public_classification(normalized_score: Decimal, coverage: Decimal) -> str:
    return (
        PARTIAL_CLASSIFICATION
        if maturity(coverage) == "partial"
        else classification(normalized_score)
    )


assert sum(WEIGHTS.values()) == Decimal("100")
