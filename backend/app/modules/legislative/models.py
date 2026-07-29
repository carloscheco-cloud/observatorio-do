import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ChamberKind(StrEnum):
    SENATE = "senate"
    CHAMBER_OF_DEPUTIES = "chamber_of_deputies"


class LegislativeRecordStatus(StrEnum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    INACTIVE = "inactive"


class DataAvailability(StrEnum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    NOT_AVAILABLE = "not_available"
    NOT_APPLICABLE = "not_applicable"
    UNDER_REVIEW = "under_review"


class TraceableLegislativeRecord:
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"), index=True)
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"), index=True)
    actor_type: Mapped[str] = mapped_column(String(30), default="human", nullable=False)
    validation_status: Mapped[str] = mapped_column(
        String(30), default=LegislativeRecordStatus.DRAFT.value, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class LegislativeChamber(TraceableLegislativeRecord, Base):
    __tablename__ = "legislative_chambers"
    __table_args__ = (
        UniqueConstraint("kind", "valid_from", name="uq_legislative_chamber_kind_period"),
        CheckConstraint("valid_to IS NULL OR valid_to >= valid_from", name="ck_chamber_dates"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    official_name: Mapped[str] = mapped_column(String(200), nullable=False)
    short_name: Mapped[str] = mapped_column(String(100), nullable=False)
    constitutional_seat_count: Mapped[int | None] = mapped_column(Integer)
    official_url: Mapped[str | None] = mapped_column(String(1000))
    valid_from: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    valid_to: Mapped[date | None] = mapped_column(Date, index=True)


class LegislativeTerm(TraceableLegislativeRecord, Base):
    __tablename__ = "legislative_terms"
    __table_args__ = (
        UniqueConstraint("term_number", "start_date", name="uq_legislative_term_number_start"),
        CheckConstraint("end_date >= start_date", name="ck_legislative_term_dates"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    term_number: Mapped[str] = mapped_column(String(50), nullable=False)
    official_name: Mapped[str] = mapped_column(String(200), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    election_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False, index=True)


class LegislativeParty(TraceableLegislativeRecord, Base):
    __tablename__ = "legislative_parties"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    official_name: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    acronym: Mapped[str | None] = mapped_column(String(30), index=True)
    official_url: Mapped[str | None] = mapped_column(String(1000))
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False, index=True)


class LegislativeBloc(TraceableLegislativeRecord, Base):
    __tablename__ = "legislative_blocs"
    __table_args__ = (
        UniqueConstraint(
            "chamber_id", "legislative_term_id", "official_name", name="uq_legislative_bloc"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    chamber_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("legislative_chambers.id"), nullable=False, index=True
    )
    legislative_term_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("legislative_terms.id"), nullable=False, index=True
    )
    party_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("legislative_parties.id"), index=True
    )
    official_name: Mapped[str] = mapped_column(String(250), nullable=False)
    acronym: Mapped[str | None] = mapped_column(String(50))
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date)


class LegislativeSeat(TraceableLegislativeRecord, Base):
    __tablename__ = "legislative_seats"
    __table_args__ = (
        UniqueConstraint(
            "chamber_id",
            "legislative_term_id",
            "seat_code",
            name="uq_legislative_seat_term_code",
        ),
        CheckConstraint("seat_number IS NULL OR seat_number > 0", name="ck_seat_number_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    chamber_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("legislative_chambers.id"), nullable=False, index=True
    )
    legislative_term_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("legislative_terms.id"), nullable=False, index=True
    )
    territory_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("territories.id"), nullable=False, index=True
    )
    seat_code: Mapped[str] = mapped_column(String(100), nullable=False)
    seat_number: Mapped[int | None] = mapped_column(Integer)
    seat_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    constituency_name: Mapped[str | None] = mapped_column(String(250), index=True)
    constituency_code: Mapped[str | None] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False, index=True)


class LegislativeMandate(TraceableLegislativeRecord, Base):
    __tablename__ = "legislative_mandates"
    __table_args__ = (
        UniqueConstraint(
            "seat_id", "person_id", "start_date", name="uq_legislative_mandate_person_seat"
        ),
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name="ck_mandate_dates"),
        CheckConstraint(
            "coverage_score IS NULL OR (coverage_score >= 0 AND coverage_score <= 100)",
            name="ck_legislative_coverage_score",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    person_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("persons.id"), nullable=False, index=True
    )
    seat_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("legislative_seats.id"), nullable=False, index=True
    )
    party_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("legislative_parties.id"), index=True
    )
    bloc_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("legislative_blocs.id"), index=True
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date | None] = mapped_column(Date, index=True)
    mandate_status: Mapped[str] = mapped_column(
        String(30), default="active", nullable=False, index=True
    )
    official_profile_url: Mapped[str | None] = mapped_column(String(1000))
    sworn_in_date: Mapped[date | None] = mapped_column(Date)
    termination_reason: Mapped[str | None] = mapped_column(Text)
    initiatives_availability: Mapped[str] = mapped_column(
        String(30), default=DataAvailability.UNDER_REVIEW.value, nullable=False
    )
    attendance_availability: Mapped[str] = mapped_column(
        String(30), default=DataAvailability.NOT_AVAILABLE.value, nullable=False
    )
    voting_availability: Mapped[str] = mapped_column(
        String(30), default=DataAvailability.NOT_AVAILABLE.value, nullable=False
    )
    declarations_availability: Mapped[str] = mapped_column(
        String(30), default=DataAvailability.UNDER_REVIEW.value, nullable=False
    )
    coverage_score: Mapped[int | None] = mapped_column(Integer)
