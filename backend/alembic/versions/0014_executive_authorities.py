# ruff: noqa: E501
"""Support traceable Executive Branch authorities.

Revision ID: 0014
Revises: 0013
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0014"
down_revision: str | None = "0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

capacity = postgresql.ENUM(
    "SUBSTANTIVE", "ACTING", "TEMPORARY", "DELEGATED", name="appointmentcapacity"
)
mechanism = postgresql.ENUM(
    "CONSTITUTIONAL_ELECTION",
    "PRESIDENTIAL_DECREE",
    "LEGAL_DESIGNATION",
    "EX_OFFICIO",
    name="appointmentmechanism",
)


def _replace_status(values: tuple[str, ...]) -> None:
    op.execute("ALTER TYPE appointmentstatus RENAME TO appointmentstatus_old")
    op.execute(f"CREATE TYPE appointmentstatus AS ENUM ({', '.join(repr(v) for v in values)})")
    op.execute(
        "ALTER TABLE appointments ALTER COLUMN status DROP DEFAULT; "
        "ALTER TABLE appointments ALTER COLUMN status TYPE appointmentstatus "
        "USING status::text::appointmentstatus; "
        "ALTER TABLE appointments ALTER COLUMN status SET DEFAULT 'PENDING'"
    )
    op.execute("DROP TYPE appointmentstatus_old")


def upgrade() -> None:
    bind = op.get_bind()
    capacity.create(bind, checkfirst=True)
    mechanism.create(bind, checkfirst=True)
    op.drop_constraint("ck_confirmed_appointment_complete", "appointments", type_="check")
    _replace_status(
        (
            "ANNOUNCED",
            "PENDING_START",
            "PENDING",
            "CONFIRMED",
            "ACTIVE",
            "ENDED",
            "REVOKED",
            "DISPUTED",
        )
    )
    op.add_column("appointments", sa.Column("capacity", capacity, nullable=True))
    op.add_column("appointments", sa.Column("mechanism", mechanism, nullable=True))
    op.add_column("appointments", sa.Column("decree_number", sa.String(50), nullable=True))
    op.add_column("appointments", sa.Column("decree_date", sa.Date(), nullable=True))
    op.add_column("appointments", sa.Column("legal_act_url", sa.String(1000), nullable=True))
    op.add_column("appointments", sa.Column("legal_act_locator", sa.String(500), nullable=True))
    op.add_column("appointments", sa.Column("start_date_basis", sa.Text(), nullable=True))
    op.add_column("appointments", sa.Column("notes", sa.Text(), nullable=True))
    op.create_table(
        "person_evidence",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "person_id", sa.Uuid(), sa.ForeignKey("persons.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "evidence_id",
            sa.Uuid(),
            sa.ForeignKey("evidence.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("relation", sa.String(100), nullable=False),
        sa.UniqueConstraint("person_id", "evidence_id"),
    )
    op.create_table(
        "position_evidence",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "position_id",
            sa.Uuid(),
            sa.ForeignKey("positions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "evidence_id",
            sa.Uuid(),
            sa.ForeignKey("evidence.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("relation", sa.String(100), nullable=False),
        sa.UniqueConstraint("position_id", "evidence_id"),
    )
    op.create_table(
        "appointment_evidence",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "appointment_id",
            sa.Uuid(),
            sa.ForeignKey("appointments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "evidence_id",
            sa.Uuid(),
            sa.ForeignKey("evidence.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("relation", sa.String(100), nullable=False),
        sa.UniqueConstraint("appointment_id", "evidence_id"),
    )
    op.create_table(
        "executive_authority_load_records",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("manifest_version", sa.String(50), nullable=False),
        sa.Column("record_type", sa.String(40), nullable=False),
        sa.Column("record_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("manifest_version", "record_type", "record_id"),
    )
    op.create_index(
        "ix_executive_authority_record_lookup",
        "executive_authority_load_records",
        ["manifest_version", "record_type"],
    )
    op.create_check_constraint(
        "ck_confirmed_appointment_complete",
        "appointments",
        "status <> 'CONFIRMED' OR (person_id IS NOT NULL AND position_id IS NOT NULL AND institution_id IS NOT NULL AND evidence_id IS NOT NULL AND source_id IS NOT NULL AND start_date IS NOT NULL AND legal_act IS NOT NULL)",
    )
    op.create_check_constraint(
        "ck_active_appointment_complete",
        "appointments",
        "status <> 'ACTIVE' OR (person_id IS NOT NULL AND position_id IS NOT NULL AND institution_id IS NOT NULL AND evidence_id IS NOT NULL AND source_id IS NOT NULL AND capacity IS NOT NULL AND mechanism IS NOT NULL AND start_date_basis IS NOT NULL AND (start_date IS NOT NULL OR notes IS NOT NULL))",
    )
    op.create_check_constraint(
        "ck_appointment_decree_traceable",
        "appointments",
        "decree_number IS NULL OR (mechanism = 'PRESIDENTIAL_DECREE' AND decree_date IS NOT NULL AND legal_act_url IS NOT NULL AND legal_act_locator IS NOT NULL)",
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION validate_appointment_integrity() RETURNS trigger AS $$
        DECLARE canonical_institution uuid; DECLARE is_single boolean; DECLARE evidence_source uuid;
        BEGIN
          IF NEW.status IN ('CONFIRMED','ACTIVE') THEN
            SELECT institution_id, single_occupant INTO canonical_institution, is_single FROM positions WHERE id=NEW.position_id;
            IF canonical_institution IS DISTINCT FROM NEW.institution_id THEN RAISE EXCEPTION 'Appointment institution must match position institution'; END IF;
            SELECT source_id INTO evidence_source FROM evidence WHERE id=NEW.evidence_id;
            IF evidence_source IS DISTINCT FROM NEW.source_id THEN RAISE EXCEPTION 'Appointment source must be the source of its evidence'; END IF;
            IF is_single AND (NEW.capacity IS NULL OR NEW.capacity='SUBSTANTIVE') AND EXISTS (
              SELECT 1 FROM appointments a WHERE a.position_id=NEW.position_id AND a.status IN ('CONFIRMED','ACTIVE')
              AND (a.capacity IS NULL OR a.capacity='SUBSTANTIVE') AND a.id<>NEW.id
              AND daterange(a.start_date,COALESCE(a.end_date+1,'infinity'::date),'[)') && daterange(NEW.start_date,COALESCE(NEW.end_date+1,'infinity'::date),'[)')
            ) THEN RAISE EXCEPTION 'Single-occupant position has incompatible substantive appointments'; END IF;
          END IF; RETURN NEW;
        END; $$ LANGUAGE plpgsql;
        """
    )


def downgrade() -> None:
    op.execute(
        "DO $$ BEGIN IF EXISTS (SELECT 1 FROM executive_authority_load_records) THEN RAISE EXCEPTION 'Rollback PE-04 data before downgrade 0014'; END IF; END $$"
    )
    op.drop_constraint("ck_active_appointment_complete", "appointments", type_="check")
    op.drop_constraint("ck_appointment_decree_traceable", "appointments", type_="check")
    op.drop_constraint("ck_confirmed_appointment_complete", "appointments", type_="check")
    op.drop_table("appointment_evidence")
    op.drop_table("position_evidence")
    op.drop_table("person_evidence")
    op.drop_index(
        "ix_executive_authority_record_lookup", table_name="executive_authority_load_records"
    )
    op.drop_table("executive_authority_load_records")
    op.drop_column("appointments", "mechanism")
    op.drop_column("appointments", "capacity")
    op.drop_column("appointments", "notes")
    op.drop_column("appointments", "start_date_basis")
    op.drop_column("appointments", "legal_act_locator")
    op.drop_column("appointments", "legal_act_url")
    op.drop_column("appointments", "decree_date")
    op.drop_column("appointments", "decree_number")
    _replace_status(("PENDING", "CONFIRMED", "ENDED", "REVOKED"))
    mechanism.drop(op.get_bind(), checkfirst=True)
    capacity.drop(op.get_bind(), checkfirst=True)
    op.create_check_constraint(
        "ck_confirmed_appointment_complete",
        "appointments",
        "status <> 'CONFIRMED' OR (person_id IS NOT NULL AND position_id IS NOT NULL AND institution_id IS NOT NULL AND evidence_id IS NOT NULL AND source_id IS NOT NULL AND start_date IS NOT NULL AND legal_act IS NOT NULL)",
    )
