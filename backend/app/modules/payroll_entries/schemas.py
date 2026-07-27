import re
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.payroll_entries.models import ComponentKind, PayrollEntryStatus

SENSITIVE_ID = re.compile(r"(?<!\d)\d{3}-?\d{7}-?\d(?!\d)")


class PayrollEntryCreate(BaseModel):
    employment_relationship_id: uuid.UUID | None = None
    person_id: uuid.UUID
    institution_id: uuid.UUID
    position_id: uuid.UUID | None = None
    organizational_unit_id: uuid.UUID | None = None
    employee_reference_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    listed_name: str
    normalized_name: str
    employment_type: str | None = None
    base_salary: Decimal = Field(ge=0)
    gross_income: Decimal = Field(ge=0)
    total_deductions: Decimal = Field(ge=0)
    net_income: Decimal = Field(ge=0)
    other_compensation: Decimal = Field(default=Decimal("0"), ge=0)
    currency: str = Field(default="DOP", min_length=3, max_length=3)
    status: PayrollEntryStatus = PayrollEntryStatus.DRAFT
    source_id: uuid.UUID | None = None
    evidence_id: uuid.UUID | None = None
    row_number: int | None = Field(default=None, ge=1)
    raw_payload: dict[str, object] = Field(default_factory=dict)
    metadata_: dict[str, object] = Field(default_factory=dict)

    @field_validator("listed_name", "normalized_name")
    @classmethod
    def no_sensitive_identifier(cls, value: str) -> str:
        if SENSITIVE_ID.search(value):
            raise ValueError("Apparent national identifier is prohibited")
        return value

    @model_validator(mode="after")
    def traceability(self) -> "PayrollEntryCreate":
        if self.status == PayrollEntryStatus.CONFIRMED and (
            self.source_id is None or self.evidence_id is None
        ):
            raise ValueError("Confirmed entry requires source and evidence")
        return self


class PayrollEntryRead(BaseModel):
    id: uuid.UUID
    payroll_period_id: uuid.UUID
    employment_relationship_id: uuid.UUID | None
    person_id: uuid.UUID
    institution_id: uuid.UUID
    position_id: uuid.UUID | None
    organizational_unit_id: uuid.UUID | None
    employee_reference_hash: str | None
    listed_name: str
    normalized_name: str
    employment_type: str | None
    base_salary: Decimal
    gross_income: Decimal
    total_deductions: Decimal
    net_income: Decimal
    other_compensation: Decimal
    currency: str
    status: PayrollEntryStatus
    source_id: uuid.UUID | None
    evidence_id: uuid.UUID | None
    row_number: int | None
    reconciliation_flag: bool
    processed_at: datetime
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PayrollComponentCreate(BaseModel):
    concept_id: uuid.UUID
    kind: ComponentKind
    amount: Decimal = Field(ge=0)
    currency: str = Field(default="DOP", min_length=3, max_length=3)
    description: str | None = None
    source_id: uuid.UUID
    evidence_id: uuid.UUID
    metadata_: dict[str, object] = Field(default_factory=dict)
