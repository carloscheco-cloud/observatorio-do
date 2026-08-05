import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

PRIMARY_INSTITUTION_ASSET_WHERE = text(
    "is_primary AND institution_id IS NOT NULL AND approval_status = 'approved'"
)
PRIMARY_PERSON_ASSET_WHERE = text(
    "is_primary AND person_id IS NOT NULL AND approval_status = 'approved'"
)


class MediaAssetType(StrEnum):
    INSTITUTION_BUILDING = "institution_building"
    AUTHORITY_PORTRAIT = "authority_portrait"
    INSTITUTION_LOGO = "institution_logo"
    OFFICIAL_BANNER = "official_banner"
    FALLBACK = "fallback"


class MediaApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class MediaStorageKind(StrEnum):
    REMOTE_OFFICIAL = "remote_official"
    MANAGED = "managed"
    CACHED = "cached"
    GENERATED_FALLBACK = "generated_fallback"


class MediaAsset(Base):
    __tablename__ = "media_assets"
    __table_args__ = (
        CheckConstraint(
            "institution_id IS NOT NULL OR person_id IS NOT NULL OR asset_type = 'fallback'",
            name="ck_media_assets_has_owner_or_fallback",
        ),
        CheckConstraint(
            "NOT (institution_id IS NOT NULL AND person_id IS NOT NULL)",
            name="ck_media_assets_single_owner",
        ),
        CheckConstraint(
            "source_url IS NOT NULL OR storage_kind = 'generated_fallback'",
            name="ck_media_assets_source_or_generated_fallback",
        ),
        CheckConstraint("width IS NULL OR width > 0", name="ck_media_assets_width_positive"),
        CheckConstraint("height IS NULL OR height > 0", name="ck_media_assets_height_positive"),
        UniqueConstraint(
            "institution_id",
            "person_id",
            "asset_type",
            "source_url",
            name="uq_media_assets_owner_type_source",
        ),
        Index(
            "uq_media_assets_primary_institution_type",
            "institution_id",
            "asset_type",
            unique=True,
            postgresql_where=PRIMARY_INSTITUTION_ASSET_WHERE,
        ),
        Index(
            "uq_media_assets_primary_person_type",
            "person_id",
            "asset_type",
            unique=True,
            postgresql_where=PRIMARY_PERSON_ASSET_WHERE,
        ),
        Index("ix_media_assets_checksum", "checksum"),
        Index("ix_media_assets_approval_type", "approval_status", "asset_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("institutions.id", ondelete="RESTRICT"), index=True
    )
    person_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("persons.id", ondelete="RESTRICT"), index=True
    )
    asset_type: Mapped[str] = mapped_column(String(40), nullable=False)
    storage_kind: Mapped[str] = mapped_column(String(40), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(2048))
    public_url: Mapped[str | None] = mapped_column(String(2048))
    storage_key: Mapped[str | None] = mapped_column(String(1024), unique=True)
    source_name: Mapped[str] = mapped_column(String(300), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approval_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=MediaApprovalStatus.PENDING.value
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    alt_text: Mapped[str] = mapped_column(String(500), nullable=False)
    caption: Mapped[str | None] = mapped_column(Text)
    license_note: Mapped[str | None] = mapped_column(Text)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    checksum: Mapped[str | None] = mapped_column(String(64))
    content_type: Mapped[str | None] = mapped_column(String(120))
    approved_by: Mapped[str | None] = mapped_column(String(200))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    supersedes_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("media_assets.id", ondelete="RESTRICT")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
