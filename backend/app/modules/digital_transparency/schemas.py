from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.modules.digital_transparency.models import (
    InformationRequestStatus,
    ResourceCheckStatus,
    ResourceCheckType,
    SearchabilityMethod,
    SearchabilityResult,
    VerificationStatus,
)


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class InformationRequestCreate(BaseModel):
    institution_id: str
    subject: str
    status: InformationRequestStatus = InformationRequestStatus.DRAFT
    submitted_at: datetime | None = None
    tracking_code: str | None = None

    @model_validator(mode="after")
    def submitted_states_require_submission(self) -> "InformationRequestCreate":
        if self.status != InformationRequestStatus.DRAFT and self.submitted_at is None:
            raise ValueError("a non-draft information request requires submitted_at")
        if self.status == InformationRequestStatus.DRAFT and self.tracking_code is not None:
            raise ValueError("a draft request cannot have a tracking code")
        return self


def is_definitive_broken_link(
    statuses: list[VerificationStatus], http_statuses: list[int | None]
) -> bool:
    """A repeated failure or unequivocal HTTP response is needed; a timeout is unavailable."""
    if any(code in {404, 410} for code in http_statuses):
        return True
    return statuses.count(VerificationStatus.BROKEN_LINK) >= 2


class ResourceCheckCreate(BaseModel):
    resource_id: str
    checked_at: datetime
    check_type: ResourceCheckType
    status: ResourceCheckStatus
    http_status: int | None = None
    final_url: str | None = None
    redirect_count: int | None = None
    response_time_ms: int | None = None
    mime_type: str | None = None
    content_length: int | None = None
    error_type: str | None = None
    error_message: str | None = None
    attempt_number: int
    user_agent: str
    timeout_seconds: int
    tool_name: str
    tool_version: str
    evidence_id: str | None = None
    notes: str | None = None


class SearchabilityCheckCreate(BaseModel):
    resource_id: str
    checked_at: datetime
    method: SearchabilityMethod
    result: SearchabilityResult
    text_detected: bool | None = None
    selectable_text: bool | None = None
    metadata_detected: bool | None = None
    title_detected: bool | None = None
    publication_date_detected: bool | None = None
    document_number_detected: bool | None = None
    page_count: int | None = None
    extracted_character_count: int | None = None
    tool_name: str
    tool_version: str
    evidence_id: str | None = None
    notes: str | None = None
