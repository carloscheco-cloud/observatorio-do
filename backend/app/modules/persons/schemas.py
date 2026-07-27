import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.persons.models import PersonStatus


class PersonCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=300)
    national_id_hash: str | None = Field(default=None, min_length=64, max_length=64)
    birth_date: date | None = None
    nationality: str | None = Field(default=None, max_length=100)
    status: PersonStatus = PersonStatus.DRAFT
    metadata_: dict[str, object] = Field(default_factory=dict)

    @field_validator("national_id_hash")
    @classmethod
    def validate_hash(cls, value: str | None) -> str | None:
        if value is not None and any(
            character not in "0123456789abcdefABCDEF" for character in value
        ):
            raise ValueError("national_id_hash must be a SHA-256 hexadecimal digest")
        return value.lower() if value else None


class PersonRead(BaseModel):
    id: uuid.UUID
    full_name: str
    normalized_name: str
    national_id_hash: str | None
    birth_date: date | None
    nationality: str | None
    status: PersonStatus
    metadata_: dict[str, object]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
