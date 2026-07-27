import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class SourceCreate(BaseModel):
    name: str
    url: HttpUrl
    publisher: str
    is_official: bool = False


class SourceRead(BaseModel):
    id: uuid.UUID
    name: str
    url: str
    publisher: str
    is_official: bool
    retrieved_at: datetime
    model_config = ConfigDict(from_attributes=True)
