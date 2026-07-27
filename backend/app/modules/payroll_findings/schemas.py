import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.payroll_findings.models import FindingSeverity, FindingStatus


class PayrollFindingRead(BaseModel):
    id: uuid.UUID
    finding_type: str
    severity: FindingSeverity
    person_id: uuid.UUID | None
    institution_id: uuid.UUID
    payroll_period_id: uuid.UUID
    comparison_period_id: uuid.UUID | None
    observed_value: dict[str, object]
    expected_or_previous_value: dict[str, object]
    explanation: str
    evidence_id: uuid.UUID | None
    status: FindingStatus
    reviewer_notes: str | None
    metadata_: dict[str, object]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class FindingReview(BaseModel):
    status: FindingStatus
    reviewer_notes: str | None = Field(default=None, max_length=4000)
