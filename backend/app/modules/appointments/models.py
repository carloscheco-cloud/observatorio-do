import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base


class AppointmentStatus(StrEnum):
    ANNOUNCED = "announced"
    PENDING_START = "pending_start"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    ENDED = "ended"
    REVOKED = "revoked"
    DISPUTED = "disputed"


class AppointmentCapacity(StrEnum):
    SUBSTANTIVE = "substantive"
    ACTING = "acting"
    TEMPORARY = "temporary"
    DELEGATED = "delegated"


class AppointmentMechanism(StrEnum):
    CONSTITUTIONAL_ELECTION = "constitutional_election"
    PRESIDENTIAL_DECREE = "presidential_decree"
    LEGAL_DESIGNATION = "legal_designation"
    EX_OFFICIO = "ex_officio"


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    person_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("persons.id", ondelete="RESTRICT")
    )
    position_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("positions.id", ondelete="RESTRICT")
    )
    institution_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("institutions.id", ondelete="RESTRICT")
    )
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    appointment_type: Mapped[str] = mapped_column(String(100), nullable=False)
    capacity: Mapped[AppointmentCapacity | None] = mapped_column(Enum(AppointmentCapacity))
    mechanism: Mapped[AppointmentMechanism | None] = mapped_column(Enum(AppointmentMechanism))
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus), default=AppointmentStatus.PENDING, nullable=False
    )
    legal_act: Mapped[str | None] = mapped_column(String(500))
    decree_number: Mapped[str | None] = mapped_column(String(50))
    decree_date: Mapped[date | None] = mapped_column(Date)
    legal_act_url: Mapped[str | None] = mapped_column(String(1000))
    legal_act_locator: Mapped[str | None] = mapped_column(String(500))
    start_date_basis: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("evidence.id", ondelete="RESTRICT")
    )
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("sources.id", ondelete="RESTRICT")
    )
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON().with_variant(JSONB(), "postgresql"), default=dict, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class AppointmentEvidence(Base):
    __tablename__ = "appointment_evidence"
    __table_args__ = (UniqueConstraint("appointment_id", "evidence_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    appointment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False
    )
    evidence_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("evidence.id", ondelete="RESTRICT"), nullable=False
    )
    relation: Mapped[str] = mapped_column(String(100), nullable=False)
