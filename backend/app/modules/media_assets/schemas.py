from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class PublicMediaAsset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    asset_type: Literal[
        "institution_building",
        "authority_portrait",
        "institution_logo",
        "official_banner",
        "fallback",
    ]
    public_url: str
    source_url: str | None
    source_name: str
    verified_at: datetime | None
    is_primary: bool
    alt_text: str
    caption: str | None
    license_note: str | None
    width: int | None
    height: int | None


class PublicMediaCollection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[PublicMediaAsset]
    fallback_required: bool
    limitation: str
