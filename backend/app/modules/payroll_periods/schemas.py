import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.payroll_periods.models import PayrollPeriodStatus


class PayrollPeriodCreate(BaseModel):
    institution_id: uuid.UUID
    year: int = Field(ge=1900, le=2200)
    month: int = Field(ge=1, le=12)
    period_start: date
    period_end: date
    publication_date: date | None = None
    status: PayrollPeriodStatus = PayrollPeriodStatus.DRAFT
    currency: str = Field(default="DOP", min_length=3, max_length=3)
    source_id: uuid.UUID | None = None
    evidence_id: uuid.UUID | None = None
    record_count: int = Field(default=0, ge=0)
    reported_gross_total: Decimal | None = Field(default=None, ge=0)
    calculated_gross_total: Decimal = Field(default=Decimal("0"), ge=0)
    calculated_net_total: Decimal = Field(default=Decimal("0"), ge=0)
    checksum: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    version: int = Field(default=1, ge=1)
    metadata_: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_period(self) -> "PayrollPeriodCreate":
        if self.period_end < self.period_start:
            raise ValueError("period_end must not precede period_start")
        if self.status == PayrollPeriodStatus.CONFIRMED and (
            self.source_id is None or self.evidence_id is None
        ):
            raise ValueError("Confirmed payroll requires source and evidence")
        return self


class PayrollPeriodRead(PayrollPeriodCreate):
    id: uuid.UUID
    processed_at: datetime
    actor_type: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PayrollSummary(BaseModel):
    period_id: uuid.UUID
    people: int
    gross_total: Decimal
    deductions_total: Decimal
    net_total: Decimal
    other_compensation_total: Decimal
    average_gross: Decimal
    minimum_gross: Decimal
    maximum_gross: Decimal
