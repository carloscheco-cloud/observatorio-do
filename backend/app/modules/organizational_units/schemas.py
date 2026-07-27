import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.organizational_units.models import (
    OrganizationalEventType,
    UnitStatus,
    UnitType,
)


class OrganizationalUnitCreate(BaseModel):
    institution_id: uuid.UUID
    parent_unit_id: uuid.UUID | None = None
    official_name: str = Field(min_length=1, max_length=300)
    normalized_name: str = Field(min_length=1, max_length=300)
    stable_code: str = Field(min_length=1, max_length=100)
    acronym: str | None = Field(default=None, max_length=50)
    description: str | None = None
    unit_type: UnitType
    hierarchy_level: int = Field(ge=0)
    order_index: int = Field(default=0, ge=0)
    is_headquarters: bool = False
    is_single_head: bool = True
    status: UnitStatus = UnitStatus.CANONICAL
    valid_from: date
    valid_to: date | None = None
    territory_id: uuid.UUID | None = None
    legal_basis_id: uuid.UUID | None
    evidence_id: uuid.UUID | None = None
    source_id: uuid.UUID | None = None
    metadata_: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_traceability_and_dates(self) -> "OrganizationalUnitCreate":
        if self.valid_to is not None and self.valid_to < self.valid_from:
            raise ValueError("valid_to must not precede valid_from")
        if self.status == UnitStatus.CANONICAL:
            missing = [
                name
                for name in ("legal_basis_id", "evidence_id", "source_id")
                if getattr(self, name) is None
            ]
            if missing:
                raise ValueError(f"Canonical unit requires: {', '.join(missing)}")
        return self


class OrganizationalUnitRead(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    parent_unit_id: uuid.UUID | None
    official_name: str
    normalized_name: str
    stable_code: str
    acronym: str | None
    description: str | None
    unit_type: UnitType
    hierarchy_level: int
    order_index: int
    is_headquarters: bool
    is_single_head: bool
    status: UnitStatus
    valid_from: date
    valid_to: date | None
    territory_id: uuid.UUID | None
    legal_basis_id: uuid.UUID | None
    metadata_: dict[str, object]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class OrganizationalChartNode(OrganizationalUnitRead):
    children: list["OrganizationalChartNode"] = Field(default_factory=list)


class OrganizationalEventCreate(BaseModel):
    institution_id: uuid.UUID
    unit_id: uuid.UUID
    event_type: OrganizationalEventType
    effective_date: date
    previous_parent_id: uuid.UUID | None = None
    new_parent_id: uuid.UUID | None = None
    previous_name: str | None = None
    new_name: str | None = None
    legal_basis_id: uuid.UUID
    evidence_id: uuid.UUID
    source_id: uuid.UUID
    description: str = Field(min_length=1)
    metadata_: dict[str, object] = Field(default_factory=dict)


class OrganizationalEventRead(OrganizationalEventCreate):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
