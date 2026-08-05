# ruff: noqa: E501
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from .methodology import WEIGHTS, ScoreResult, maturity

VERSION = "OED-TD-1.1"
SUPERSEDES_VERSION = "OED-TD-1.0"

SCALES: dict[str, tuple[int, ...]] = {
    "legal_framework": (0, 3, 6, 9, 12, 15),
    "organizational_structure": (0, 3, 6, 9, 12, 15),
    "official_contact_information": (0, 2, 4, 6, 8, 10),
    "document_searchability": (0, 2, 4, 6, 8, 10),
    "stable_links": (0, 1, 2, 3, 4, 5),
}

RULE_DESCRIPTIONS: dict[str, tuple[str, ...]] = {
    "legal_framework": (
        "revisión completa documentada sin marco legal oficial localizable",
        "base legal mencionada sin documento oficial verificable",
        "referencias oficiales dispersas; solo parte del marco es verificable",
        "marco oficial parcial o con documentos/metadatos/enlaces incompletos",
        "sección oficial y normas principales accesibles con una carencia menor",
        "sección oficial atribuida, norma principal identificable y cobertura suficiente con documentos, número, fecha y enlaces oficiales",
    ),
    "organizational_structure": (
        "búsqueda completa documentada sin estructura institucional oficial localizable",
        "estructura limitada o organigrama de una unidad interna; un directorio o menú no constituye estructura",
        "estructura textual oficial sin organigrama institucional completo",
        "estructura institucional sustancial u organigrama parcial/interactivo con limitaciones",
        "organigrama institucional oficial completo y legible sin fecha o versión verificable",
        "organigrama institucional oficial, inequívoco, fechado/versionado, legible, suficiente y descargable o navegable",
    ),
    "official_contact_information": (
        "revisión completa sin canal institucional oficial verificable",
        "un único canal institucional básico verificable",
        "contacto institucional parcial y OAI no localizada o incompleta",
        "contacto institucional suficiente y OAI parcialmente documentada",
        "dirección, teléfono, correo o canal general suficientes; OAI identificada con canal verificable",
        "contacto institucional y OAI completos, con canal SAIP o equivalente verificable, sin puntuar datos personales",
    ),
    "document_searchability": (
        "recurso oficial disponible pero técnicamente inutilizable para consulta",
        "recurso accesible con dificultades técnicas graves de interpretación",
        "documento legible pero no buscable o escaneado; no se aplicó OCR",
        "contenido parcialmente buscable o extracción limitada",
        "texto seleccionable con metadatos o navegación incompletos",
        "HTML o PDF con texto seleccionable, título/metadatos mínimos y localización clara",
    ),
    "stable_links": (
        "enlace roto confirmado conforme a PE-06A",
        "not_found_provisional con recurso alternativo o evidencia histórica",
        "acceso restringido, intermitente o error técnico no concluyente",
        "recurso disponible mediante URL poco estable, navegación indirecta o metadatos pobres",
        "recurso disponible con redirección oficial o carencia menor de metadatos",
        "URL directa o redirección oficial estable, 2xx, tipo correcto e identificación básica",
    ),
}


@dataclass(frozen=True)
class Rule:
    methodology_version: str
    dimension: str
    rule_code: str
    description: str
    conditions: dict[str, Any]
    awarded_score: Decimal
    maximum_score: Decimal
    public_explanation: str
    quality_level: str


def _code(dimension: str, score: int) -> str:
    return f"TD11-{dimension.upper()}-{score:02d}"


RULES = tuple(
    Rule(
        VERSION,
        dimension,
        _code(dimension, score),
        description,
        {
            "all_conditions_must_be_supported": True,
            "evidence_condition": description,
            "score": score,
            "temporary_error_is_absence": False,
        },
        Decimal(score),
        WEIGHTS[dimension],
        description.capitalize() + ".",
        {
            0: "none",
            1: "provisional",
            2: "very_limited",
            3: "limited",
            4: "limited",
            5: "complete",
            6: "limited",
            8: "substantial",
            9: "partial",
            10: "complete",
            12: "substantial",
            15: "complete",
        }[score],
    )
    for dimension, scores in SCALES.items()
    for score, description in zip(scores, RULE_DESCRIPTIONS[dimension], strict=True)
)
RULE_BY_CODE = {rule.rule_code: rule for rule in RULES}


@dataclass(frozen=True)
class EvaluatedComponent:
    dimension: str
    rule_code: str | None
    status: str
    observation_id: str | None
    evidence_id: str | None
    calculation_reason: str


def evaluate_rule(component: EvaluatedComponent) -> Rule | None:
    if component.status == "pending_evaluation":
        if component.rule_code is not None:
            raise ValueError("pending_evaluation cannot receive a scoring rule or zero")
        return None
    if component.status == "not_applicable":
        if component.rule_code is not None:
            raise ValueError("not_applicable cannot receive a scoring rule")
        return None
    if not component.observation_id or not component.evidence_id:
        raise ValueError("a scored component requires observation and evidence")
    rule = RULE_BY_CODE.get(component.rule_code or "")
    if rule is None or rule.dimension != component.dimension:
        raise ValueError("unknown or mismatched rule_code")
    if not component.calculation_reason.strip():
        raise ValueError("a scored component requires calculation_reason")
    return rule


def calculate_components(components: list[EvaluatedComponent]) -> ScoreResult:
    if not components:
        raise ValueError("a score requires components")
    if len({item.dimension for item in components}) != len(components):
        raise ValueError("select one representative observation per dimension")
    raw = Decimal()
    maximum = Decimal()
    for component in components:
        rule = evaluate_rule(component)
        if component.status == "not_applicable":
            continue
        if rule is not None:
            raw += rule.awarded_score
            maximum += rule.maximum_score
    if maximum == 0:
        raise ValueError("at least one dimension must be evaluated")
    normalized = (raw * Decimal(100) / maximum).quantize(Decimal("0.001"))
    return ScoreResult(raw, maximum, normalized)


def consolidate_representative(
    dimension: str, candidates: list[EvaluatedComponent], selected_observation_id: str
) -> EvaluatedComponent:
    """Require an explicit representative; complementary and contradictory resources remain auditable."""
    matches = [item for item in candidates if item.observation_id == selected_observation_id]
    if len(matches) != 1 or any(item.dimension != dimension for item in candidates):
        raise ValueError("representative observation must be explicit and belong to the dimension")
    selected = matches[0]
    scored = [evaluate_rule(item) for item in candidates]
    scores = {item.awarded_score for item in scored if item is not None}
    if len(scores) > 1 and "contradict" not in selected.calculation_reason.lower():
        raise ValueError("contradictory resources require an explicit reconciliation reason")
    return selected


def coverage_and_maturity(result: ScoreResult) -> tuple[Decimal, str]:
    coverage = result.maximum_score
    return coverage, maturity(coverage)


assert sum(WEIGHTS.values()) == Decimal(100)
assert len(RULE_BY_CODE) == len(RULES)
