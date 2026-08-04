import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InstitutionStatus(StrEnum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"


class StateBranch(StrEnum):
    EXECUTIVE = "executive"
    LEGISLATIVE = "legislative"
    JUDICIAL = "judicial"
    CONSTITUTIONAL = "constitutional"
    OTHER = "other"


class InstitutionType(StrEnum):
    PRESIDENCY = "presidency"
    VICE_PRESIDENCY = "vice_presidency"
    MINISTRY = "ministry"
    VICE_MINISTRY = "vice_ministry"
    GENERAL_DIRECTORATE = "general_directorate"
    ATTACHED_AGENCY = "attached_agency"
    AUTONOMOUS_INSTITUTION = "autonomous_institution"
    DECENTRALIZED_INSTITUTION = "decentralized_institution"
    SUPERINTENDENCY = "superintendency"
    COUNCIL = "council"
    COMMISSION = "commission"
    INSTITUTE = "institute"
    CABINET = "cabinet"
    PUBLIC_COMPANY = "public_company"
    PROVINCIAL_GOVERNMENT = "provincial_government"
    TERRITORIAL_DEPENDENCY = "territorial_dependency"
    OTHER = "other"


class OperationalStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    IN_REORGANIZATION = "in_reorganization"
    MERGED = "merged"
    DISSOLVED = "dissolved"
    UNKNOWN = "unknown"


class CoverageLevel(StrEnum):
    NONE = "none"
    BASIC = "basic"
    PARTIAL = "partial"
    SUBSTANTIAL = "substantial"
    COMPLETE = "complete"


class InstitutionRelationshipType(StrEnum):
    HIERARCHICAL = "hierarchical"
    ATTACHED = "attached"
    SUPERVISED = "supervised"
    COORDINATED = "coordinated"
    TERRITORIAL = "territorial"
    DEPENDENT_ON = "dependent_on"


class Institution(Base):
    __tablename__ = "institutions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    kind: Mapped[str] = mapped_column(String(100), nullable=False)
    acronym: Mapped[str | None] = mapped_column(String(40))
    slug: Mapped[str | None] = mapped_column(String(320), unique=True)
    state_branch: Mapped[StateBranch | None] = mapped_column(Enum(StateBranch))
    institution_type: Mapped[InstitutionType | None] = mapped_column(Enum(InstitutionType))
    operational_status: Mapped[OperationalStatus] = mapped_column(
        Enum(OperationalStatus), default=OperationalStatus.UNKNOWN, nullable=False
    )
    coverage_level: Mapped[CoverageLevel] = mapped_column(
        Enum(CoverageLevel), default=CoverageLevel.NONE, nullable=False
    )
    official_website: Mapped[str | None] = mapped_column(String(500))
    functions_summary: Mapped[str | None] = mapped_column(Text)
    creation_date: Mapped[date | None] = mapped_column(Date)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    territory_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("territories.id"), nullable=False)
    status: Mapped[InstitutionStatus] = mapped_column(
        Enum(InstitutionStatus), default=InstitutionStatus.DRAFT, nullable=False
    )
    evidence_links: Mapped[list["InstitutionEvidence"]] = relationship(
        back_populates="institution", cascade="all, delete-orphan"
    )
    parent_relationships: Mapped[list["InstitutionRelationship"]] = relationship(
        foreign_keys="InstitutionRelationship.child_institution_id",
        back_populates="child_institution",
        cascade="all, delete-orphan",
    )
    child_relationships: Mapped[list["InstitutionRelationship"]] = relationship(
        foreign_keys="InstitutionRelationship.parent_institution_id",
        back_populates="parent_institution",
        cascade="all, delete-orphan",
    )


class InstitutionEvidence(Base):
    __tablename__ = "institution_evidence"
    __table_args__ = (UniqueConstraint("institution_id", "evidence_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False
    )
    evidence_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("evidence.id", ondelete="RESTRICT"), nullable=False
    )
    relation: Mapped[str] = mapped_column(String(100), default="supports_existence", nullable=False)
    institution: Mapped[Institution] = relationship(back_populates="evidence_links")


class InstitutionRelationship(Base):
    __tablename__ = "institution_relationships"
    __table_args__ = (
        CheckConstraint("parent_institution_id <> child_institution_id"),
        CheckConstraint("valid_to IS NULL OR valid_from IS NULL OR valid_to >= valid_from"),
        CheckConstraint("valid_from IS NOT NULL OR length(trim(notes)) > 0"),
        Index(
            "uq_institution_relationship_period_known",
            "parent_institution_id",
            "child_institution_id",
            "relationship_type",
            "valid_from",
            unique=True,
            postgresql_where=text("valid_from IS NOT NULL"),
            sqlite_where=text("valid_from IS NOT NULL"),
        ),
        Index(
            "uq_institution_relationship_period_unknown",
            "parent_institution_id",
            "child_institution_id",
            "relationship_type",
            unique=True,
            postgresql_where=text("valid_from IS NULL"),
            sqlite_where=text("valid_from IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    parent_institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    child_institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    relationship_type: Mapped[InstitutionRelationshipType] = mapped_column(
        Enum(InstitutionRelationshipType), nullable=False
    )
    valid_from: Mapped[date | None] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    evidence_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("evidence.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    parent_institution: Mapped[Institution] = relationship(
        foreign_keys=[parent_institution_id], back_populates="child_relationships"
    )
    child_institution: Mapped[Institution] = relationship(
        foreign_keys=[child_institution_id], back_populates="parent_relationships"
    )
