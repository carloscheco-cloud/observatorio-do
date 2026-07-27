"""Create block 3 persons, positions, legal bases and appointments.

Revision ID: 0002
Revises: 0001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    person_status = sa.Enum("DRAFT", "CONFIRMED", "INACTIVE", name="personstatus")
    legal_type = sa.Enum(
        "CONSTITUTION",
        "LAW",
        "DECREE",
        "RESOLUTION",
        "REGULATION",
        "ORDINANCE",
        "OTHER",
        name="legalinstrumenttype",
    )
    access_method = sa.Enum(
        "ELECTION", "APPOINTMENT", "COMPETITION", "EX_OFFICIO", "OTHER", name="accessmethod"
    )
    position_status = sa.Enum("DRAFT", "CANONICAL", "INACTIVE", name="positionstatus")
    appointment_status = sa.Enum(
        "PENDING", "CONFIRMED", "ENDED", "REVOKED", name="appointmentstatus"
    )

    op.create_table(
        "persons",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("full_name", sa.String(300), nullable=False),
        sa.Column("normalized_name", sa.String(300), nullable=False),
        sa.Column("national_id_hash", sa.String(64), unique=True),
        sa.Column("birth_date", sa.Date()),
        sa.Column("nationality", sa.String(100)),
        sa.Column("status", person_status, server_default="DRAFT", nullable=False),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "national_id_hash IS NULL OR national_id_hash ~ '^[0-9a-f]{64}$'",
            name="ck_person_national_id_sha256",
        ),
    )
    op.create_index("ix_persons_normalized_name", "persons", ["normalized_name"])
    op.create_table(
        "legal_bases",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("instrument_type", legal_type, nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("reference", sa.String(300), nullable=False, unique=True),
        sa.Column("article", sa.String(100)),
        sa.Column("official_url", sa.String(1000)),
        sa.Column(
            "evidence_id",
            sa.Uuid(),
            sa.ForeignKey("evidence.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("effective_from", sa.Date()),
        sa.Column("effective_to", sa.Date()),
        sa.Column("issuing_body", sa.String(300), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_from IS NULL OR effective_to >= effective_from",
            name="ck_legal_basis_dates",
        ),
    )
    op.create_table(
        "positions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "institution_id",
            sa.Uuid(),
            sa.ForeignKey("institutions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("official_name", sa.String(300), nullable=False),
        sa.Column("code", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text()),
        sa.Column("position_type", sa.String(100), nullable=False),
        sa.Column("hierarchy_level", sa.String(100), nullable=False),
        sa.Column("access_method", access_method, nullable=False),
        sa.Column(
            "legal_basis_id",
            sa.Uuid(),
            sa.ForeignKey("legal_bases.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("status", position_status, server_default="DRAFT", nullable=False),
        sa.Column("valid_from", sa.Date()),
        sa.Column("valid_to", sa.Date()),
        sa.Column("single_occupant", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "valid_to IS NULL OR valid_from IS NULL OR valid_to >= valid_from",
            name="ck_position_dates",
        ),
    )
    op.create_table(
        "appointments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("person_id", sa.Uuid(), sa.ForeignKey("persons.id", ondelete="RESTRICT")),
        sa.Column("position_id", sa.Uuid(), sa.ForeignKey("positions.id", ondelete="RESTRICT")),
        sa.Column(
            "institution_id", sa.Uuid(), sa.ForeignKey("institutions.id", ondelete="RESTRICT")
        ),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("appointment_type", sa.String(100), nullable=False),
        sa.Column("status", appointment_status, server_default="PENDING", nullable=False),
        sa.Column("legal_act", sa.String(500)),
        sa.Column("evidence_id", sa.Uuid(), sa.ForeignKey("evidence.id", ondelete="RESTRICT")),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id", ondelete="RESTRICT")),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "end_date IS NULL OR start_date IS NULL OR end_date >= start_date",
            name="ck_appointment_dates",
        ),
        sa.CheckConstraint(
            "status <> 'CONFIRMED' OR "
            "(person_id IS NOT NULL AND position_id IS NOT NULL AND institution_id IS NOT NULL "
            "AND evidence_id IS NOT NULL AND source_id IS NOT NULL AND start_date IS NOT NULL "
            "AND legal_act IS NOT NULL)",
            name="ck_confirmed_appointment_complete",
        ),
    )

    for table in ("persons", "legal_bases", "positions", "appointments"):
        op.execute(
            f"CREATE TRIGGER {table}_reject_ai BEFORE INSERT OR UPDATE OR DELETE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION reject_ai_canonical_write()"
        )

    op.execute(
        """
        CREATE FUNCTION validate_appointment_integrity() RETURNS trigger AS $$
        DECLARE canonical_institution uuid;
        DECLARE is_single boolean;
        DECLARE evidence_source uuid;
        BEGIN
          IF NEW.status = 'CONFIRMED' THEN
            SELECT institution_id, single_occupant
              INTO canonical_institution, is_single
              FROM positions WHERE id = NEW.position_id;
            IF canonical_institution IS DISTINCT FROM NEW.institution_id THEN
              RAISE EXCEPTION 'Appointment institution must match position institution';
            END IF;
            SELECT source_id INTO evidence_source FROM evidence WHERE id = NEW.evidence_id;
            IF evidence_source IS DISTINCT FROM NEW.source_id THEN
              RAISE EXCEPTION 'Appointment source must be the source of its evidence';
            END IF;
            IF is_single AND EXISTS (
              SELECT 1 FROM appointments a
              WHERE a.position_id = NEW.position_id
                AND a.status = 'CONFIRMED'
                AND a.id <> NEW.id
                AND daterange(a.start_date, COALESCE(a.end_date + 1, 'infinity'::date), '[)')
                    && daterange(NEW.start_date, COALESCE(NEW.end_date + 1, 'infinity'::date), '[)')
            ) THEN
              RAISE EXCEPTION 'Single-occupant position has an incompatible active appointment';
            END IF;
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER appointments_validate_integrity
        BEFORE INSERT OR UPDATE ON appointments
        FOR EACH ROW EXECUTE FUNCTION validate_appointment_integrity();
        """
    )


def downgrade() -> None:
    op.drop_table("appointments")
    op.drop_table("positions")
    op.drop_table("legal_bases")
    op.drop_index("ix_persons_normalized_name", table_name="persons")
    op.drop_table("persons")
    op.execute("DROP FUNCTION IF EXISTS validate_appointment_integrity()")
    sa.Enum(name="appointmentstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="positionstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="accessmethod").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="legalinstrumenttype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="personstatus").drop(op.get_bind(), checkfirst=True)
