from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.modules.appointments.models import Appointment, AppointmentStatus
from app.modules.evidence.models import Evidence
from app.modules.institutions.models import (
    Institution,
    InstitutionEvidence,
    InstitutionStatus,
)
from app.modules.legal_basis.models import LegalBasis, LegalInstrumentType
from app.modules.persons.models import Person, PersonStatus
from app.modules.positions.models import AccessMethod, Position, PositionStatus
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

    controlled_evidence = db.scalar(
        select(Evidence).where(
            Evidence.content_hash
            == "c62bba43c31f0367a0aca6f45b80ddbf0ddae5a15cbd0320d2f56d2a4f308f73"
        )
    )
    if controlled_evidence is None:
        controlled_evidence = Evidence(
            source_id=source.id,
            title="Registro controlado para pruebas del bloque 3",
            excerpt=(
                "Contenido deliberadamente ficticio para validar personas, cargos, "
                "fundamento legal y designaciones."
            ),
            locator="controlled://block-3/bonao-mayor",
            content_hash="c62bba43c31f0367a0aca6f45b80ddbf0ddae5a15cbd0320d2f56d2a4f308f73",
            metadata_={"controlled": True, "fictitious": True, "seed": "block-3"},
        )
        db.add(controlled_evidence)
        db.flush()

    person = db.scalar(
        select(Person).where(Person.normalized_name == "persona ficticia de control")
    )
    if person is None:
        person = Person(
            full_name="Persona Ficticia de Control",
            normalized_name="persona ficticia de control",
            status=PersonStatus.CONFIRMED,
            nationality="Ficticia",
            metadata_={"controlled": True, "fictitious": True, "seed": "block-3"},
        )
        db.add(person)
        db.flush()

    legal_basis = db.scalar(
        select(LegalBasis).where(LegalBasis.reference == "CONTROL-B3-LEGAL-001")
    )
    if legal_basis is None:
        legal_basis = LegalBasis(
            instrument_type=LegalInstrumentType.OTHER,
            title="Instrumento jurídico controlado para pruebas",
            reference="CONTROL-B3-LEGAL-001",
            article="Artículo de control",
            evidence_id=controlled_evidence.id,
            issuing_body="Organismo emisor ficticio de control",
            description="No representa una norma real ni atribuye datos a funcionarios reales.",
            metadata_={"controlled": True, "fictitious": True, "seed": "block-3"},
        )
        db.add(legal_basis)
        db.flush()

    position = db.scalar(select(Position).where(Position.code == "DO-BONAO-ALCALDIA-CONTROL"))
    if position is None:
        position = Position(
            institution_id=institution.id,
            official_name="Alcalde/Alcaldesa del Ayuntamiento Municipal de Bonao",
            code="DO-BONAO-ALCALDIA-CONTROL",
            description="Cargo municipal incluido únicamente como semilla controlada.",
            position_type="elected_municipal_executive",
            hierarchy_level="municipal_executive",
            access_method=AccessMethod.ELECTION,
            legal_basis_id=legal_basis.id,
            status=PositionStatus.CANONICAL,
            single_occupant=True,
            metadata_={"controlled": True, "seed": "block-3"},
        )
        db.add(position)
        db.flush()

    appointment = db.scalar(
        select(Appointment).where(
            Appointment.position_id == position.id,
            Appointment.person_id == person.id,
            Appointment.legal_act == "ACTO-CONTROL-B3-001",
        )
    )
    if appointment is None:
        appointment = Appointment(
            person_id=person.id,
            position_id=position.id,
            institution_id=institution.id,
            start_date=date(2025, 1, 1),
            appointment_type="controlled_test",
            status=AppointmentStatus.CONFIRMED,
            legal_act="ACTO-CONTROL-B3-001",
            evidence_id=controlled_evidence.id,
            source_id=source.id,
            metadata_={"controlled": True, "fictitious": True, "seed": "block-3"},
        )
        db.add(appointment)
    db.commit()


def main() -> None:
    with SessionLocal() as db:
        seed(db)


if __name__ == "__main__":
    main()
