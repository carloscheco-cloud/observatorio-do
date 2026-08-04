from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.modules.digital_transparency.models import InformationRequestStatus, VerificationStatus


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
