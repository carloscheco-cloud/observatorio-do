import uuid

from pydantic import BaseModel, ConfigDict

from app.modules.institutions.models import InstitutionStatus


class InstitutionCreate(BaseModel):
    name: str
    kind: str
    territory_id: uuid.UUID
    evidence_id: uuid.UUID


class InstitutionRead(BaseModel):
    id: uuid.UUID
    name: str
    kind: str
    territory_id: uuid.UUID
    status: InstitutionStatus
    model_config = ConfigDict(from_attributes=True)
