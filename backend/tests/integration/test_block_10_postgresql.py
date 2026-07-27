import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.db.seed import seed
from app.modules.risk_engine.models import RiskFinding, RiskRule
from tests.integration.test_postgresql_guards import migrate

pytestmark = pytest.mark.integration


def _seeded(postgres_url: str) -> tuple[object, RiskFinding, RiskRule]:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with Session(engine) as db:
        seed(db)
        finding = db.scalar(
            select(RiskFinding).where(RiskFinding.finding_code == "B10-FINDING-RECURRENT")
        )
        rule = db.scalar(
            select(RiskRule).where(RiskRule.stable_code == "b10.monthly_employee_growth")
        )
        assert finding is not None and rule is not None
        db.expunge(finding)
        db.expunge(rule)
    return engine, finding, rule


def test_confirmed_finding_requires_evidence_and_ai_cannot_confirm(
    postgres_url: str,
) -> None:
    engine, finding, _ = _seeded(postgres_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(
                text("DELETE FROM finding_evidence_links WHERE finding_id=:id"),
                {"id": finding.id},
            )
            connection.execute(
                text("UPDATE risk_findings SET status='confirmed_signal' WHERE id=:id"),
                {"id": finding.id},
            )
            with pytest.raises(DBAPIError, match="requires linked evidence"):
                connection.execute(text("SET CONSTRAINTS ALL IMMEDIATE"))
        finally:
            transaction.rollback()
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text("SET LOCAL app.actor_type = 'ai'"))
            connection.execute(
                text("UPDATE risk_findings SET status='confirmed_signal' WHERE id=:id"),
                {"id": finding.id},
            )
            with pytest.raises(DBAPIError, match="AI actors"):
                connection.execute(text("SET CONSTRAINTS ALL IMMEDIATE"))
        finally:
            transaction.rollback()


def test_publication_requires_review_and_audit_is_immutable(postgres_url: str) -> None:
    engine, finding, _ = _seeded(postgres_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(
                text(
                    "UPDATE risk_findings SET visibility='public', reviewed_by_actor_id=NULL "
                    "WHERE id=:id"
                ),
                {"id": finding.id},
            )
            with pytest.raises(DBAPIError, match="requires human review"):
                connection.execute(text("SET CONSTRAINTS ALL IMMEDIATE"))
        finally:
            transaction.rollback()
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            audit_id = connection.scalar(
                text(
                    "INSERT INTO audit_events "
                    "(id, actor_type, action, entity_type, entity_id, metadata) "
                    "VALUES (gen_random_uuid(), 'human', 'test', 'risk_finding', :id, '{}') "
                    "RETURNING id"
                ),
                {"id": finding.id},
            )
            assert audit_id is not None
            with pytest.raises(DBAPIError, match="immutable"):
                connection.execute(
                    text("UPDATE audit_events SET action='changed' WHERE id=:id"),
                    {"id": audit_id},
                )
        finally:
            transaction.rollback()


def test_used_rule_requires_new_version(postgres_url: str) -> None:
    engine, _, rule = _seeded(postgres_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            with pytest.raises(DBAPIError, match="must be versioned"):
                connection.execute(
                    text("UPDATE risk_rules SET threshold_config='{\"value\": 999}' WHERE id=:id"),
                    {"id": rule.id},
                )
        finally:
            transaction.rollback()
