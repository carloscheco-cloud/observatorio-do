"""Extend institutions for the Poder Ejecutivo domain.

Revision ID: 0012
Revises: 0011
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0012"
down_revision: str | None = "0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

state_branch = postgresql.ENUM(
    "EXECUTIVE",
    "LEGISLATIVE",
    "JUDICIAL",
    "CONSTITUTIONAL",
    "OTHER",
    name="statebranch",
    create_type=False,
)
institution_type = postgresql.ENUM(
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
    name="institutiontype",
    create_type=False,
)
operational_status = postgresql.ENUM(
    "ACTIVE",
    "INACTIVE",
    "IN_REORGANIZATION",
    "MERGED",
    "DISSOLVED",
    "UNKNOWN",
    name="operationalstatus",
    create_type=False,
)
coverage_level = postgresql.ENUM(
    "NONE",
    "BASIC",
    "PARTIAL",
    "SUBSTANTIAL",
    "COMPLETE",
    name="coveragelevel",
    create_type=False,
)
relationship_type = postgresql.ENUM(
    "HIERARCHICAL",
    "ATTACHED",
    "SUPERVISED",
    "COORDINATED",
    "TERRITORIAL",
    name="institutionrelationshiptype",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    state_branch.create(bind, checkfirst=True)
    institution_type.create(bind, checkfirst=True)
    operational_status.create(bind, checkfirst=True)
    coverage_level.create(bind, checkfirst=True)
    relationship_type.create(bind, checkfirst=True)

    op.add_column("institutions", sa.Column("acronym", sa.String(length=40), nullable=True))
    op.add_column("institutions", sa.Column("slug", sa.String(length=320), nullable=True))
    op.add_column("institutions", sa.Column("state_branch", state_branch, nullable=True))
    op.add_column("institutions", sa.Column("institution_type", institution_type, nullable=True))
    op.add_column(
        "institutions",
        sa.Column(
            "operational_status", operational_status, nullable=False, server_default="UNKNOWN"
        ),
    )
    op.add_column(
        "institutions",
        sa.Column("coverage_level", coverage_level, nullable=False, server_default="NONE"),
    )
    op.add_column(
        "institutions", sa.Column("official_website", sa.String(length=500), nullable=True)
    )
    op.add_column("institutions", sa.Column("functions_summary", sa.Text(), nullable=True))
    op.add_column("institutions", sa.Column("creation_date", sa.Date(), nullable=True))
    op.add_column(
        "institutions", sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.create_unique_constraint("uq_institutions_slug", "institutions", ["slug"])

    op.create_table(
        "institution_relationships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("parent_institution_id", sa.Uuid(), nullable=False),
        sa.Column("child_institution_id", sa.Uuid(), nullable=False),
        sa.Column("relationship_type", relationship_type, nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("evidence_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "parent_institution_id <> child_institution_id",
            name="ck_institution_relationship_not_self",
        ),
        sa.CheckConstraint(
            "valid_to IS NULL OR valid_to >= valid_from",
            name="ck_institution_relationship_valid_period",
        ),
        sa.ForeignKeyConstraint(
            ["parent_institution_id"], ["institutions.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["child_institution_id"], ["institutions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["evidence_id"], ["evidence.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "parent_institution_id",
            "child_institution_id",
            "relationship_type",
            "valid_from",
            name="uq_institution_relationship_period",
        ),
    )
    op.create_index(
        "ix_institution_relationships_parent_institution_id",
        "institution_relationships",
        ["parent_institution_id"],
    )
    op.create_index(
        "ix_institution_relationships_child_institution_id",
        "institution_relationships",
        ["child_institution_id"],
    )

    op.alter_column("institutions", "operational_status", server_default=None)
    op.alter_column("institutions", "coverage_level", server_default=None)


def downgrade() -> None:
    op.drop_index(
        "ix_institution_relationships_child_institution_id",
        table_name="institution_relationships",
    )
    op.drop_index(
        "ix_institution_relationships_parent_institution_id",
        table_name="institution_relationships",
    )
    op.drop_table("institution_relationships")
    op.drop_constraint("uq_institutions_slug", "institutions", type_="unique")
    for column in (
        "last_reviewed_at",
        "creation_date",
        "functions_summary",
        "official_website",
        "coverage_level",
        "operational_status",
        "institution_type",
        "state_branch",
        "slug",
        "acronym",
    ):
        op.drop_column("institutions", column)

    bind = op.get_bind()
    relationship_type.drop(bind, checkfirst=True)
    coverage_level.drop(bind, checkfirst=True)
    operational_status.drop(bind, checkfirst=True)
    institution_type.drop(bind, checkfirst=True)
    state_branch.drop(bind, checkfirst=True)
