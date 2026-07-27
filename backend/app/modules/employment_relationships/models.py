import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base


class EmploymentType(StrEnum):
    PERMANENT = "permanent"
    CAREER = "career"
    APPOINTED = "appointed"
    ELECTED = "elected"
    TEMPORARY = "temporary"
    FIXED_TERM = "fixed_term"
    CONTRACTOR = "contractor"
    CONSULTANT = "consultant"
    MILITARY = "military"
    POLICE = "police"
    TEACHER = "teacher"
    HEALTH_WORKER = "health_worker"
    INTERN = "intern"
    HONORARY = "honorary"
    OTHER = "other"


class RelationshipStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ENDED = "ended"
    CANCELLED = "cancelled"
    UNDER_REVIEW = "under_review"


class EmploymentRelationship(Base):
    __tablename__ = "employment_relationships"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    person_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("persons.id"), nullable=False)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"), nullable=False)
    position_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("positions.id"))
    organizational_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_units.id")
    )
    employment_type: Mapped[EmploymentType] = mapped_column(Enum(EmploymentType), nullable=False)
    relationship_status: Mapped[RelationshipStatus] = mapped_column(
        Enum(RelationshipStatus), nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    contract_reference: Mapped[str | None] = mapped_column(String(300))
    work_location: Mapped[str | None] = mapped_column(Text)
    territory_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("territories.id"))
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"), nullable=False)
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"), nullable=False)
    legal_basis_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("legal_bases.id"))
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON().with_variant(JSONB(), "postgresql"), default=dict, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
