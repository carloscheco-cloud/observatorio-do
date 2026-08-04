"""Add immutable technical transparency check history.

Revision ID: 0016
Revises: 0015
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0016"
down_revision: str | None = "0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RESOURCE_CHECK_TYPE = postgresql.ENUM(
    "HTTP_AVAILABILITY",
    "REDIRECT_RESOLUTION",
    "CONTENT_METADATA",
    name="resourcechecktype",
    create_type=False,
)
RESOURCE_CHECK_STATUS = postgresql.ENUM(
    "AVAILABLE",
    "AVAILABLE_WITH_REDIRECT",
    "RESTRICTED",
    "RATE_LIMITED",
    "SOURCE_UNAVAILABLE",
    "NOT_FOUND_PROVISIONAL",
    "BROKEN_LINK_CONFIRMED",
    "TECHNICAL_ERROR",
    name="resourcecheckstatus",
    create_type=False,
)
SEARCHABILITY_METHOD = postgresql.ENUM(
    "HTML_TEXT_INSPECTION",
    "PDF_TEXT_EXTRACTION",
    "METADATA_INSPECTION",
    "MANUAL_REVIEW",
    name="searchabilitymethod",
    create_type=False,
)
SEARCHABILITY_RESULT = postgresql.ENUM(
    "SEARCHABLE",
    "PARTIALLY_SEARCHABLE",
    "NOT_SEARCHABLE",
    "INCONCLUSIVE",
    "TECHNICAL_ERROR",
    name="searchabilityresult",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    for enum in (
        RESOURCE_CHECK_TYPE,
        RESOURCE_CHECK_STATUS,
        SEARCHABILITY_METHOD,
        SEARCHABILITY_RESULT,
    ):
        enum.create(bind, checkfirst=True)
    op.create_table(
        "transparency_resource_checks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("resource_id", sa.Uuid(), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("check_type", RESOURCE_CHECK_TYPE, nullable=False),
        sa.Column("status", RESOURCE_CHECK_STATUS, nullable=False),
        sa.Column("http_status", sa.Integer()),
        sa.Column("final_url", sa.String(1000)),
        sa.Column("redirect_count", sa.Integer()),
        sa.Column("response_time_ms", sa.Integer()),
        sa.Column("mime_type", sa.String(150)),
        sa.Column("content_length", sa.Integer()),
        sa.Column("error_type", sa.String(80)),
        sa.Column("error_message", sa.Text()),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("user_agent", sa.String(300), nullable=False),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False),
        sa.Column("tool_name", sa.String(100), nullable=False),
        sa.Column("tool_version", sa.String(100), nullable=False),
        sa.Column("evidence_id", sa.Uuid()),
        sa.Column("notes", sa.Text()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("attempt_number >= 1"),
        sa.CheckConstraint("timeout_seconds > 0"),
        sa.CheckConstraint("redirect_count IS NULL OR redirect_count >= 0"),
        sa.CheckConstraint("response_time_ms IS NULL OR response_time_ms >= 0"),
        sa.CheckConstraint("content_length IS NULL OR content_length >= 0"),
        sa.CheckConstraint("http_status IS NULL OR (http_status >= 100 AND http_status <= 599)"),
        sa.CheckConstraint("final_url IS NULL OR http_status IS NOT NULL"),
        sa.CheckConstraint("status != 'RESTRICTED' OR http_status = 403"),
        sa.CheckConstraint("status != 'RATE_LIMITED' OR http_status = 429"),
        sa.CheckConstraint("status != 'NOT_FOUND_PROVISIONAL' OR http_status = 404"),
        sa.CheckConstraint("status != 'BROKEN_LINK_CONFIRMED' OR http_status IN (404, 410)"),
        sa.ForeignKeyConstraint(["resource_id"], ["document_resources.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["evidence_id"], ["evidence.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("resource_id", "checked_at", "check_type", "attempt_number"),
    )
    op.create_index(
        "ix_transparency_resource_checks_resource_checked",
        "transparency_resource_checks",
        ["resource_id", "checked_at"],
    )
    op.create_index(
        "ix_transparency_resource_checks_status", "transparency_resource_checks", ["status"]
    )
    op.create_table(
        "transparency_searchability_checks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("resource_id", sa.Uuid(), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("method", SEARCHABILITY_METHOD, nullable=False),
        sa.Column("result", SEARCHABILITY_RESULT, nullable=False),
        sa.Column("text_detected", sa.Boolean()),
        sa.Column("selectable_text", sa.Boolean()),
        sa.Column("metadata_detected", sa.Boolean()),
        sa.Column("title_detected", sa.Boolean()),
        sa.Column("publication_date_detected", sa.Boolean()),
        sa.Column("document_number_detected", sa.Boolean()),
        sa.Column("page_count", sa.Integer()),
        sa.Column("extracted_character_count", sa.Integer()),
        sa.Column("tool_name", sa.String(100), nullable=False),
        sa.Column("tool_version", sa.String(100), nullable=False),
        sa.Column("evidence_id", sa.Uuid()),
        sa.Column("notes", sa.Text()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("page_count IS NULL OR page_count >= 0"),
        sa.CheckConstraint("extracted_character_count IS NULL OR extracted_character_count >= 0"),
        sa.CheckConstraint("selectable_text IS NOT TRUE OR text_detected IS TRUE"),
        sa.CheckConstraint("result != 'SEARCHABLE' OR text_detected IS TRUE"),
        sa.ForeignKeyConstraint(["resource_id"], ["document_resources.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["evidence_id"], ["evidence.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_transparency_searchability_checks_resource_checked",
        "transparency_searchability_checks",
        ["resource_id", "checked_at"],
    )
    op.create_index(
        "ix_transparency_searchability_checks_result",
        "transparency_searchability_checks",
        ["result"],
    )
    op.execute(
        """
        CREATE FUNCTION transparency_check_history_immutable() RETURNS trigger AS $$
        BEGIN
          IF TG_OP = 'DELETE' AND EXISTS (
            SELECT 1 FROM digital_transparency_load_records
            WHERE manifest_version = 'PE-06A-2026-08-03'
              AND record_id = OLD.id
              AND record_type IN ('resource_check', 'searchability_check')
          ) THEN
            RETURN OLD;
          END IF;
          RAISE EXCEPTION 'Technical check history is immutable';
        END;
        $$ LANGUAGE plpgsql;
        CREATE TRIGGER trg_resource_checks_immutable
          BEFORE UPDATE OR DELETE ON transparency_resource_checks
          FOR EACH ROW EXECUTE FUNCTION transparency_check_history_immutable();
        CREATE TRIGGER trg_searchability_checks_immutable
          BEFORE UPDATE OR DELETE ON transparency_searchability_checks
          FOR EACH ROW EXECUTE FUNCTION transparency_check_history_immutable();
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_searchability_checks_immutable "
        "ON transparency_searchability_checks"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS trg_resource_checks_immutable ON transparency_resource_checks"
    )
    op.execute("DROP FUNCTION IF EXISTS transparency_check_history_immutable()")
    op.drop_table("transparency_searchability_checks")
    op.drop_table("transparency_resource_checks")
    bind = op.get_bind()
    for enum in (
        SEARCHABILITY_RESULT,
        SEARCHABILITY_METHOD,
        RESOURCE_CHECK_STATUS,
        RESOURCE_CHECK_TYPE,
    ):
        enum.drop(bind, checkfirst=True)
