"""Fix deferred institution evidence trigger record access.

Revision ID: 0003
Revises: 0002
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION require_any_institution_evidence() RETURNS trigger AS $$
        DECLARE target_id uuid;
        BEGIN
          IF TG_TABLE_NAME = 'institutions' THEN
            target_id := NEW.id;
          ELSE
            target_id := OLD.institution_id;
          END IF;
          IF EXISTS (SELECT 1 FROM institutions WHERE id = target_id)
             AND NOT EXISTS (
               SELECT 1 FROM institution_evidence WHERE institution_id = target_id
             )
          THEN
            RAISE EXCEPTION 'An institution requires at least one evidence record';
          END IF;
          RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION require_any_institution_evidence() RETURNS trigger AS $$
        DECLARE target_id uuid;
        BEGIN
          target_id := CASE WHEN TG_TABLE_NAME = 'institutions' THEN NEW.id
                            ELSE OLD.institution_id END;
          IF EXISTS (SELECT 1 FROM institutions WHERE id = target_id)
             AND NOT EXISTS (
               SELECT 1 FROM institution_evidence WHERE institution_id = target_id
             )
          THEN
            RAISE EXCEPTION 'An institution requires at least one evidence record';
          END IF;
          RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
        """
    )
