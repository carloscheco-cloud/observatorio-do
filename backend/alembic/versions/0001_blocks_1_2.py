"""Create blocks 1 and 2 schema and PostgreSQL protections.

Revision ID: 0001
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    territory_type = sa.Enum("COUNTRY", "PROVINCE", "MUNICIPALITY", name="territorytype")
    institution_status = sa.Enum("DRAFT", "CONFIRMED", name="institutionstatus")

    op.create_table(
        "territories",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("code", sa.String(32), nullable=False, unique=True),
        sa.Column("type", territory_type, nullable=False),
        sa.Column("parent_id", sa.Uuid(), sa.ForeignKey("territories.id")),
    )
    op.create_table(
        "sources",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("url", sa.String(1000), nullable=False, unique=True),
        sa.Column("publisher", sa.String(200), nullable=False),
        sa.Column("is_official", sa.Boolean(), nullable=False),
        sa.Column(
            "retrieved_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_table(
        "evidence",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=False),
        sa.Column("locator", sa.String(1000), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column(
            "observed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_table(
        "institutions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(300), nullable=False, unique=True),
        sa.Column("kind", sa.String(100), nullable=False),
        sa.Column("territory_id", sa.Uuid(), sa.ForeignKey("territories.id"), nullable=False),
        sa.Column(
            "status",
            institution_status,
            server_default="DRAFT",
            nullable=False,
        ),
    )
    op.create_table(
        "institution_evidence",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "institution_id",
            sa.Uuid(),
            sa.ForeignKey("institutions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "evidence_id",
            sa.Uuid(),
            sa.ForeignKey("evidence.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "relation",
            sa.String(100),
            server_default="supports_existence",
            nullable=False,
        ),
        sa.UniqueConstraint("institution_id", "evidence_id"),
    )

    op.execute(
        """
        CREATE FUNCTION reject_ai_canonical_write() RETURNS trigger AS $$
        BEGIN
          IF lower(COALESCE(current_setting('app.actor_type', true), 'human')) = 'ai' THEN
            RAISE EXCEPTION 'AI actors cannot write canonical tables';
          END IF;
          IF TG_OP = 'DELETE' THEN
            RETURN OLD;
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER territories_reject_ai
        BEFORE INSERT OR UPDATE OR DELETE ON territories
        FOR EACH ROW EXECUTE FUNCTION reject_ai_canonical_write();

        CREATE TRIGGER institutions_reject_ai
        BEFORE INSERT OR UPDATE OR DELETE ON institutions
        FOR EACH ROW EXECUTE FUNCTION reject_ai_canonical_write();
        """
    )
    op.execute(
        """
        CREATE FUNCTION require_institution_evidence() RETURNS trigger AS $$
        BEGIN
          IF NEW.status = 'CONFIRMED'
             AND NOT EXISTS (
               SELECT 1 FROM institution_evidence ie WHERE ie.institution_id = NEW.id
             )
          THEN
            RAISE EXCEPTION 'A confirmed institution requires evidence';
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER institutions_require_evidence
        BEFORE INSERT OR UPDATE OF status ON institutions
        FOR EACH ROW EXECUTE FUNCTION require_institution_evidence();

        CREATE FUNCTION protect_last_institution_evidence() RETURNS trigger AS $$
        BEGIN
          IF EXISTS (
            SELECT 1 FROM institutions i
            WHERE i.id = OLD.institution_id AND i.status = 'CONFIRMED'
          ) AND NOT EXISTS (
            SELECT 1 FROM institution_evidence ie
            WHERE ie.institution_id = OLD.institution_id AND ie.id <> OLD.id
          )
          THEN
            RAISE EXCEPTION 'Cannot remove the last evidence from a confirmed institution';
          END IF;
          RETURN OLD;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER institution_evidence_protect_last
        BEFORE DELETE ON institution_evidence
        FOR EACH ROW EXECUTE FUNCTION protect_last_institution_evidence();
        """
    )
    op.execute(
        """
        CREATE FUNCTION require_any_institution_evidence() RETURNS trigger AS $$
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

        CREATE CONSTRAINT TRIGGER institutions_always_require_evidence
        AFTER INSERT OR UPDATE ON institutions
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION require_any_institution_evidence();

        CREATE CONSTRAINT TRIGGER evidence_delete_preserves_institution
        AFTER DELETE ON institution_evidence
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION require_any_institution_evidence();
        """
    )


def downgrade() -> None:
    op.drop_table("institution_evidence")
    op.drop_table("institutions")
    op.drop_table("evidence")
    op.drop_table("sources")
    op.drop_table("territories")
    op.execute("DROP FUNCTION IF EXISTS protect_last_institution_evidence()")
    op.execute("DROP FUNCTION IF EXISTS require_institution_evidence()")
    op.execute("DROP FUNCTION IF EXISTS require_any_institution_evidence()")
    op.execute("DROP FUNCTION IF EXISTS reject_ai_canonical_write()")
    sa.Enum(name="institutionstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="territorytype").drop(op.get_bind(), checkfirst=True)
