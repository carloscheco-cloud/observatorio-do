"""Create organizational units, events and position affiliations.

Revision ID: 0004
Revises: 0003
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    unit_type = sa.Enum(
        "GOVERNING_BODY",
        "EXECUTIVE_OFFICE",
        "DIRECTORATE",
        "DEPARTMENT",
        "DIVISION",
        "SECTION",
        "UNIT",
        "OFFICE",
        "COMMITTEE",
        "COUNCIL",
        "TERRITORIAL_OFFICE",
        "ADVISORY_BODY",
        "SUPPORT_BODY",
        "OPERATIONAL_BODY",
        "OTHER",
        name="unittype",
    )
    unit_status = sa.Enum(
        "DRAFT",
        "CANONICAL",
        "INACTIVE",
        "ELIMINATED",
        "MERGED",
        "REPLACED",
        name="unitstatus",
    )
    event_type = sa.Enum(
        "CREATION",
        "ELIMINATION",
        "MERGER",
        "SPLIT",
        "RENAME",
        "TRANSFER",
        "AFFILIATION",
        "DISAFFILIATION",
        "HIERARCHY_CHANGE",
        "TYPE_CHANGE",
        "LEGAL_BASIS_CHANGE",
        name="organizationaleventtype",
    )
    op.create_table(
        "organizational_units",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "institution_id",
            sa.Uuid(),
            sa.ForeignKey("institutions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "parent_unit_id",
            sa.Uuid(),
            sa.ForeignKey("organizational_units.id", ondelete="RESTRICT"),
        ),
        sa.Column("official_name", sa.String(300), nullable=False),
        sa.Column("normalized_name", sa.String(300), nullable=False),
        sa.Column("stable_code", sa.String(100), nullable=False),
        sa.Column("acronym", sa.String(50)),
        sa.Column("description", sa.Text()),
        sa.Column("unit_type", unit_type, nullable=False),
        sa.Column("hierarchy_level", sa.Integer(), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_headquarters", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_single_head", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("status", unit_status, server_default="DRAFT", nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_to", sa.Date()),
        sa.Column("territory_id", sa.Uuid(), sa.ForeignKey("territories.id", ondelete="RESTRICT")),
        sa.Column(
            "legal_basis_id", sa.Uuid(), sa.ForeignKey("legal_bases.id", ondelete="RESTRICT")
        ),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("institution_id", "stable_code", name="uq_unit_institution_code"),
        sa.CheckConstraint(
            "parent_unit_id IS NULL OR parent_unit_id <> id", name="ck_unit_not_self"
        ),
        sa.CheckConstraint("hierarchy_level >= 0", name="ck_unit_hierarchy_level"),
        sa.CheckConstraint("order_index >= 0", name="ck_unit_order_index"),
        sa.CheckConstraint("valid_to IS NULL OR valid_to >= valid_from", name="ck_unit_dates"),
        sa.CheckConstraint(
            "status <> 'CANONICAL' OR legal_basis_id IS NOT NULL",
            name="ck_canonical_unit_legal_basis",
        ),
    )
    op.create_table(
        "organizational_unit_evidence",
        sa.Column(
            "unit_id",
            sa.Uuid(),
            sa.ForeignKey("organizational_units.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "evidence_id",
            sa.Uuid(),
            sa.ForeignKey("evidence.id", ondelete="RESTRICT"),
            primary_key=True,
        ),
        sa.Column(
            "source_id",
            sa.Uuid(),
            sa.ForeignKey("sources.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_table(
        "organizational_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "institution_id",
            sa.Uuid(),
            sa.ForeignKey("institutions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "unit_id",
            sa.Uuid(),
            sa.ForeignKey("organizational_units.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("event_type", event_type, nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column(
            "previous_parent_id",
            sa.Uuid(),
            sa.ForeignKey("organizational_units.id", ondelete="RESTRICT"),
        ),
        sa.Column(
            "new_parent_id",
            sa.Uuid(),
            sa.ForeignKey("organizational_units.id", ondelete="RESTRICT"),
        ),
        sa.Column("previous_name", sa.String(300)),
        sa.Column("new_name", sa.String(300)),
        sa.Column(
            "legal_basis_id",
            sa.Uuid(),
            sa.ForeignKey("legal_bases.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "evidence_id",
            sa.Uuid(),
            sa.ForeignKey("evidence.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "source_id",
            sa.Uuid(),
            sa.ForeignKey("sources.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.add_column("positions", sa.Column("organizational_unit_id", sa.Uuid()))
    op.create_foreign_key(
        "fk_positions_organizational_unit",
        "positions",
        "organizational_units",
        ["organizational_unit_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_table(
        "position_unit_assignments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "position_id",
            sa.Uuid(),
            sa.ForeignKey("positions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "organizational_unit_id",
            sa.Uuid(),
            sa.ForeignKey("organizational_units.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_to", sa.Date()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "valid_to IS NULL OR valid_to >= valid_from", name="ck_position_unit_assignment_dates"
        ),
    )

    indexes = (
        ("ix_units_institution", "organizational_units", ["institution_id"]),
        ("ix_units_parent", "organizational_units", ["parent_unit_id"]),
        ("ix_units_valid_from", "organizational_units", ["valid_from"]),
        ("ix_units_valid_to", "organizational_units", ["valid_to"]),
        ("ix_units_status", "organizational_units", ["status"]),
        ("ix_units_type", "organizational_units", ["unit_type"]),
        ("ix_units_stable_code", "organizational_units", ["stable_code"]),
        (
            "ix_units_chart_as_of",
            "organizational_units",
            ["institution_id", "valid_from", "valid_to", "parent_unit_id"],
        ),
        ("ix_events_institution", "organizational_events", ["institution_id"]),
        ("ix_events_unit", "organizational_events", ["unit_id"]),
        ("ix_events_type", "organizational_events", ["event_type"]),
        ("ix_events_effective_date", "organizational_events", ["effective_date"]),
        ("ix_positions_unit", "positions", ["organizational_unit_id"]),
        (
            "ix_position_unit_assignments_unit",
            "position_unit_assignments",
            ["organizational_unit_id"],
        ),
        (
            "ix_position_unit_assignments_position",
            "position_unit_assignments",
            ["position_id"],
        ),
    )
    for name, table, columns in indexes:
        op.create_index(name, table, columns)

    op.execute(
        """
        CREATE FUNCTION validate_organizational_unit_hierarchy() RETURNS trigger AS $$
        DECLARE parent_institution uuid;
        DECLARE parent_level integer;
        BEGIN
          IF NEW.parent_unit_id IS NULL THEN
            RETURN NEW;
          END IF;
          IF NEW.parent_unit_id = NEW.id THEN
            RAISE EXCEPTION 'An organizational unit cannot be its own parent';
          END IF;
          SELECT institution_id, hierarchy_level
            INTO parent_institution, parent_level
            FROM organizational_units WHERE id = NEW.parent_unit_id;
          IF parent_institution IS DISTINCT FROM NEW.institution_id THEN
            RAISE EXCEPTION 'Parent and child must belong to the same institution';
          END IF;
          IF NEW.hierarchy_level <= parent_level THEN
            RAISE EXCEPTION 'Child hierarchy level must be below its parent';
          END IF;
          IF EXISTS (
            WITH RECURSIVE lineage AS (
              SELECT id, parent_unit_id FROM organizational_units
                WHERE id = NEW.parent_unit_id
              UNION ALL
              SELECT u.id, u.parent_unit_id FROM organizational_units u
                JOIN lineage l ON u.id = l.parent_unit_id
            )
            SELECT 1 FROM lineage WHERE id = NEW.id
          ) THEN
            RAISE EXCEPTION 'Organizational hierarchy cycle detected';
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER organizational_units_validate_hierarchy
        BEFORE INSERT OR UPDATE OF parent_unit_id, institution_id, hierarchy_level
        ON organizational_units
        FOR EACH ROW EXECUTE FUNCTION validate_organizational_unit_hierarchy();

        CREATE FUNCTION validate_unit_evidence_link() RETURNS trigger AS $$
        DECLARE canonical_source uuid;
        BEGIN
          SELECT source_id INTO canonical_source FROM evidence WHERE id = NEW.evidence_id;
          IF canonical_source IS DISTINCT FROM NEW.source_id THEN
            RAISE EXCEPTION 'Unit evidence source must match evidence source';
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER organizational_unit_evidence_validate
        BEFORE INSERT OR UPDATE ON organizational_unit_evidence
        FOR EACH ROW EXECUTE FUNCTION validate_unit_evidence_link();

        CREATE FUNCTION require_canonical_unit_traceability() RETURNS trigger AS $$
        DECLARE target_id uuid;
        DECLARE target_status unitstatus;
        DECLARE target_legal_basis uuid;
        BEGIN
          IF TG_TABLE_NAME = 'organizational_units' THEN
            target_id := NEW.id;
          ELSIF TG_OP = 'DELETE' THEN
            target_id := OLD.unit_id;
          ELSE
            target_id := NEW.unit_id;
          END IF;
          SELECT status, legal_basis_id INTO target_status, target_legal_basis
            FROM organizational_units WHERE id = target_id;
          IF target_status = 'CANONICAL' AND (
            target_legal_basis IS NULL OR NOT EXISTS (
              SELECT 1 FROM organizational_unit_evidence l
              JOIN evidence e ON e.id = l.evidence_id
              JOIN sources s ON s.id = l.source_id
              WHERE l.unit_id = target_id AND e.source_id = s.id
            )
          ) THEN
            RAISE EXCEPTION
              'Canonical organizational unit requires legal basis, evidence and source';
          END IF;
          RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;

        CREATE CONSTRAINT TRIGGER organizational_units_require_traceability
        AFTER INSERT OR UPDATE ON organizational_units
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION require_canonical_unit_traceability();

        CREATE CONSTRAINT TRIGGER organizational_unit_evidence_preserve_traceability
        AFTER INSERT OR UPDATE OR DELETE ON organizational_unit_evidence
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION require_canonical_unit_traceability();

        CREATE FUNCTION validate_organizational_event() RETURNS trigger AS $$
        DECLARE unit_institution uuid;
        DECLARE evidence_source uuid;
        DECLARE parent_institution uuid;
        BEGIN
          SELECT institution_id INTO unit_institution
            FROM organizational_units WHERE id = NEW.unit_id;
          IF unit_institution IS DISTINCT FROM NEW.institution_id THEN
            RAISE EXCEPTION 'Event unit must belong to event institution';
          END IF;
          SELECT source_id INTO evidence_source FROM evidence WHERE id = NEW.evidence_id;
          IF evidence_source IS DISTINCT FROM NEW.source_id THEN
            RAISE EXCEPTION 'Event source must match evidence source';
          END IF;
          IF NEW.new_parent_id IS NOT NULL THEN
            SELECT institution_id INTO parent_institution
              FROM organizational_units WHERE id = NEW.new_parent_id;
            IF parent_institution IS DISTINCT FROM NEW.institution_id THEN
              RAISE EXCEPTION 'New parent must belong to event institution';
            END IF;
            IF EXISTS (
              WITH RECURSIVE descendants AS (
                SELECT id FROM organizational_units WHERE parent_unit_id = NEW.unit_id
                UNION ALL
                SELECT u.id FROM organizational_units u
                  JOIN descendants d ON u.parent_unit_id = d.id
              )
              SELECT 1 FROM descendants WHERE id = NEW.new_parent_id
            ) THEN
              RAISE EXCEPTION 'A hierarchy change cannot target a descendant';
            END IF;
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER organizational_events_validate
        BEFORE INSERT OR UPDATE ON organizational_events
        FOR EACH ROW EXECUTE FUNCTION validate_organizational_event();

        CREATE FUNCTION validate_position_unit() RETURNS trigger AS $$
        DECLARE position_institution uuid;
        DECLARE unit_institution uuid;
        BEGIN
          IF TG_TABLE_NAME = 'positions' THEN
            IF NEW.organizational_unit_id IS NULL THEN RETURN NEW; END IF;
            position_institution := NEW.institution_id;
            SELECT institution_id INTO unit_institution
              FROM organizational_units WHERE id = NEW.organizational_unit_id;
          ELSE
            SELECT institution_id INTO position_institution
              FROM positions WHERE id = NEW.position_id;
            SELECT institution_id INTO unit_institution
              FROM organizational_units WHERE id = NEW.organizational_unit_id;
          END IF;
          IF position_institution IS DISTINCT FROM unit_institution THEN
            RAISE EXCEPTION 'Position and organizational unit must belong to same institution';
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER positions_validate_unit
        BEFORE INSERT OR UPDATE OF institution_id, organizational_unit_id ON positions
        FOR EACH ROW EXECUTE FUNCTION validate_position_unit();

        CREATE TRIGGER position_unit_assignments_validate
        BEFORE INSERT OR UPDATE ON position_unit_assignments
        FOR EACH ROW EXECUTE FUNCTION validate_position_unit();
        """
    )
    for table in (
        "organizational_units",
        "organizational_unit_evidence",
        "organizational_events",
        "position_unit_assignments",
    ):
        op.execute(
            f"CREATE TRIGGER {table}_reject_ai BEFORE INSERT OR UPDATE OR DELETE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION reject_ai_canonical_write()"
        )


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS validate_position_unit() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS validate_organizational_event() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS require_canonical_unit_traceability() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS validate_unit_evidence_link() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS validate_organizational_unit_hierarchy() CASCADE")
    op.drop_table("position_unit_assignments")
    op.drop_constraint("fk_positions_organizational_unit", "positions", type_="foreignkey")
    op.drop_column("positions", "organizational_unit_id")
    op.drop_table("organizational_events")
    op.drop_table("organizational_unit_evidence")
    op.drop_table("organizational_units")
    sa.Enum(name="organizationaleventtype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="unitstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="unittype").drop(op.get_bind(), checkfirst=True)
