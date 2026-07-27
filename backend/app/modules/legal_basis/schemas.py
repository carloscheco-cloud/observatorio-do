import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.legal_basis.models import LegalInstrumentType


class LegalBasisCreate(BaseModel):
    instrument_type: LegalInstrumentType
    title: str = Field(min_length=1, max_length=500)
    reference: str = Field(min_length=1, max_length=300)
    article: str | None = Field(default=None, max_length=100)
    official_url: str | None = Field(default=None, max_length=1000)
    evidence_id: uuid.UUID
    effective_from: date | None = None
    effective_to: date | None = None
    issuing_body: str = Field(min_length=1, max_length=300)
    description: str | None = None
    metadata_: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def dates_are_ordered(self) -> "LegalBasisCreate":
        if self.effective_from and self.effective_to and self.effective_to < self.effective_from:
            raise ValueError("effective_to must not precede effective_from")
        return self


class LegalBasisRead(LegalBasisCreate):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
