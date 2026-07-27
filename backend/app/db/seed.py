from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.modules.evidence.models import Evidence
from app.modules.institutions.models import (
    Institution,
    InstitutionEvidence,
    InstitutionStatus,
)
from app.modules.sources.models import Source
from app.modules.territories.models import Territory, TerritoryType


def _territory(
    db: Session, *, code: str, name: str, kind: TerritoryType, parent: Territory | None = None
) -> Territory:
    item = db.scalar(select(Territory).where(Territory.code == code))
    if item is None:
        item = Territory(code=code, name=name, type=kind, parent=parent)
        db.add(item)
        db.flush()
    return item


def seed(db: Session) -> None:
    country = _territory(db, code="DO", name="República Dominicana", kind=TerritoryType.COUNTRY)
    province = _territory(
        db, code="DO-28", name="Monseñor Nouel", kind=TerritoryType.PROVINCE, parent=country
    )
    bonao = _territory(
        db, code="DO-2801", name="Bonao", kind=TerritoryType.MUNICIPALITY, parent=province
    )
    _territory(db, code="DO-2802", name="Maimón", kind=TerritoryType.MUNICIPALITY, parent=province)
    _territory(
        db, code="DO-2803", name="Piedra Blanca", kind=TerritoryType.MUNICIPALITY, parent=province
    )

    source = db.scalar(select(Source).where(Source.url == "https://ayuntamientobonao.gob.do/"))
    if source is None:
        source = Source(
            name="Portal oficial del Ayuntamiento Municipal de Bonao",
            url="https://ayuntamientobonao.gob.do/",
            publisher="Ayuntamiento Municipal de Bonao",
            is_official=True,
        )
        db.add(source)
        db.flush()

    evidence = db.scalar(
        select(Evidence).where(
            Evidence.content_hash
            == "40bcd65d9f94d84ff99f11c07e912c2667d57c48159152ed301f20df65b1c72e"
        )
    )
    if evidence is None:
        evidence = Evidence(
            source_id=source.id,
            title="Portal institucional del Ayuntamiento Municipal de Bonao",
            excerpt="Portal oficial que identifica al Ayuntamiento Municipal de Bonao.",
            locator="https://ayuntamientobonao.gob.do/",
            content_hash="40bcd65d9f94d84ff99f11c07e912c2667d57c48159152ed301f20df65b1c72e",
            metadata_={"official": True, "seed": "blocks-1-2"},
        )
        db.add(evidence)
        db.flush()

    institution = db.scalar(
        select(Institution).where(Institution.name == "Ayuntamiento Municipal de Bonao")
    )
    if institution is None:
        institution = Institution(
            name="Ayuntamiento Municipal de Bonao",
            kind="municipal_government",
            territory_id=bonao.id,
            status=InstitutionStatus.DRAFT,
        )
        db.add(institution)
        db.flush()
    link = db.scalar(
        select(InstitutionEvidence).where(
            InstitutionEvidence.institution_id == institution.id,
            InstitutionEvidence.evidence_id == evidence.id,
        )
    )
    if link is None:
        db.add(InstitutionEvidence(institution_id=institution.id, evidence_id=evidence.id))
        db.flush()
    institution.status = InstitutionStatus.CONFIRMED
    db.commit()


def main() -> None:
    with SessionLocal() as db:
        seed(db)


if __name__ == "__main__":
    main()
