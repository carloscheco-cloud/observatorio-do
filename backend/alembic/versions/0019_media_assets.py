"""Add traced media assets for PE-09.

Revision ID: 0019
Revises: 0018
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0019"
down_revision: str | None = "0018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "media_assets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=True),
        sa.Column("person_id", sa.Uuid(), nullable=True),
        sa.Column("asset_type", sa.String(length=40), nullable=False),
        sa.Column("storage_kind", sa.String(length=40), nullable=False),
        sa.Column("source_url", sa.String(length=2048), nullable=True),
        sa.Column("public_url", sa.String(length=2048), nullable=True),
        sa.Column("storage_key", sa.String(length=1024), nullable=True),
        sa.Column("source_name", sa.String(length=300), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "approval_status",
            sa.String(length=30),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("alt_text", sa.String(length=500), nullable=False),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("license_note", sa.Text(), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("checksum", sa.String(length=64), nullable=True),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("approved_by", sa.String(length=200), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("supersedes_asset_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "asset_type IN ("
            "'institution_building','authority_portrait','institution_logo',"
            "'official_banner','fallback'"
            ")",
            name="ck_media_assets_asset_type",
        ),
        sa.CheckConstraint(
            "storage_kind IN ('remote_official','managed','cached','generated_fallback')",
            name="ck_media_assets_storage_kind",
        ),
        sa.CheckConstraint(
            "approval_status IN ('pending','approved','rejected','archived')",
            name="ck_media_assets_approval_status",
        ),
        sa.CheckConstraint(
            "institution_id IS NOT NULL OR person_id IS NOT NULL OR asset_type = 'fallback'",
            name="ck_media_assets_has_owner_or_fallback",
        ),
        sa.CheckConstraint(
            "NOT (institution_id IS NOT NULL AND person_id IS NOT NULL)",
            name="ck_media_assets_single_owner",
        ),
        sa.CheckConstraint(
            "source_url IS NOT NULL OR storage_kind = 'generated_fallback'",
            name="ck_media_assets_source_or_generated_fallback",
        ),
        sa.CheckConstraint("width IS NULL OR width > 0", name="ck_media_assets_width_positive"),
        sa.CheckConstraint(
            "height IS NULL OR height > 0",
            name="ck_media_assets_height_positive",
        ),
        sa.ForeignKeyConstraint(
            ["institution_id"],
            ["institutions.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["supersedes_asset_id"],
            ["media_assets.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key", name="uq_media_assets_storage_key"),
        sa.UniqueConstraint(
            "institution_id",
            "person_id",
            "asset_type",
            "source_url",
            name="uq_media_assets_owner_type_source",
        ),
    )
    op.create_index("ix_media_assets_institution_id", "media_assets", ["institution_id"])
    op.create_index("ix_media_assets_person_id", "media_assets", ["person_id"])
    op.create_index("ix_media_assets_checksum", "media_assets", ["checksum"])
    op.create_index(
        "ix_media_assets_approval_type",
        "media_assets",
        ["approval_status", "asset_type"],
    )
    op.create_index(
        "uq_media_assets_primary_institution_type",
        "media_assets",
        ["institution_id", "asset_type"],
        unique=True,
        postgresql_where=sa.text(
            "is_primary AND institution_id IS NOT NULL AND approval_status = 'approved'"
        ),
    )
    op.create_index(
        "uq_media_assets_primary_person_type",
        "media_assets",
        ["person_id", "asset_type"],
        unique=True,
        postgresql_where=sa.text(
            "is_primary AND person_id IS NOT NULL AND approval_status = 'approved'"
        ),
    )
    op.alter_column("media_assets", "approval_status", server_default=None)
    op.alter_column("media_assets", "is_primary", server_default=None)


def downgrade() -> None:
    op.drop_index("uq_media_assets_primary_person_type", table_name="media_assets")
    op.drop_index("uq_media_assets_primary_institution_type", table_name="media_assets")
    op.drop_index("ix_media_assets_approval_type", table_name="media_assets")
    op.drop_index("ix_media_assets_checksum", table_name="media_assets")
    op.drop_index("ix_media_assets_person_id", table_name="media_assets")
    op.drop_index("ix_media_assets_institution_id", table_name="media_assets")
    op.drop_table("media_assets")
