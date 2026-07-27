import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.employment_relationships.models import EmploymentType, RelationshipStatus


class EmploymentRelationshipCreate(BaseModel):
    person_id: uuid.UUID
    institution_id: uuid.UUID
    position_id: uuid.UUID | None = None
    organizational_unit_id: uuid.UUID | None = None
    employment_type: EmploymentType
    relationship_status: RelationshipStatus = RelationshipStatus.PENDING
    start_date: date
    end_date: date | None = None
    contract_reference: str | None = Field(default=None, max_length=300)
    work_location: str | None = None
    territory_id: uuid.UUID | None = None
    source_id: uuid.UUID
    evidence_id: uuid.UUID
    legal_basis_id: uuid.UUID | None = None
    metadata_: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def chronology(self) -> "EmploymentRelationshipCreate":
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date must not precede start_date")
        return self


class EmploymentRelationshipRead(EmploymentRelationshipCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
