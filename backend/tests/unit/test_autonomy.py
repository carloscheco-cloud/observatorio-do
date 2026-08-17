import pytest

from app.core import actors
from app.modules.autonomy.mission import BranchCoverage, choose_next_focus
from app.modules.institutions.models import StateBranch


def _coverage(branch: StateBranch, institutions: int, basic_ratio: float) -> BranchCoverage:
    basic = round(institutions * basic_ratio)
    return BranchCoverage(
        branch=branch.value,
        institutions=institutions,
        basic_or_better=basic,
        substantial_or_better=0,
        basic_ratio=basic_ratio,
        substantial_ratio=0.0,
    )


def test_director_bootstraps_branches_in_priority_order() -> None:
    report = {
        StateBranch.EXECUTIVE: _coverage(StateBranch.EXECUTIVE, 100, 0.90),
        StateBranch.LEGISLATIVE: _coverage(StateBranch.LEGISLATIVE, 0, 0.0),
        StateBranch.JUDICIAL: _coverage(StateBranch.JUDICIAL, 0, 0.0),
    }
    assert choose_next_focus(report, target=0.80) == StateBranch.LEGISLATIVE


def test_director_keeps_executive_until_basic_target() -> None:
    report = {
        StateBranch.EXECUTIVE: _coverage(StateBranch.EXECUTIVE, 100, 0.70),
        StateBranch.LEGISLATIVE: _coverage(StateBranch.LEGISLATIVE, 20, 0.0),
        StateBranch.JUDICIAL: _coverage(StateBranch.JUDICIAL, 20, 0.0),
    }
    assert choose_next_focus(report, target=0.80) == StateBranch.EXECUTIVE


def test_ai_actor_is_blocked_when_autonomy_is_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(actors.settings, "autonomy_mode_enabled", False)
    with pytest.raises(PermissionError):
        actors.canonical_actor_type("ai")


def test_ai_actor_becomes_autonomy_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(actors.settings, "autonomy_mode_enabled", True)
    assert actors.canonical_actor_type("ai") == "autonomy"
    assert actors.canonical_actor_type("autonomy") == "autonomy"
