import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EvidenceCreate(BaseModel):
    source_id: uuid.UUID
    title: str
    excerpt: str
    locator: str
    content_hash: str
    metadata_: dict[str, object] = Field(default_factory=dict)


class EvidenceRead(EvidenceCreate):
    id: uuid.UUID
    observed_at: datetime
    model_config = ConfigDict(from_attributes=True)
