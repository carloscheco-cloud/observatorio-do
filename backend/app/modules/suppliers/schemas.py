import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.suppliers.models import SupplierType


class SupplierCreate(BaseModel):
    legal_name: str = Field(min_length=1, max_length=300)
    normalized_name: str = Field(min_length=1, max_length=300)
    trade_name: str | None = None
    supplier_type: SupplierType
    registry_reference_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    country: str = Field(default="DO", pattern=r"^[A-Z]{2}$")
    territory_id: uuid.UUID | None = None
    registration_status: str = "confirmed"
    registration_date: date | None = None
    economic_activity: str | None = None
    is_public_entity: bool = False
    is_nonprofit: bool = False
    source_id: uuid.UUID
    evidence_id: uuid.UUID
    metadata_: dict[str, object] = Field(default_factory=dict)

    @field_validator("normalized_name")
    @classmethod
    def normalized(cls, value: str) -> str:
        if value != value.strip().casefold():
            raise ValueError("normalized_name must be trimmed and case-folded")
        return value


class SupplierRead(SupplierCreate):
    id: uuid.UUID
    actor_type: str
    validation_status: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SupplierHistoryRead(BaseModel):
    id: uuid.UUID
    supplier_id: uuid.UUID
    legal_name: str
    normalized_name: str
    registration_status: str
    effective_date: date
    reason: str
    source_id: uuid.UUID
    evidence_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
