import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.appointments.models import AppointmentStatus


class AppointmentCreate(BaseModel):
    person_id: uuid.UUID | None = None
    position_id: uuid.UUID | None = None
    institution_id: uuid.UUID | None = None
    start_date: date | None = None
    end_date: date | None = None
    appointment_type: str = Field(min_length=1, max_length=100)
    status: AppointmentStatus = AppointmentStatus.PENDING
    legal_act: str | None = Field(default=None, max_length=500)
    evidence_id: uuid.UUID | None = None
    source_id: uuid.UUID | None = None
    metadata_: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def valid_chronology(self) -> "AppointmentCreate":
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must not precede start_date")
        return self


class AppointmentRead(AppointmentCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
