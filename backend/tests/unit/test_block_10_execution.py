import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.seed import seed
from app.modules.appointments.models import Appointment
from app.modules.employment_relationships.models import EmploymentRelationship
from app.modules.risk_engine import service
from app.modules.risk_engine.engine import EvaluationContext
from app.modules.risk_engine.models import (
    FindingEvidenceLink,
    RiskFinding,
    RiskRule,
    RiskScore,
    RiskSuppression,
)
from app.modules.risk_engine.schemas import EvaluationRequest


def _request(*, dry_run: bool = False) -> EvaluationRequest:
    return EvaluationRequest(
        trigger_type="manual",
        period_start=date(2099, 1, 1),
        period_end=date(2099, 12, 31),
        dry_run=dry_run,
    )


def test_real_execution_creates_evidenced_findings_and_scores(db: Session) -> None:
    seed(db)
    before = db.scalar(select(func.count()).select_from(RiskFinding)) or 0
    run = service.run_evaluation(db, _request(), actor_type="service", actor_id=None)
    db.commit()
    created = db.scalar(
        select(func.count()).select_from(RiskFinding).where(RiskFinding.evaluation_run_id == run.id)
    )
    assert run.status == "completed"
    assert run.records_evaluated > 0
    assert run.findings_created > 0
    assert created == run.findings_created
    assert (db.scalar(select(func.count()).select_from(RiskFinding)) or 0) > before
    assert db.scalar(select(func.count()).select_from(FindingEvidenceLink)) >= run.findings_created
    assert db.scalar(select(func.count()).select_from(RiskScore)) > 0
    summaries = run.metadata_["summary"]
    assert isinstance(summaries, dict)
    assert all("error" not in value for value in summaries.values() if isinstance(value, dict))


def test_dry_run_does_not_persist_findings_or_scores(db: Session) -> None:
    seed(db)
    before_findings = db.scalar(select(func.count()).select_from(RiskFinding))
    before_scores = db.scalar(select(func.count()).select_from(RiskScore))
    run = service.run_evaluation(db, _request(dry_run=True), actor_type="service", actor_id=None)
    db.commit()
    assert run.findings_created > 0
    assert db.scalar(select(func.count()).select_from(RiskFinding)) == before_findings
    assert db.scalar(select(func.count()).select_from(RiskScore)) == before_scores


def test_second_execution_is_idempotent_and_increments_recurrence(db: Session) -> None:
    seed(db)
    first = service.run_evaluation(db, _request(), actor_type="service", actor_id=None)
    db.commit()
    finding = db.scalar(select(RiskFinding).where(RiskFinding.evaluation_run_id == first.id))
    assert finding is not None
    count = db.scalar(select(func.count()).select_from(RiskFinding))
    occurrence = finding.occurrence_count
    second = service.run_evaluation(db, _request(), actor_type="service", actor_id=None)
    db.commit()
    db.refresh(finding)
    assert db.scalar(select(func.count()).select_from(RiskFinding)) == count
    assert second.findings_updated > 0
    assert finding.occurrence_count == occurrence + 1


def test_suppression_and_disabled_rule_are_respected(db: Session) -> None:
    seed(db)
    rule = db.scalar(select(RiskRule).where(RiskRule.stable_code == "b10.stale_source"))
    assert rule is not None
    rule.enabled = False
    reviewer = uuid.uuid4()
    other = db.scalar(select(RiskRule).where(RiskRule.stable_code == "b10.asset_without_custodian"))
    assert other is not None
    db.add(
        RiskSuppression(
            risk_rule_id=other.id,
            reason="Controlled test",
            valid_from=date(2099, 1, 1),
            valid_to=date(2099, 12, 31),
            approved_by_actor_id=reviewer,
        )
    )
    db.commit()
    run = service.run_evaluation(db, _request(), actor_type="service", actor_id=None)
    db.commit()
    assert run.findings_suppressed > 0
    assert (
        db.scalar(
            select(func.count()).select_from(RiskFinding).where(RiskFinding.risk_rule_id == rule.id)
        )
        == 0
    )


def test_adapter_failure_does_not_stop_execution(db: Session, monkeypatch: object) -> None:
    seed(db)
    original = service.ADAPTERS[0].evaluate

    def fail(*args: object, **kwargs: object) -> object:
        raise RuntimeError("controlled adapter failure")

    service.ADAPTERS[0].evaluate = fail
    try:
        run = service.run_evaluation(db, _request(), actor_type="service", actor_id=None)
        db.commit()
    finally:
        service.ADAPTERS[0].evaluate = original
    assert run.status == "completed_with_errors"
    assert run.errors_count == 1
    assert run.findings_created > 0


def test_cross_domain_findings_have_complete_explanations(db: Session) -> None:
    seed(db)
    run = service.run_evaluation(
        db,
        EvaluationRequest(
            trigger_type="manual",
            domain="cross_domain",
            period_end=date(2099, 12, 31),
        ),
        actor_type="service",
        actor_id=None,
    )
    db.commit()
    findings = list(
        db.scalars(
            select(RiskFinding).where(
                RiskFinding.evaluation_run_id == run.id,
                RiskFinding.domain == "cross_domain",
            )
        )
    )
    assert findings
    for finding in findings:
        assert "Regla aplicada:" in finding.public_explanation
        assert "Umbral:" in finding.public_explanation
        assert "Comparación:" in finding.public_explanation
        assert "no permite concluir fraude" in finding.public_explanation


def test_every_registered_adapter_produces_a_controlled_real_candidate(db: Session) -> None:
    seed(db)
    relationship = db.scalar(select(EmploymentRelationship))
    assert relationship is not None
    relationship.organizational_unit_id = None
    for appointment in db.scalars(select(Appointment)):
        appointment.status = "ended"
    db.flush()
    rules = list(db.scalars(select(RiskRule).where(RiskRule.enabled.is_(True))))
    context = EvaluationContext(
        run_id=uuid.uuid4(),
        as_of=date(2099, 12, 31),
        dry_run=True,
    )
    results = {
        adapter.__name__: adapter(db, rules).evaluate(context) for adapter in service.ADAPTERS
    }
    assert all(result.candidates for result in results.values()), {
        name: len(result.candidates) for name, result in results.items()
    }
    assert all(
        candidate.evidence_links for result in results.values() for candidate in result.candidates
    )
