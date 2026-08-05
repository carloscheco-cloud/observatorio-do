"""Add versioned transparency methodologies and OED-TD-1.1 rules.

Revision ID: 0018
Revises: 0017
"""
# ruff: noqa: E501

from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa

from alembic import op
from app.modules.digital_transparency.methodology_v1_1 import RULES
from app.modules.digital_transparency.models import TransparencyMethodology, TransparencyScoringRule

revision: str = "0018"
down_revision: str | None = "0017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _immutability_trigger() -> None:
    op.execute(
        """
        CREATE FUNCTION transparency_methodology_immutable() RETURNS trigger AS $$
        BEGIN
          IF OLD.status = 'published' OR OLD.is_immutable THEN
            RAISE EXCEPTION 'Published transparency methodologies are immutable';
          END IF;
          RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
        END;
        $$ LANGUAGE plpgsql;
        CREATE TRIGGER trg_transparency_methodology_immutable
          BEFORE UPDATE OR DELETE ON transparency_methodologies
          FOR EACH ROW EXECUTE FUNCTION transparency_methodology_immutable();
        CREATE FUNCTION transparency_rule_immutable() RETURNS trigger AS $$
        BEGIN
          IF EXISTS (SELECT 1 FROM transparency_methodologies
                     WHERE version = OLD.methodology_version
                       AND (status = 'published' OR is_immutable)) THEN
            RAISE EXCEPTION 'Published transparency scoring rules are immutable';
          END IF;
          RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
        END;
        $$ LANGUAGE plpgsql;
        CREATE TRIGGER trg_transparency_rule_immutable
          BEFORE UPDATE OR DELETE ON transparency_scoring_rules
          FOR EACH ROW EXECUTE FUNCTION transparency_rule_immutable();
        """
    )


def upgrade() -> None:
    bind = op.get_bind()
    TransparencyMethodology.__table__.create(bind)
    TransparencyScoringRule.__table__.create(bind)
    existing_columns = {
        item["name"] for item in sa.inspect(bind).get_columns("transparency_assessment_components")
    }
    if "rule_code" not in existing_columns:
        op.add_column("transparency_assessment_components", sa.Column("rule_code", sa.String(100)))
    if "public_explanation" not in existing_columns:
        op.add_column(
            "transparency_assessment_components", sa.Column("public_explanation", sa.Text())
        )
    now = datetime(2026, 8, 4, tzinfo=UTC)
    op.bulk_insert(
        TransparencyMethodology.__table__,
        [
            {
                "version": "OED-TD-1.0",
                "name": "Disponibilidad digital OED-TD 1.0",
                "description": "Metodología histórica PE-05; se registra sin alterar sus requisitos ni evaluaciones.",
                "published_at": now,
                "supersedes_version": None,
                "status": "published",
                "is_immutable": True,
            },
            {
                "version": "OED-TD-1.1",
                "name": "Disponibilidad digital OED-TD 1.1",
                "description": "Escalas discretas, reproducibles y auditables para las ocho dimensiones.",
                "published_at": now,
                "supersedes_version": "OED-TD-1.0",
                "status": "published",
                "is_immutable": True,
            },
        ],
    )
    op.bulk_insert(
        TransparencyScoringRule.__table__,
        [
            {
                "id": __import__("uuid").uuid4(),
                "methodology_version": rule.methodology_version,
                "dimension": rule.dimension,
                "rule_code": rule.rule_code,
                "description": rule.description,
                "awarded_score": rule.awarded_score,
                "maximum_score": rule.maximum_score,
                "conditions_json": rule.conditions,
                "public_explanation": rule.public_explanation,
                "quality_level": rule.quality_level,
                "severity": None,
                "active": True,
            }
            for rule in RULES
        ],
    )
    _immutability_trigger()


def downgrade() -> None:
    bind = op.get_bind()
    count = bind.scalar(
        sa.text(
            "SELECT count(*) FROM transparency_assessment_components WHERE methodology_version = 'OED-TD-1.1'"
        )
    )
    if count:
        raise RuntimeError("Remove OED-TD-1.1 assessments before downgrade 0018")
    op.execute("DROP TRIGGER trg_transparency_rule_immutable ON transparency_scoring_rules")
    op.execute("DROP FUNCTION transparency_rule_immutable()")
    op.execute("DROP TRIGGER trg_transparency_methodology_immutable ON transparency_methodologies")
    op.execute("DROP FUNCTION transparency_methodology_immutable()")
    op.drop_column("transparency_assessment_components", "public_explanation")
    op.drop_column("transparency_assessment_components", "rule_code")
    op.drop_table("transparency_scoring_rules")
    op.drop_table("transparency_methodologies")
