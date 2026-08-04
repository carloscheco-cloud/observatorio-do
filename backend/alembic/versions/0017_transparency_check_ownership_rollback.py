"""Allow owned transparency checks to be removed by manifest rollback.

Revision ID: 0017
Revises: 0016
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0017"
down_revision: str | None = "0016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _replace_function(*, pe06a_only: bool) -> None:
    ownership_filter = "manifest_version = 'PE-06A-2026-08-03' AND " if pe06a_only else ""
    op.execute(
        f"""
        CREATE OR REPLACE FUNCTION transparency_check_history_immutable() RETURNS trigger AS $$
        BEGIN
          IF TG_OP = 'DELETE' AND EXISTS (
            SELECT 1 FROM digital_transparency_load_records
            WHERE {ownership_filter}record_id = OLD.id
              AND record_type IN ('resource_check', 'searchability_check')
          ) THEN
            RETURN OLD;
          END IF;
          RAISE EXCEPTION 'Technical check history is immutable';
        END;
        $$ LANGUAGE plpgsql;
        """
    )


def upgrade() -> None:
    _replace_function(pe06a_only=False)


def downgrade() -> None:
    _replace_function(pe06a_only=True)
