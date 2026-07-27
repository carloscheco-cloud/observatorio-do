from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.modules.appointments.models import Appointment, AppointmentStatus
from app.modules.budget.models import (
    BudgetAppropriation,
    BudgetClassifier,
    BudgetCycle,
    BudgetExecutionRecord,
    BudgetFinding,
    BudgetModification,
    BudgetProgram,
    BudgetRevenue,
    BudgetStatus,
    CycleType,
)
from app.modules.employment_relationships.models import (
    EmploymentRelationship,
    EmploymentType,
    RelationshipStatus,
)
from app.modules.evidence.models import Evidence
from app.modules.institutions.models import (
    Institution,
    InstitutionEvidence,
    InstitutionStatus,
)
from app.modules.legal_basis.models import LegalBasis, LegalInstrumentType
from app.modules.organizational_units.models import (
    OrganizationalEvent,
    OrganizationalEventType,
    OrganizationalUnit,
    OrganizationalUnitEvidence,
    PositionUnitAssignment,
    UnitStatus,
    UnitType,
)
from app.modules.payroll_entries.models import PayrollEntry, PayrollEntryStatus
from app.modules.payroll_periods.models import PayrollPeriod, PayrollPeriodStatus
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
    block4_source = db.scalar(
        select(Source).where(Source.url == "controlled://block-4/organizational-structure")
    )
    if block4_source is None:
        block4_source = Source(
            name="Fuente ficticia controlada del bloque 4",
            url="controlled://block-4/organizational-structure",
            publisher="Observatorio del Estado Dominicano - datos de prueba",
            is_official=False,
        )
        db.add(block4_source)
        db.flush()
    block4_evidence = db.scalar(
        select(Evidence).where(
            Evidence.content_hash
            == "94e820af41a1d870f8ddf4e98ca20b230c8070e42b84d17b1951326402933c1a"
        )
    )
    if block4_evidence is None:
        block4_evidence = Evidence(
            source_id=block4_source.id,
            title="Organigrama completamente ficticio para pruebas del bloque 4",
            excerpt="No representa la estructura real del Ayuntamiento Municipal de Bonao.",
            locator="controlled://block-4/organizational-structure/evidence",
            content_hash="94e820af41a1d870f8ddf4e98ca20b230c8070e42b84d17b1951326402933c1a",
            metadata_={"controlled": True, "fictitious": True, "seed": "block-4"},
        )
        db.add(block4_evidence)
        db.flush()
    block4_legal = db.scalar(
        select(LegalBasis).where(LegalBasis.reference == "CONTROL-B4-LEGAL-001")
    )
    if block4_legal is None:
        block4_legal = LegalBasis(
            instrument_type=LegalInstrumentType.OTHER,
            title="Fundamento legal ficticio controlado del bloque 4",
            reference="CONTROL-B4-LEGAL-001",
            evidence_id=block4_evidence.id,
            effective_from=date(2025, 1, 1),
            issuing_body="Órgano ficticio de control",
            description="Instrumento de prueba sin validez ni afirmaciones sobre la realidad.",
            metadata_={"controlled": True, "fictitious": True, "seed": "block-4"},
        )
        db.add(block4_legal)
        db.flush()

    def controlled_unit(
        code: str,
        name: str,
        kind: UnitType,
        level: int,
        parent: OrganizationalUnit | None = None,
        *,
        territory: Territory | None = None,
    ) -> OrganizationalUnit:
        unit = db.scalar(
            select(OrganizationalUnit).where(
                OrganizationalUnit.institution_id == institution.id,
                OrganizationalUnit.stable_code == code,
            )
        )
        if unit is None:
            unit = OrganizationalUnit(
                institution_id=institution.id,
                parent_unit_id=parent.id if parent else None,
                official_name=name,
                normalized_name=name.casefold(),
                stable_code=code,
                unit_type=kind,
                hierarchy_level=level,
                order_index=level,
                is_headquarters=parent is None,
                status=UnitStatus.CANONICAL,
                valid_from=date(2025, 1, 1),
                territory_id=territory.id if territory else None,
                legal_basis_id=block4_legal.id,
                metadata_={"controlled": True, "fictitious": True, "seed": "block-4"},
            )
            db.add(unit)
            db.flush()
        link = db.scalar(
            select(OrganizationalUnitEvidence).where(
                OrganizationalUnitEvidence.unit_id == unit.id,
                OrganizationalUnitEvidence.evidence_id == block4_evidence.id,
            )
        )
        if link is None:
            db.add(
                OrganizationalUnitEvidence(
                    unit_id=unit.id,
                    evidence_id=block4_evidence.id,
                    source_id=block4_source.id,
                )
            )
            db.flush()
        return unit

    root = controlled_unit("CONTROL-B4-ROOT", "Unidad Raíz Controlada", UnitType.GOVERNING_BODY, 0)
    directorate = controlled_unit(
        "CONTROL-B4-DIR-ADM",
        "Dirección Administrativa Ficticia",
        UnitType.DIRECTORATE,
        1,
        root,
    )
    department = controlled_unit(
        "CONTROL-B4-DEP-RRHH",
        "Departamento de Recursos Humanos Ficticio",
        UnitType.DEPARTMENT,
        2,
        directorate,
    )
    controlled_unit(
        "CONTROL-B4-DIV-NOM",
        "División de Nómina Ficticia",
        UnitType.DIVISION,
        3,
        department,
    )
    controlled_unit(
        "CONTROL-B4-OF-TERR",
        "Oficina Territorial Ficticia",
        UnitType.TERRITORIAL_OFFICE,
        1,
        root,
        territory=bonao,
    )
    event = db.scalar(
        select(OrganizationalEvent).where(
            OrganizationalEvent.unit_id == directorate.id,
            OrganizationalEvent.event_type == OrganizationalEventType.CREATION,
            OrganizationalEvent.effective_date == date(2025, 1, 1),
        )
    )
    if event is None:
        db.add(
            OrganizationalEvent(
                institution_id=institution.id,
                unit_id=directorate.id,
                event_type=OrganizationalEventType.CREATION,
                effective_date=date(2025, 1, 1),
                new_parent_id=root.id,
                new_name=directorate.official_name,
                legal_basis_id=block4_legal.id,
                evidence_id=block4_evidence.id,
                source_id=block4_source.id,
                description="Evento ficticio y controlado de creación organizativa.",
                metadata_={"controlled": True, "fictitious": True, "seed": "block-4"},
            )
        )
    head_position = db.scalar(select(Position).where(Position.code == "CONTROL-B4-DIRECTOR-ADM"))
    if head_position is None:
        head_position = Position(
            institution_id=institution.id,
            organizational_unit_id=directorate.id,
            official_name="Director/a Administrativo/a Ficticio/a",
            code="CONTROL-B4-DIRECTOR-ADM",
            position_type="controlled_unit_head",
            hierarchy_level="directorate_head",
            access_method=AccessMethod.APPOINTMENT,
            legal_basis_id=block4_legal.id,
            status=PositionStatus.CANONICAL,
            valid_from=date(2025, 1, 1),
            metadata_={"controlled": True, "fictitious": True, "seed": "block-4"},
        )
        db.add(head_position)
        db.flush()
    assignment = db.scalar(
        select(PositionUnitAssignment).where(
            PositionUnitAssignment.position_id == head_position.id,
            PositionUnitAssignment.organizational_unit_id == directorate.id,
        )
    )
    if assignment is None:
        db.add(
            PositionUnitAssignment(
                position_id=head_position.id,
                organizational_unit_id=directorate.id,
                valid_from=date(2025, 1, 1),
            )
        )
    block4_appointment = db.scalar(
        select(Appointment).where(
            Appointment.position_id == head_position.id,
            Appointment.legal_act == "ACTO-CONTROL-B4-001",
        )
    )
    if block4_appointment is None:
        db.add(
            Appointment(
                person_id=person.id,
                position_id=head_position.id,
                institution_id=institution.id,
                start_date=date(2025, 1, 1),
                appointment_type="controlled_test",
                status=AppointmentStatus.CONFIRMED,
                legal_act="ACTO-CONTROL-B4-001",
                evidence_id=block4_evidence.id,
                source_id=block4_source.id,
                metadata_={"controlled": True, "fictitious": True, "seed": "block-4"},
            )
        )
    _seed_block5(
        db, institution, person, head_position, directorate, block4_source, block4_evidence
    )
    _seed_block6(db, institution, directorate, bonao, block4_source, block4_evidence, block4_legal)
    db.commit()


def _seed_block5(
    db: Session,
    institution: Institution,
    person: Person,
    position: Position,
    unit: OrganizationalUnit,
    source: Source,
    evidence: Evidence,
) -> None:
    """Idempotent, explicitly fictitious payroll sample; never production data."""
    relationship = db.scalar(
        select(EmploymentRelationship).where(
            EmploymentRelationship.person_id == person.id,
            EmploymentRelationship.institution_id == institution.id,
            EmploymentRelationship.start_date == date(2025, 1, 1),
        )
    )
    if relationship is None:
        relationship = EmploymentRelationship(
            person_id=person.id,
            institution_id=institution.id,
            position_id=position.id,
            organizational_unit_id=unit.id,
            employment_type=EmploymentType.CAREER,
            relationship_status=RelationshipStatus.ACTIVE,
            start_date=date(2025, 1, 1),
            source_id=source.id,
            evidence_id=evidence.id,
            metadata_={"controlled": True, "fictitious": True, "seed": "block-5"},
        )
        db.add(relationship)
        db.flush()
    for month, gross in ((1, 50000), (2, 52500)):
        period = db.scalar(
            select(PayrollPeriod).where(
                PayrollPeriod.institution_id == institution.id,
                PayrollPeriod.year == 2025,
                PayrollPeriod.month == month,
                PayrollPeriod.version == 1,
            )
        )
        if period is None:
            period = PayrollPeriod(
                institution_id=institution.id,
                year=2025,
                month=month,
                period_start=date(2025, month, 1),
                period_end=date(2025, month, 28),
                status=PayrollPeriodStatus.CONFIRMED,
                currency="DOP",
                source_id=source.id,
                evidence_id=evidence.id,
                record_count=1,
                calculated_gross_total=gross,
                calculated_net_total=gross - 5000,
                checksum=f"{month:064x}",
                metadata_={"controlled": True, "fictitious": True, "seed": "block-5"},
            )
            db.add(period)
            db.flush()
        entry = db.scalar(
            select(PayrollEntry).where(
                PayrollEntry.payroll_period_id == period.id,
                PayrollEntry.person_id == person.id,
            )
        )
        if entry is None:
            db.add(
                PayrollEntry(
                    payroll_period_id=period.id,
                    employment_relationship_id=relationship.id,
                    person_id=person.id,
                    institution_id=institution.id,
                    position_id=position.id,
                    organizational_unit_id=unit.id,
                    listed_name="Persona Ficticia de Control",
                    normalized_name="persona ficticia de control",
                    employment_type="career",
                    base_salary=gross,
                    gross_income=gross,
                    total_deductions=5000,
                    net_income=gross - 5000,
                    other_compensation=0,
                    currency="DOP",
                    status=PayrollEntryStatus.CONFIRMED,
                    source_id=source.id,
                    evidence_id=evidence.id,
                    raw_payload={"controlled": True, "fictitious": True},
                    metadata_={"controlled": True, "fictitious": True, "seed": "block-5"},
                )
            )


def _seed_block6(
    db: Session,
    institution: Institution,
    unit: OrganizationalUnit,
    territory: Territory,
    source: Source,
    evidence: Evidence,
    legal_basis: LegalBasis,
) -> None:
    """Idempotent fictitious budget sample; amounts do not represent public finances."""
    marker = {"controlled": True, "fictitious": True, "test_data": True, "seed": "block-6"}
    cycle = db.scalar(
        select(BudgetCycle).where(
            BudgetCycle.fiscal_year == 2099,
            BudgetCycle.jurisdiction == "Jurisdicción ficticia de control",
        )
    )
    if cycle is None:
        cycle = BudgetCycle(
            fiscal_year=2099,
            jurisdiction="Jurisdicción ficticia de control",
            government_level="municipal_controlled",
            cycle_type=CycleType.APPROVED,
            start_date=date(2099, 1, 1),
            end_date=date(2099, 12, 31),
            status=BudgetStatus.CONFIRMED,
            currency="DOP",
            legal_basis_id=legal_basis.id,
            source_id=source.id,
            evidence_id=evidence.id,
            version=1,
            checksum="6" * 64,
            metadata_=marker,
        )
        db.add(cycle)
        db.flush()
    classifier = db.scalar(
        select(BudgetClassifier).where(
            BudgetClassifier.classifier_type == "expenditure",
            BudgetClassifier.code == "CONTROL-B6-GASTO",
        )
    )
    if classifier is None:
        classifier = BudgetClassifier(
            classifier_type="expenditure",
            code="CONTROL-B6-GASTO",
            official_name="Clasificador ficticio de gasto",
            hierarchy_level=0,
            valid_from=date(2099, 1, 1),
            status=BudgetStatus.CONFIRMED,
            source_id=source.id,
            evidence_id=evidence.id,
            metadata_=marker,
        )
        db.add(classifier)
        db.flush()
    programs: list[BudgetProgram] = []
    for code, name in (
        ("CONTROL-P01", "Programa ficticio de servicios controlados"),
        ("CONTROL-P02", "Programa ficticio de infraestructura controlada"),
    ):
        program = db.scalar(
            select(BudgetProgram).where(
                BudgetProgram.budget_cycle_id == cycle.id,
                BudgetProgram.program_code == code,
            )
        )
        if program is None:
            program = BudgetProgram(
                institution_id=institution.id,
                budget_cycle_id=cycle.id,
                program_code=code,
                official_name=name,
                normalized_name=name.lower(),
                program_type="program",
                territory_id=territory.id,
                organizational_unit_id=unit.id,
                start_date=date(2099, 1, 1),
                status=BudgetStatus.CONFIRMED,
                legal_basis_id=legal_basis.id,
                source_id=source.id,
                evidence_id=evidence.id,
                metadata_=marker,
            )
            db.add(program)
            db.flush()
        programs.append(program)
    appropriations: list[BudgetAppropriation] = []
    for index, (program, approved, current) in enumerate(
        ((programs[0], 100000, 120000), (programs[1], 200000, 180000)), 1
    ):
        item = db.scalar(
            select(BudgetAppropriation).where(
                BudgetAppropriation.budget_cycle_id == cycle.id,
                BudgetAppropriation.program_id == program.id,
                BudgetAppropriation.version == 1,
            )
        )
        if item is None:
            item = BudgetAppropriation(
                budget_cycle_id=cycle.id,
                institution_id=institution.id,
                program_id=program.id,
                organizational_unit_id=unit.id,
                territory_id=territory.id,
                classifier_id=classifier.id,
                approved_amount=approved,
                current_amount=current,
                currency="DOP",
                valid_from=date(2099, 1, 1),
                status=BudgetStatus.CONFIRMED,
                source_id=source.id,
                evidence_id=evidence.id,
                row_number=index,
                version=1,
                checksum=f"{60 + index:064x}",
                raw_payload=marker,
                metadata_=marker,
            )
            db.add(item)
            db.flush()
        appropriations.append(item)
    if (
        db.scalar(
            select(BudgetModification).where(
                BudgetModification.appropriation_id == appropriations[0].id
            )
        )
        is None
    ):
        db.add(
            BudgetModification(
                budget_cycle_id=cycle.id,
                institution_id=institution.id,
                appropriation_id=appropriations[0].id,
                modification_type="increase",
                amount=20000,
                previous_balance=100000,
                resulting_balance=120000,
                effective_date=date(2099, 2, 1),
                legal_reference="CONTROL-B6-MOD-001",
                legal_basis_id=legal_basis.id,
                source_id=source.id,
                evidence_id=evidence.id,
                description="Aumento ficticio controlado.",
                status=BudgetStatus.CONFIRMED,
                metadata_=marker,
            )
        )
    for month, committed, accrued, paid in (
        (1, 10000, 8000, 7000),
        (2, 15000, 12000, 11000),
        (3, 20000, 16000, 15000),
    ):
        start = date(2099, month, 1)
        if (
            db.scalar(
                select(BudgetExecutionRecord).where(
                    BudgetExecutionRecord.appropriation_id == appropriations[0].id,
                    BudgetExecutionRecord.period_start == start,
                )
            )
            is None
        ):
            db.add(
                BudgetExecutionRecord(
                    budget_cycle_id=cycle.id,
                    institution_id=institution.id,
                    appropriation_id=appropriations[0].id,
                    execution_period=f"2099-{month:02d}",
                    period_start=start,
                    period_end=date(2099, month, 28),
                    initial_budget=100000,
                    current_budget=120000,
                    committed_amount=committed,
                    accrued_amount=accrued,
                    paid_amount=paid,
                    available_balance=120000 - committed,
                    currency="DOP",
                    status=BudgetStatus.CONFIRMED,
                    source_id=source.id,
                    evidence_id=evidence.id,
                    row_number=month,
                    raw_payload=marker,
                    metadata_=marker,
                )
            )
    if db.scalar(select(BudgetRevenue).where(BudgetRevenue.budget_cycle_id == cycle.id)) is None:
        db.add(
            BudgetRevenue(
                budget_cycle_id=cycle.id,
                institution_id=institution.id,
                revenue_classifier_id=classifier.id,
                estimated_amount=300000,
                modified_estimate=300000,
                collected_amount=90000,
                accrued_amount=95000,
                period_start=date(2099, 1, 1),
                period_end=date(2099, 3, 31),
                currency="DOP",
                status=BudgetStatus.CONFIRMED,
                source_id=source.id,
                evidence_id=evidence.id,
                raw_payload=marker,
                metadata_=marker,
            )
        )
    if (
        db.scalar(
            select(BudgetFinding).where(
                BudgetFinding.budget_cycle_id == cycle.id,
                BudgetFinding.finding_type == "under_execution",
            )
        )
        is None
    ):
        db.add(
            BudgetFinding(
                finding_type="under_execution",
                severity="review_required",
                institution_id=institution.id,
                budget_cycle_id=cycle.id,
                appropriation_id=appropriations[1].id,
                observed_value={"paid_percentage": "0"},
                expected_or_previous_value={"controlled_threshold": "25"},
                explanation=(
                    "Señal ficticia de subejecución para pruebas; no implica irregularidad."
                ),
                evidence_id=evidence.id,
                metadata_=marker,
            )
        )


def main() -> None:
    with SessionLocal() as db:
        seed(db)


if __name__ == "__main__":
    main()
