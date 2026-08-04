"""Add historical digital transparency assessments.

Revision ID: 0015
Revises: 0014
"""

from collections.abc import Sequence

from alembic import op
from app.modules.digital_transparency.models import (
    AssessmentComponent,
    DigitalTransparencyLoadRecord,
    DocumentRequirement,
    DocumentResource,
    InformationRequest,
    ManualResearchTask,
    TransparencyAssessment,
    TransparencyObservation,
)

revision: str = "0015"
down_revision: str | None = "0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLES = (
    DocumentRequirement.__table__,
    DocumentResource.__table__,
    TransparencyObservation.__table__,
    ManualResearchTask.__table__,
    InformationRequest.__table__,
    TransparencyAssessment.__table__,
    AssessmentComponent.__table__,
    DigitalTransparencyLoadRecord.__table__,
)


def upgrade() -> None:
    bind = op.get_bind()
    for table in TABLES:
        table.create(bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.execute(DigitalTransparencyLoadRecord.__table__.select().limit(1)).first():
        raise RuntimeError("Rollback PE-05 data before downgrade 0015")
    for table in reversed(TABLES):
        op.drop_table(table.name)
    for name in (
        "informationrequeststatus",
        "researchtaskstatus",
        "confidencelevel",
        "reviewertype",
        "verificationstatus",
    ):
        op.execute(f"DROP TYPE IF EXISTS {name}")
