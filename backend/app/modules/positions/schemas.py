import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.positions.models import AccessMethod, PositionStatus


class PositionCreate(BaseModel):
    institution_id: uuid.UUID
    organizational_unit_id: uuid.UUID | None = None
    official_name: str = Field(min_length=1, max_length=300)
    code: str = Field(min_length=1, max_length=100)
    description: str | None = None
    position_type: str = Field(min_length=1, max_length=100)
    hierarchy_level: str = Field(min_length=1, max_length=100)
    access_method: AccessMethod
    legal_basis_id: uuid.UUID
    status: PositionStatus = PositionStatus.CANONICAL
    valid_from: date | None = None
    valid_to: date | None = None
    single_occupant: bool = True
    metadata_: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def dates_are_ordered(self) -> "PositionCreate":
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("valid_to must not precede valid_from")
        return self


class PositionRead(PositionCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
