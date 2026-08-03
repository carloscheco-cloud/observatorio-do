import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.modules.institutions.models import (
    CoverageLevel,
    InstitutionStatus,
    InstitutionType,
    OperationalStatus,
    StateBranch,
)


class InstitutionCreate(BaseModel):
    name: str = Field(min_length=2, max_length=300)
    kind: str = Field(min_length=2, max_length=100)
    territory_id: uuid.UUID
    evidence_id: uuid.UUID
    acronym: str | None = Field(default=None, max_length=40)
    slug: str | None = Field(default=None, min_length=2, max_length=320, pattern=r"^[a-z0-9-]+$")
    state_branch: StateBranch | None = None
    institution_type: InstitutionType | None = None
    operational_status: OperationalStatus = OperationalStatus.UNKNOWN
    coverage_level: CoverageLevel = CoverageLevel.NONE
    official_website: HttpUrl | None = None
    functions_summary: str | None = Field(default=None, max_length=5000)
    creation_date: date | None = None
    last_reviewed_at: datetime | None = None


class InstitutionRead(BaseModel):
    id: uuid.UUID
    name: str
    kind: str
    acronym: str | None
    slug: str | None
    state_branch: StateBranch | None
    institution_type: InstitutionType | None
    operational_status: OperationalStatus
    coverage_level: CoverageLevel
    official_website: str | None
    functions_summary: str | None
    creation_date: date | None
    last_reviewed_at: datetime | None
    territory_id: uuid.UUID
    status: InstitutionStatus
    model_config = ConfigDict(from_attributes=True)
