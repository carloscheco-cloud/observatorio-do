from dataclasses import asdict, dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.institutions.models import (
    CoverageLevel,
    Institution,
    InstitutionStatus,
    StateBranch,
)

MISSION = (
    "Maximizar continuamente la cobertura publica verificable del Estado dominicano, "
    "priorizando Poder Ejecutivo, Poder Legislativo y Poder Judicial. Publicar cobertura "
    "basica util tan pronto exista una fuente trazable y mejorarla iterativamente."
)

BRANCH_PRIORITY = (
    StateBranch.EXECUTIVE,
    StateBranch.LEGISLATIVE,
    StateBranch.JUDICIAL,
)

BASIC_OR_BETTER = {
    CoverageLevel.BASIC,
    CoverageLevel.PARTIAL,
    CoverageLevel.SUBSTANTIAL,
    CoverageLevel.COMPLETE,
}
SUBSTANTIAL_OR_BETTER = {CoverageLevel.SUBSTANTIAL, CoverageLevel.COMPLETE}


@dataclass(frozen=True)
class BranchCoverage:
    branch: str
    institutions: int
    basic_or_better: int
    substantial_or_better: int
    basic_ratio: float
    substantial_ratio: float

    def to_dict(self) -> dict[str, str | int | float]:
        return asdict(self)


def coverage_by_branch(db: Session) -> dict[StateBranch, BranchCoverage]:
    institutions = list(
        db.scalars(select(Institution).where(Institution.status == InstitutionStatus.CONFIRMED))
    )
    result: dict[StateBranch, BranchCoverage] = {}
    for branch in BRANCH_PRIORITY:
        rows = [row for row in institutions if row.state_branch == branch]
        total = len(rows)
        basic = sum(row.coverage_level in BASIC_OR_BETTER for row in rows)
        substantial = sum(row.coverage_level in SUBSTANTIAL_OR_BETTER for row in rows)
        result[branch] = BranchCoverage(
            branch=branch.value,
            institutions=total,
            basic_or_better=basic,
            substantial_or_better=substantial,
            basic_ratio=(basic / total) if total else 0.0,
            substantial_ratio=(substantial / total) if total else 0.0,
        )
    return result


def choose_next_focus(
    report: dict[StateBranch, BranchCoverage], target: float | None = None
) -> StateBranch:
    threshold = target if target is not None else settings.autonomy_target_basic_coverage
    for branch in BRANCH_PRIORITY:
        coverage = report[branch]
        if coverage.institutions == 0 or coverage.basic_ratio < threshold:
            return branch
    return min(BRANCH_PRIORITY, key=lambda branch: report[branch].substantial_ratio)


def status_payload(db: Session) -> dict[str, Any]:
    report = coverage_by_branch(db)
    focus = choose_next_focus(report)
    return {
        "mission": MISSION,
        "autonomy_enabled": settings.autonomy_mode_enabled,
        "target_basic_coverage": settings.autonomy_target_basic_coverage,
        "next_focus": focus.value,
        "branches": {branch.value: report[branch].to_dict() for branch in BRANCH_PRIORITY},
        "operating_rule": (
            "Primero cobertura basica visible; luego profundidad y auditoria continua."
        ),
    }
