import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

CATEGORY_TYPES = {
    "real_estate",
    "land",
    "building",
    "infrastructure",
    "vehicle",
    "machinery",
    "technology",
    "furniture",
    "medical_equipment",
    "educational_equipment",
    "cultural_asset",
    "intangible",
    "biological_asset",
    "construction_in_progress",
    "leased_asset",
    "concession",
    "other",
}


class AssetCategoryCreate(BaseModel):
    stable_code: str = Field(min_length=1, max_length=100)
    official_name: str = Field(min_length=1, max_length=300)
    normalized_name: str = Field(min_length=1, max_length=300)
    description: str | None = None
    category_type: str
    parent_id: uuid.UUID | None = None
    depreciation_method: str | None = None
    default_useful_life_years: int | None = Field(None, ge=0)
    is_depreciable: bool = True
    status: str = "draft"
    valid_from: date
    valid_to: date | None = None
    source_id: uuid.UUID
    evidence_id: uuid.UUID
    metadata_: dict[str, object] = Field(default_factory=dict, alias="metadata")

    @model_validator(mode="after")
    def valid(self) -> "AssetCategoryCreate":
        if self.category_type not in CATEGORY_TYPES:
            raise ValueError("unsupported category_type")
        if self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("valid_to cannot precede valid_from")
        return self


class AssetCategoryRead(AssetCategoryCreate):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
