"""Support verifiable Executive Branch dependencies.

Revision ID: 0013
Revises: 0012
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0013"
down_revision: str | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _replace_enum(name: str, values: tuple[str, ...], columns: tuple[tuple[str, str], ...]) -> None:
    op.execute(f"ALTER TYPE {name} RENAME TO {name}_old")
    op.execute(f"CREATE TYPE {name} AS ENUM ({', '.join(repr(value) for value in values)})")
    for table, column in columns:
        op.execute(
            f"ALTER TABLE {table} ALTER COLUMN {column} TYPE {name} USING {column}::text::{name}"
        )
    op.execute(f"DROP TYPE {name}_old")


def upgrade() -> None:
    _replace_enum(
        "institutiontype",
        (
            "PRESIDENCY",
            "VICE_PRESIDENCY",
            "MINISTRY",
            "VICE_MINISTRY",
            "GENERAL_DIRECTORATE",
            "ATTACHED_AGENCY",
            "AUTONOMOUS_INSTITUTION",
            "DECENTRALIZED_INSTITUTION",
            "SUPERINTENDENCY",
            "COUNCIL",
            "COMMISSION",
            "INSTITUTE",
            "CABINET",
            "PUBLIC_COMPANY",
            "PROVINCIAL_GOVERNMENT",
            "TERRITORIAL_DEPENDENCY",
            "OTHER",
        ),
        (("institutions", "institution_type"),),
    )
    _replace_enum(
        "institutionrelationshiptype",
        ("HIERARCHICAL", "ATTACHED", "SUPERVISED", "COORDINATED", "TERRITORIAL", "DEPENDENT_ON"),
        (("institution_relationships", "relationship_type"),),
    )
    op.alter_column("institution_relationships", "valid_from", nullable=True)
    op.add_column("institution_relationships", sa.Column("notes", sa.Text(), nullable=True))
    op.drop_constraint(
        "ck_institution_relationship_valid_period", "institution_relationships", type_="check"
    )
    op.create_check_constraint(
        "ck_institution_relationship_valid_period",
        "institution_relationships",
        "valid_to IS NULL OR valid_from IS NULL OR valid_to >= valid_from",
    )
    op.create_check_constraint(
        "ck_institution_relationship_unknown_start_note",
        "institution_relationships",
        "valid_from IS NOT NULL OR length(trim(notes)) > 0",
    )
    op.drop_constraint(
        "uq_institution_relationship_period", "institution_relationships", type_="unique"
    )
    op.create_index(
        "uq_institution_relationship_period_known",
        "institution_relationships",
        ["parent_institution_id", "child_institution_id", "relationship_type", "valid_from"],
        unique=True,
        postgresql_where=sa.text("valid_from IS NOT NULL"),
    )
    op.create_index(
        "uq_institution_relationship_period_unknown",
        "institution_relationships",
        ["parent_institution_id", "child_institution_id", "relationship_type"],
        unique=True,
        postgresql_where=sa.text("valid_from IS NULL"),
    )
    op.create_table(
        "executive_dependency_load_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("manifest_version", sa.String(length=50), nullable=False),
        sa.Column("record_type", sa.String(length=40), nullable=False),
        sa.Column("record_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "manifest_version", "record_type", "record_id", name="uq_executive_dependency_record"
        ),
    )
    op.create_index(
        "ix_executive_dependency_record_lookup",
        "executive_dependency_load_records",
        ["manifest_version", "record_type"],
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
          IF EXISTS (SELECT 1 FROM institution_relationships WHERE valid_from IS NULL) THEN
            RAISE EXCEPTION 'Cannot downgrade 0013 while relationships with unknown start exist';
          END IF;
          IF EXISTS (SELECT 1 FROM institutions WHERE institution_type = 'INSTITUTE') THEN
            RAISE EXCEPTION 'Cannot downgrade 0013 while institute institutions exist';
          END IF;
          IF EXISTS (SELECT 1 FROM executive_dependency_load_records) THEN
            RAISE EXCEPTION 'Cannot downgrade 0013 while PE-03 ownership records exist';
          END IF;
        END $$
        """
    )
    op.drop_index(
        "ix_executive_dependency_record_lookup",
        table_name="executive_dependency_load_records",
    )
    op.drop_table("executive_dependency_load_records")
    op.drop_index(
        "uq_institution_relationship_period_unknown", table_name="institution_relationships"
    )
    op.drop_index(
        "uq_institution_relationship_period_known", table_name="institution_relationships"
    )
    op.create_unique_constraint(
        "uq_institution_relationship_period",
        "institution_relationships",
        ["parent_institution_id", "child_institution_id", "relationship_type", "valid_from"],
    )
    op.drop_constraint(
        "ck_institution_relationship_unknown_start_note", "institution_relationships", type_="check"
    )
    op.drop_constraint(
        "ck_institution_relationship_valid_period", "institution_relationships", type_="check"
    )
    op.create_check_constraint(
        "ck_institution_relationship_valid_period",
        "institution_relationships",
        "valid_to IS NULL OR valid_to >= valid_from",
    )
    op.drop_column("institution_relationships", "notes")
    op.alter_column("institution_relationships", "valid_from", nullable=False)
    _replace_enum(
        "institutionrelationshiptype",
        ("HIERARCHICAL", "ATTACHED", "SUPERVISED", "COORDINATED", "TERRITORIAL"),
        (("institution_relationships", "relationship_type"),),
    )
    _replace_enum(
        "institutiontype",
        (
            "PRESIDENCY",
            "VICE_PRESIDENCY",
            "MINISTRY",
            "VICE_MINISTRY",
            "GENERAL_DIRECTORATE",
            "ATTACHED_AGENCY",
            "AUTONOMOUS_INSTITUTION",
            "DECENTRALIZED_INSTITUTION",
            "SUPERINTENDENCY",
            "COUNCIL",
            "COMMISSION",
            "CABINET",
            "PUBLIC_COMPANY",
            "PROVINCIAL_GOVERNMENT",
            "TERRITORIAL_DEPENDENCY",
            "OTHER",
        ),
        (("institutions", "institution_type"),),
    )
