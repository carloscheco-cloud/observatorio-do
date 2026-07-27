import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CreditorType = Literal[
    "multilateral",
    "bilateral",
    "commercial_bank",
    "investment_fund",
    "bondholder_group",
    "supplier",
    "public_entity",
    "central_bank",
    "pension_fund",
    "individual",
    "other",
]


class CreditorCreate(BaseModel):
    legal_name: str = Field(min_length=1, max_length=400)
    normalized_name: str = Field(min_length=1, max_length=400)
    creditor_type: CreditorType
    country: str | None = Field(default=None, pattern=r"^[A-Z]{2}$")
    territory_id: uuid.UUID | None = None
    is_domestic: bool
    is_public_entity: bool
    registry_reference_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    status: str = "active"
    source_id: uuid.UUID
    evidence_id: uuid.UUID
    metadata_: dict[str, object] = Field(default_factory=dict)


class CreditorRead(CreditorCreate):
    id: uuid.UUID
    actor_type: str
    validation_status: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CreditorExposure(BaseModel):
    creditor_id: uuid.UUID
    principal_outstanding: str
    guarantee_exposure: str
    potential_duplicates: list[uuid.UUID]
