import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base


class UnitType(StrEnum):
    GOVERNING_BODY = "governing_body"
    EXECUTIVE_OFFICE = "executive_office"
    DIRECTORATE = "directorate"
    DEPARTMENT = "department"
    DIVISION = "division"
    SECTION = "section"
    UNIT = "unit"
    OFFICE = "office"
    COMMITTEE = "committee"
    COUNCIL = "council"
    TERRITORIAL_OFFICE = "territorial_office"
    ADVISORY_BODY = "advisory_body"
    SUPPORT_BODY = "support_body"
    OPERATIONAL_BODY = "operational_body"
    OTHER = "other"


class UnitStatus(StrEnum):
    DRAFT = "draft"
    CANONICAL = "canonical"
    INACTIVE = "inactive"
    ELIMINATED = "eliminated"
    MERGED = "merged"
    REPLACED = "replaced"


class OrganizationalEventType(StrEnum):
    CREATION = "creation"
    ELIMINATION = "elimination"
    MERGER = "merger"
    SPLIT = "split"
    RENAME = "rename"
    TRANSFER = "transfer"
    AFFILIATION = "affiliation"
    DISAFFILIATION = "disaffiliation"
    HIERARCHY_CHANGE = "hierarchy_change"
    TYPE_CHANGE = "type_change"
    LEGAL_BASIS_CHANGE = "legal_basis_change"


class OrganizationalUnit(Base):
    __tablename__ = "organizational_units"
    __table_args__ = (
        UniqueConstraint("institution_id", "stable_code", name="uq_unit_institution_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id", ondelete="RESTRICT"), nullable=False
    )
    parent_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_units.id", ondelete="RESTRICT")
    )
    official_name: Mapped[str] = mapped_column(String(300), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(300), nullable=False)
    stable_code: Mapped[str] = mapped_column(String(100), nullable=False)
    acronym: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    unit_type: Mapped[UnitType] = mapped_column(Enum(UnitType), nullable=False)
    hierarchy_level: Mapped[int] = mapped_column(Integer, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_headquarters: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_single_head: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[UnitStatus] = mapped_column(
        Enum(UnitStatus), default=UnitStatus.DRAFT, nullable=False
    )
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date)
    territory_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("territories.id", ondelete="RESTRICT")
    )
    legal_basis_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("legal_bases.id", ondelete="RESTRICT")
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


class OrganizationalUnitEvidence(Base):
    __tablename__ = "organizational_unit_evidence"

    unit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizational_units.id", ondelete="CASCADE"), primary_key=True
    )
    evidence_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("evidence.id", ondelete="RESTRICT"), primary_key=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class OrganizationalEvent(Base):
    __tablename__ = "organizational_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id", ondelete="RESTRICT"), nullable=False
    )
    unit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizational_units.id", ondelete="RESTRICT"), nullable=False
    )
    event_type: Mapped[OrganizationalEventType] = mapped_column(
        Enum(OrganizationalEventType), nullable=False
    )
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    previous_parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_units.id", ondelete="RESTRICT")
    )
    new_parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_units.id", ondelete="RESTRICT")
    )
    previous_name: Mapped[str | None] = mapped_column(String(300))
    new_name: Mapped[str | None] = mapped_column(String(300))
    legal_basis_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("legal_bases.id", ondelete="RESTRICT"), nullable=False
    )
    evidence_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("evidence.id", ondelete="RESTRICT"), nullable=False
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON().with_variant(JSONB(), "postgresql"), default=dict, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class PositionUnitAssignment(Base):
    __tablename__ = "position_unit_assignments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    position_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("positions.id", ondelete="CASCADE"), nullable=False
    )
    organizational_unit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizational_units.id", ondelete="RESTRICT"), nullable=False
    )
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
