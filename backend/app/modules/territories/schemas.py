import uuid

from pydantic import BaseModel, ConfigDict

from app.modules.territories.models import TerritoryType


class TerritoryCreate(BaseModel):
    name: str
    code: str
    type: TerritoryType
    parent_id: uuid.UUID | None = None


class TerritoryRead(TerritoryCreate):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
