from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.modules.appointments.models import Appointment, AppointmentStatus
from app.modules.asset_categories.models import AssetCategory
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
from app.modules.creditors.models import Creditor
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
from app.modules.procurement_processes.models import (
    ContractAmendment,
    ContractDelivery,
    ContractGuarantee,
    ContractPayment,
    ProcedureType,
    ProcessStatus,
    ProcurementAward,
    ProcurementBid,
    ProcurementChallenge,
    ProcurementContract,
    ProcurementFinding,
    ProcurementItem,
    ProcurementLot,
    ProcurementProcess,
    ProcurementType,
    PurchaseOrder,
)
from app.modules.public_assets.models import (
    AssetAssignment,
    AssetDisposal,
    AssetEvent,
    AssetFinding,
    AssetInsurancePolicy,
    AssetLocation,
    AssetMaintenanceRecord,
    AssetTransfer,
    AssetValuation,
    EquipmentAsset,
    InfrastructureAsset,
    IntangibleAsset,
    PhysicalInventory,
    PhysicalInventoryItem,
    PublicAsset,
    RealEstateAsset,
    VehicleAsset,
)
from app.modules.public_debt.models import (
    DebtBalanceSnapshot,
    DebtDisbursement,
    DebtInstrument,
    DebtPayment,
    DebtServiceSchedule,
    DebtTerm,
    FiscalRiskFinding,
    MultiYearCommitment,
    PublicGuarantee,
    PublicObligation,
    PublicSubsidy,
)
from app.modules.risk_engine.seed import seed_risk_engine
from app.modules.sources.models import Source
from app.modules.suppliers.models import Supplier, SupplierType
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
    _seed_block7(db, institution, directorate, bonao, block4_source, block4_evidence, block4_legal)
    _seed_block8(db, institution, source, evidence, legal_basis)
    _seed_block9(db, institution, bonao, block4_source, block4_evidence, block4_legal)
    seed_risk_engine(
        db,
        institution_id=institution.id,
        territory_id=bonao.id,
        source_id=block4_source.id,
        evidence_id=block4_evidence.id,
    )
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


def _seed_block7(
    db: Session,
    institution: Institution,
    unit: OrganizationalUnit,
    territory: Territory,
    source: Source,
    evidence: Evidence,
    legal_basis: LegalBasis,
) -> None:
    """Idempotent, fictitious procurement sample for automated tests only."""
    marker = {"controlled": True, "fictitious": True, "seed": "block-7"}
    suppliers: list[Supplier] = []
    for number, name in enumerate(
        (
            "Suministros Quisqueya de Prueba SRL",
            "Servicios Cibao Controlados SRL",
            "Consorcio Ficticio La Vega",
        ),
        1,
    ):
        normalized = name.casefold()
        supplier = db.scalar(select(Supplier).where(Supplier.normalized_name == normalized))
        if supplier is None:
            supplier = Supplier(
                legal_name=name,
                normalized_name=normalized,
                supplier_type=SupplierType.CONSORTIUM if number == 3 else SupplierType.COMPANY,
                country="DO",
                registration_status="confirmed",
                is_public_entity=False,
                is_nonprofit=False,
                source_id=source.id,
                evidence_id=evidence.id,
                metadata_=marker,
            )
            db.add(supplier)
            db.flush()
        suppliers.append(supplier)
    processes: list[ProcurementProcess] = []
    for number, procedure, amount in (
        (1, ProcedureType.PRICE_COMPARISON, 100000),
        (2, ProcedureType.MINOR_PURCHASE, 50000),
    ):
        code = f"TEST-B7-2099-{number:03d}"
        process = db.scalar(
            select(ProcurementProcess).where(
                ProcurementProcess.institution_id == institution.id,
                ProcurementProcess.source_id == source.id,
                ProcurementProcess.process_code == code,
            )
        )
        if process is None:
            process = ProcurementProcess(
                institution_id=institution.id,
                organizational_unit_id=unit.id,
                procurement_unit_name="Unidad de Compras Ficticia",
                process_code=code,
                title=f"Proceso controlado de prueba {number}",
                procurement_type=ProcurementType.GOODS,
                procedure_type=procedure,
                process_status=ProcessStatus.AWARDED,
                publication_date=datetime(2099, number, 1, tzinfo=UTC),
                submission_deadline=datetime(2099, number, 10, tzinfo=UTC),
                opening_date=datetime(2099, number, 11, tzinfo=UTC),
                award_date=date(2099, number, 15),
                estimated_amount=amount,
                currency="DOP",
                fiscal_year=2099,
                territory_id=territory.id,
                legal_basis_id=legal_basis.id,
                source_id=source.id,
                evidence_id=evidence.id,
                raw_payload=marker,
                metadata_=marker,
                checksum=f"{number:064x}",
            )
            db.add(process)
            db.flush()
        processes.append(process)
    lot = db.scalar(
        select(ProcurementLot).where(ProcurementLot.procurement_process_id == processes[0].id)
    )
    if lot is None:
        lot = ProcurementLot(
            procurement_process_id=processes[0].id,
            lot_number="1",
            title="Lote ficticio",
            description="Bienes controlados para pruebas",
            estimated_amount=100000,
            awarded_amount=90000,
            currency="DOP",
            status="awarded",
            source_id=source.id,
            evidence_id=evidence.id,
            metadata_=marker,
        )
        db.add(lot)
        db.flush()
        for number in (1, 2):
            db.add(
                ProcurementItem(
                    procurement_process_id=processes[0].id,
                    lot_id=lot.id,
                    item_code=f"ITEM-TEST-{number}",
                    description=f"Ítem ficticio {number}",
                    quantity=10,
                    unit_of_measure="unidad",
                    estimated_unit_price=5000,
                    awarded_unit_price=4500,
                    estimated_total=50000,
                    awarded_total=45000,
                    currency="DOP",
                    source_id=source.id,
                    evidence_id=evidence.id,
                    metadata_=marker,
                )
            )
    bids: list[ProcurementBid] = []
    for supplier, amount in zip(suppliers[:2], (90000, 95000), strict=True):
        bid = db.scalar(
            select(ProcurementBid).where(
                ProcurementBid.procurement_process_id == processes[0].id,
                ProcurementBid.supplier_id == supplier.id,
            )
        )
        if bid is None:
            bid = ProcurementBid(
                procurement_process_id=processes[0].id,
                lot_id=lot.id,
                supplier_id=supplier.id,
                submission_date=datetime(2099, 1, 9, tzinfo=UTC),
                offered_amount=amount,
                currency="DOP",
                bid_status="selected" if amount == 90000 else "not_selected",
                technical_score=90,
                financial_score=90,
                total_score=90,
                is_compliant=True,
                source_id=source.id,
                evidence_id=evidence.id,
                metadata_=marker,
            )
            db.add(bid)
            db.flush()
        bids.append(bid)
    single_bid = db.scalar(
        select(ProcurementBid).where(ProcurementBid.procurement_process_id == processes[1].id)
    )
    if single_bid is None:
        single_bid = ProcurementBid(
            procurement_process_id=processes[1].id,
            supplier_id=suppliers[2].id,
            submission_date=datetime(2099, 2, 9, tzinfo=UTC),
            offered_amount=48000,
            currency="DOP",
            bid_status="evaluated",
            source_id=source.id,
            evidence_id=evidence.id,
            metadata_=marker,
        )
        db.add(single_bid)
    award = db.scalar(
        select(ProcurementAward).where(ProcurementAward.award_reference == "AWARD-TEST-B7-001")
    )
    if award is None:
        award = ProcurementAward(
            procurement_process_id=processes[0].id,
            lot_id=lot.id,
            supplier_id=suppliers[0].id,
            bid_id=bids[0].id,
            award_reference="AWARD-TEST-B7-001",
            award_date=date(2099, 1, 15),
            awarded_amount=90000,
            currency="DOP",
            award_status="confirmed",
            legal_basis_id=legal_basis.id,
            source_id=source.id,
            evidence_id=evidence.id,
            metadata_=marker,
        )
        db.add(award)
        db.flush()
    contract = db.scalar(
        select(ProcurementContract).where(
            ProcurementContract.contract_code == "CONTRACT-TEST-B7-001"
        )
    )
    if contract is None:
        contract = ProcurementContract(
            procurement_process_id=processes[0].id,
            award_id=award.id,
            institution_id=institution.id,
            supplier_id=suppliers[0].id,
            contract_code="CONTRACT-TEST-B7-001",
            title="Contrato ficticio controlado",
            signature_date=date(2099, 1, 20),
            start_date=date(2099, 1, 21),
            end_date=date(2099, 6, 30),
            original_amount=90000,
            current_amount=110000,
            paid_amount=40000,
            currency="DOP",
            contract_status="active",
            procurement_type=ProcurementType.GOODS,
            territory_id=territory.id,
            organizational_unit_id=unit.id,
            legal_basis_id=legal_basis.id,
            source_id=source.id,
            evidence_id=evidence.id,
            raw_payload=marker,
            metadata_=marker,
            checksum="7" * 64,
        )
        db.add(contract)
        db.flush()
    if (
        db.scalar(select(ContractAmendment).where(ContractAmendment.contract_id == contract.id))
        is None
    ):
        db.add(
            ContractAmendment(
                contract_id=contract.id,
                amendment_number="1",
                amendment_type="amount_increase",
                effective_date=date(2099, 3, 1),
                previous_amount=90000,
                new_amount=110000,
                description="Incremento ficticio controlado",
                legal_basis_id=legal_basis.id,
                source_id=source.id,
                evidence_id=evidence.id,
                status="confirmed",
                metadata_=marker,
            )
        )
    order = db.scalar(select(PurchaseOrder).where(PurchaseOrder.contract_id == contract.id))
    if order is None:
        order = PurchaseOrder(
            contract_id=contract.id,
            order_code="PO-TEST-B7-001",
            issue_date=date(2099, 1, 22),
            amount=90000,
            currency="DOP",
            status="issued",
            source_id=source.id,
            evidence_id=evidence.id,
            metadata_=marker,
        )
        db.add(order)
        db.flush()
    additions = (
        (
            ContractDelivery,
            dict(
                contract_id=contract.id,
                purchase_order_id=order.id,
                delivery_date=date(2099, 2, 15),
                acceptance_date=date(2099, 2, 16),
                delivered_amount=40000,
                accepted_amount=40000,
                status="accepted",
                description="Entrega ficticia controlada",
            ),
        ),
        (
            ContractPayment,
            dict(
                contract_id=contract.id,
                institution_id=institution.id,
                supplier_id=suppliers[0].id,
                payment_reference="PAY-TEST-B7-001",
                payment_date=date(2099, 2, 20),
                gross_amount=40000,
                deductions=0,
                net_amount=40000,
                currency="DOP",
                status="confirmed",
            ),
        ),
        (
            ContractGuarantee,
            dict(
                contract_id=contract.id,
                supplier_id=suppliers[0].id,
                guarantee_type="performance_bond",
                issuer_name="Emisor Ficticio de Prueba",
                amount=9000,
                currency="DOP",
                issue_date=date(2099, 1, 20),
                expiration_date=date(2099, 7, 30),
                status="active",
            ),
        ),
        (
            ProcurementChallenge,
            dict(
                procurement_process_id=processes[0].id,
                supplier_id=suppliers[1].id,
                challenge_type="review_request",
                filing_date=date(2099, 1, 16),
                decision_date=date(2099, 1, 19),
                status="decided",
                summary="Impugnación ficticia sin valoración jurídica",
                decision_summary="Decisión ficticia controlada",
            ),
        ),
    )
    for model, values in additions:
        if (
            db.scalar(select(model).where(model.source_id == source.id, model.metadata_ == marker))
            is None
        ):
            db.add(model(**values, source_id=source.id, evidence_id=evidence.id, metadata_=marker))
    for finding_type, process_id, observed in (
        ("single_bidder", processes[1].id, {"bidder_count": 1}),
        ("contract_growth", processes[0].id, {"growth_percentage": "22.22"}),
    ):
        if (
            db.scalar(
                select(ProcurementFinding).where(
                    ProcurementFinding.procurement_process_id == process_id,
                    ProcurementFinding.finding_type == finding_type,
                )
            )
            is None
        ):
            db.add(
                ProcurementFinding(
                    finding_type=finding_type,
                    severity="review_required",
                    institution_id=institution.id,
                    procurement_process_id=process_id,
                    contract_id=contract.id if finding_type == "contract_growth" else None,
                    supplier_id=suppliers[0].id if finding_type == "contract_growth" else None,
                    observed_value=observed,
                    explanation=(
                        "Señal ficticia para pruebas; no implica fraude, corrupción ni ilegalidad."
                    ),
                    evidence_id=evidence.id,
                    metadata_=marker,
                )
            )


def _seed_block8(
    db: Session,
    institution: Institution,
    source: Source,
    evidence: Evidence,
    legal_basis: LegalBasis,
) -> None:
    """Idempotent, controlled and entirely fictional Block 8 dataset."""
    marker = {"fictional": True, "seed": "block-8-controlled"}
    creditors: list[Creditor] = []
    for code, name, kind in (
        ("B8-CRED-A", "Fondo Multilateral Ficticio Alfa", "multilateral"),
        ("B8-CRED-B", "Banco Comercial Ficticio Beta", "commercial_bank"),
    ):
        item = db.scalar(select(Creditor).where(Creditor.normalized_name == code))
        if item is None:
            item = Creditor(
                legal_name=name,
                normalized_name=code,
                creditor_type=kind,
                is_domestic=False,
                is_public_entity=False,
                status="active",
                source_id=source.id,
                evidence_id=evidence.id,
                metadata_=marker,
            )
            db.add(item)
            db.flush()
        creditors.append(item)

    instruments: list[DebtInstrument] = []
    for code, title, kind, creditor, principal in (
        ("B8-LOAN-TEST-001", "Préstamo ficticio controlado", "loan", creditors[0], 1000000),
        ("B8-BOND-TEST-001", "Título ficticio controlado", "domestic_bond", creditors[1], 500000),
    ):
        debt_item = db.scalar(select(DebtInstrument).where(DebtInstrument.instrument_code == code))
        if debt_item is None:
            debt_item = DebtInstrument(
                debtor_institution_id=institution.id,
                creditor_id=creditor.id,
                instrument_code=code,
                title=title,
                instrument_type=kind,
                debt_scope="municipal",
                origin="external" if kind == "loan" else "domestic",
                currency="DOP",
                original_principal=principal,
                current_principal=principal,
                approved_amount=principal,
                effective_date=date(2099, 1, 1),
                maturity_date=date(2102, 12, 31),
                interest_type="fixed",
                nominal_interest_rate="5.25",
                payment_frequency="quarterly",
                status="active",
                legal_basis_id=legal_basis.id,
                source_id=source.id,
                evidence_id=evidence.id,
                raw_payload={"controlled": True},
                metadata_=marker,
            )
            db.add(debt_item)
            db.flush()
        instruments.append(debt_item)

    instrument = instruments[0]
    additions: tuple[tuple[Any, dict[str, object]], ...] = (
        (
            DebtTerm,
            {
                "debt_instrument_id": instrument.id,
                "valid_from": date(2099, 1, 1),
                "interest_type": "fixed",
                "nominal_rate": "5.25",
                "payment_frequency": "quarterly",
                "currency": "DOP",
            },
        ),
        (
            DebtDisbursement,
            {
                "debt_instrument_id": instrument.id,
                "debtor_institution_id": institution.id,
                "disbursement_reference": "B8-DISB-001",
                "disbursement_date": date(2099, 1, 10),
                "amount": 400000,
                "currency": "DOP",
                "status": "confirmed",
            },
        ),
        (
            DebtServiceSchedule,
            {
                "debt_instrument_id": instrument.id,
                "installment_number": 1,
                "due_date": date(2099, 4, 1),
                "principal_due": 100000,
                "interest_due": 12500,
                "fees_due": 0,
                "penalties_due": 0,
                "total_due": 112500,
                "currency": "DOP",
                "schedule_status": "partially_paid",
            },
        ),
        (
            DebtPayment,
            {
                "debt_instrument_id": instrument.id,
                "debtor_institution_id": institution.id,
                "creditor_id": creditors[0].id,
                "payment_reference": "B8-PAY-001",
                "payment_date": date(2099, 4, 1),
                "principal_paid": 50000,
                "interest_paid": 12500,
                "fees_paid": 0,
                "penalties_paid": 0,
                "total_paid": 62500,
                "currency": "DOP",
                "status": "confirmed",
            },
        ),
        (
            DebtBalanceSnapshot,
            {
                "debt_instrument_id": instrument.id,
                "snapshot_date": date(2099, 3, 31),
                "principal_outstanding": 950000,
                "interest_accrued": 12500,
                "arrears_principal": 0,
                "arrears_interest": 0,
                "fees_outstanding": 0,
                "total_outstanding": 962500,
                "currency": "DOP",
                "valuation_method": "nominal",
                "status": "confirmed",
            },
        ),
        (
            PublicGuarantee,
            {
                "guarantor_institution_id": institution.id,
                "guaranteed_entity_id": institution.id,
                "beneficiary_creditor_id": creditors[1].id,
                "guarantee_code": "B8-GUAR-001",
                "guarantee_type": "payment_guarantee",
                "issue_date": date(2099, 1, 1),
                "guaranteed_amount": 100000,
                "outstanding_exposure": 80000,
                "currency": "DOP",
                "status": "active",
                "legal_basis_id": legal_basis.id,
                "exception_documented": True,
            },
        ),
        (
            PublicObligation,
            {
                "institution_id": institution.id,
                "creditor_id": creditors[1].id,
                "obligation_code": "B8-OBL-001",
                "obligation_type": "accounts_payable",
                "description": "Obligación ficticia pendiente",
                "recognition_date": date(2099, 1, 1),
                "due_date": date(2099, 2, 1),
                "original_amount": 10000,
                "outstanding_amount": 7500,
                "paid_amount": 2500,
                "currency": "DOP",
                "status": "overdue",
                "legal_basis_id": legal_basis.id,
            },
        ),
        (
            PublicSubsidy,
            {
                "granting_institution_id": institution.id,
                "beneficiary_institution_id": institution.id,
                "subsidy_code": "B8-SUB-001",
                "subsidy_type": "institutional",
                "period_start": date(2099, 1, 1),
                "period_end": date(2099, 12, 31),
                "approved_amount": 20000,
                "paid_amount": 10000,
                "currency": "DOP",
                "purpose": "Subsidio ficticio controlado",
                "status": "active",
                "legal_basis_id": legal_basis.id,
            },
        ),
        (
            MultiYearCommitment,
            {
                "institution_id": institution.id,
                "commitment_code": "B8-MYC-001",
                "start_year": 2099,
                "end_year": 2100,
                "total_committed_amount": 30000,
                "currency": "DOP",
                "annual_breakdown": {"2099": 10000, "2100": 20000},
                "status": "active",
                "legal_basis_id": legal_basis.id,
            },
        ),
    )
    for model, values in additions:
        if db.scalar(select(model).where(model.metadata_ == marker)) is None:
            db.add(model(**values, source_id=source.id, evidence_id=evidence.id, metadata_=marker))
    if (
        db.scalar(
            select(FiscalRiskFinding).where(FiscalRiskFinding.debt_instrument_id == instrument.id)
        )
        is None
    ):
        db.add(
            FiscalRiskFinding(
                finding_type="upcoming_maturity",
                severity="informational",
                institution_id=institution.id,
                debt_instrument_id=instrument.id,
                observed_value={"controlled_test": True},
                explanation="Señal ficticia para revisión; no afirma ilegalidad ni corrupción.",
                evidence_id=evidence.id,
                metadata_=marker,
            )
        )


def _seed_block9(
    db: Session,
    institution: Institution,
    territory: Territory,
    source: Source,
    evidence: Evidence,
    legal_basis: LegalBasis,
) -> None:
    """Create only controlled, explicitly fictitious patrimony examples."""
    marker = {"controlled": True, "fictitious": True, "seed": "block-9"}
    category_specs = (
        ("B9-LAND", "Terreno ficticio de control", "land", False),
        ("B9-BUILDING", "Edificio ficticio de control", "building", True),
        ("B9-VEHICLE", "Vehículo ficticio de control", "vehicle", True),
        ("B9-TECH", "Tecnología ficticia de control", "technology", True),
        ("B9-FURNITURE", "Mobiliario ficticio de control", "furniture", True),
        ("B9-INTANGIBLE", "Intangible ficticio de control", "intangible", True),
        ("B9-CIP", "Obra en construcción ficticia", "construction_in_progress", False),
    )
    categories: dict[str, AssetCategory] = {}
    for code, name, kind, depreciable in category_specs:
        row = db.scalar(select(AssetCategory).where(AssetCategory.stable_code == code))
        if row is None:
            row = AssetCategory(
                stable_code=code,
                official_name=name,
                normalized_name=name.casefold(),
                category_type=kind,
                is_depreciable=depreciable,
                depreciation_method="straight_line" if depreciable else None,
                default_useful_life_years=5 if depreciable else None,
                status="confirmed",
                valid_from=date(2099, 1, 1),
                source_id=source.id,
                evidence_id=evidence.id,
                metadata_=marker,
            )
            db.add(row)
            db.flush()
        categories[kind] = row

    unit = db.scalar(
        select(OrganizationalUnit).where(OrganizationalUnit.institution_id == institution.id)
    )
    person = db.scalar(select(Person).where(Person.metadata_["controlled"].as_boolean() == True))  # noqa: E712
    location = db.scalar(
        select(AssetLocation).where(AssetLocation.official_name == "Almacén B9 ficticio")
    )
    if location is None:
        location = AssetLocation(
            institution_id=institution.id,
            territory_id=territory.id,
            organizational_unit_id=unit.id if unit else None,
            location_type="warehouse",
            official_name="Almacén B9 ficticio",
            status="active",
            is_restricted=True,
            source_id=source.id,
            evidence_id=evidence.id,
            metadata_=marker,
        )
        db.add(location)
        db.flush()

    asset_specs = (
        ("B9-ASSET-LAND-001", "Terreno ficticio B9", "land", "donation", 1000),
        ("B9-ASSET-BLD-001", "Edificio ficticio B9", "building", "construction", 800),
        ("B9-ASSET-VEH-001", "Vehículo ficticio B9 A", "vehicle", "purchase", 100),
        ("B9-ASSET-VEH-002", "Vehículo ficticio B9 B", "vehicle", "purchase", 120),
        ("B9-ASSET-TECH-001", "Equipo tecnológico ficticio B9", "technology", "purchase", 50),
        ("B9-ASSET-FURN-001", "Mobiliario ficticio B9", "furniture", "purchase", 25),
        ("B9-ASSET-LIC-001", "Licencia ficticia B9", "intangible", "purchase", 30),
        (
            "B9-ASSET-CIP-001",
            "Obra ficticia en construcción B9",
            "construction_in_progress",
            "construction",
            500,
        ),
        ("B9-ASSET-DISP-001", "Bien ficticio para baja B9", "furniture", "purchase", 10),
    )
    assets: dict[str, PublicAsset] = {}
    for code, name, kind, method, value in asset_specs:
        asset = db.scalar(select(PublicAsset).where(PublicAsset.asset_code == code))
        if asset is None:
            asset = PublicAsset(
                owner_institution_id=institution.id,
                managing_institution_id=institution.id,
                organizational_unit_id=unit.id if unit else None,
                asset_category_id=categories[kind].id,
                asset_code=code,
                official_name=name,
                normalized_name=name.casefold(),
                acquisition_method=method,
                acquisition_date=date(2099, 1, 1),
                original_cost=value,
                current_book_value=value,
                estimated_market_value=value,
                currency="DOP",
                quantity=1,
                unit_of_measure="unit",
                status="under_construction" if kind == "construction_in_progress" else "active",
                condition_status="good",
                ownership_status="owned",
                territory_id=territory.id,
                location_id=location.id,
                source_id=source.id,
                evidence_id=evidence.id,
                raw_payload={"controlled": True},
                metadata_=marker,
            )
            db.add(asset)
            db.flush()
        assets[code] = asset

    extensions: tuple[tuple[type[Any], str, dict[str, object]], ...] = (
        (
            RealEstateAsset,
            "B9-ASSET-LAND-001",
            {
                "property_type": "land",
                "land_area": 100,
                "unit_of_area": "m2",
                "title_status": "controlled",
                "occupancy_status": "idle",
                "encumbrance_status": "none",
            },
        ),
        (
            RealEstateAsset,
            "B9-ASSET-BLD-001",
            {
                "property_type": "building",
                "built_area": 80,
                "unit_of_area": "m2",
                "title_status": "controlled",
                "occupancy_status": "occupied",
                "encumbrance_status": "none",
                "parent_land_asset_id": assets["B9-ASSET-LAND-001"].id,
            },
        ),
        (
            VehicleAsset,
            "B9-ASSET-VEH-001",
            {
                "vehicle_type": "car",
                "plate_reference_masked": "TEST-***",
                "vin_hash": "a" * 64,
                "operational_status": "operational",
                "insurance_status": "insured",
            },
        ),
        (
            VehicleAsset,
            "B9-ASSET-VEH-002",
            {
                "vehicle_type": "pickup",
                "plate_reference_masked": "CTRL-***",
                "vin_hash": "b" * 64,
                "operational_status": "maintenance",
                "insurance_status": "uninsured",
            },
        ),
        (
            EquipmentAsset,
            "B9-ASSET-TECH-001",
            {
                "equipment_type": "computer",
                "serial_reference_hash": "c" * 64,
                "technical_specifications": {"controlled": True},
                "operational_status": "operational",
            },
        ),
        (
            EquipmentAsset,
            "B9-ASSET-FURN-001",
            {
                "equipment_type": "furniture",
                "technical_specifications": {"controlled": True},
                "operational_status": "operational",
            },
        ),
        (
            IntangibleAsset,
            "B9-ASSET-LIC-001",
            {
                "intangible_type": "software",
                "license_type": "controlled_test",
                "start_date": date(2099, 1, 1),
                "expiration_date": date(2099, 12, 31),
                "number_of_users": 5,
                "annual_cost": 30,
                "ownership_or_license_status": "licensed",
            },
        ),
        (
            InfrastructureAsset,
            "B9-ASSET-CIP-001",
            {
                "infrastructure_type": "public_building",
                "construction_start_date": date(2099, 1, 1),
                "physical_progress_percentage": 40,
                "financial_progress_percentage": 45,
            },
        ),
    )
    for model, code, values in extensions:
        if db.get(model, assets[code].id) is None:
            db.add(model(asset_id=assets[code].id, metadata_=marker, **values))

    assigned = assets["B9-ASSET-TECH-001"]
    if db.scalar(select(AssetAssignment).where(AssetAssignment.asset_id == assigned.id)) is None:
        db.add(
            AssetAssignment(
                asset_id=assigned.id,
                institution_id=institution.id,
                organizational_unit_id=unit.id if unit else None,
                person_id=person.id if person else None,
                assignment_type="custody",
                start_date=date(2099, 1, 1),
                status="active",
                responsibility_description="Custodia ficticia controlada.",
                source_id=source.id,
                evidence_id=evidence.id,
                metadata_=marker,
            )
        )
    if db.scalar(select(AssetEvent).where(AssetEvent.asset_id == assigned.id)) is None:
        db.add(
            AssetEvent(
                asset_id=assigned.id,
                institution_id=institution.id,
                event_type="relocated",
                event_date=date(2099, 2, 1),
                new_location_id=location.id,
                description="Traslado ficticio y controlado.",
                source_id=source.id,
                evidence_id=evidence.id,
                metadata_=marker,
            )
        )
    other = db.scalar(select(Institution).where(Institution.name == "Institución ficticia B9"))
    if other is None:
        other = Institution(
            name="Institución ficticia B9",
            kind="controlled_test",
            territory_id=territory.id,
            status=InstitutionStatus.DRAFT,
        )
        db.add(other)
        db.flush()
    other_link = db.scalar(
        select(InstitutionEvidence).where(
            InstitutionEvidence.institution_id == other.id,
            InstitutionEvidence.evidence_id == evidence.id,
        )
    )
    if other_link is None:
        db.add(InstitutionEvidence(institution_id=other.id, evidence_id=evidence.id))
    if (
        db.scalar(
            select(AssetTransfer).where(AssetTransfer.asset_id == assets["B9-ASSET-VEH-002"].id)
        )
        is None
    ):
        db.add(
            AssetTransfer(
                asset_id=assets["B9-ASSET-VEH-002"].id,
                origin_institution_id=institution.id,
                destination_institution_id=other.id,
                transfer_type="temporary",
                approval_date=date(2099, 2, 1),
                effective_date=date(2099, 2, 2),
                previous_book_value=120,
                transferred_value=120,
                currency="DOP",
                legal_basis_id=legal_basis.id,
                status="confirmed",
                description="Transferencia ficticia controlada.",
                source_id=source.id,
                evidence_id=evidence.id,
                metadata_=marker,
            )
        )
    if (
        db.scalar(
            select(AssetMaintenanceRecord).where(
                AssetMaintenanceRecord.asset_id == assets["B9-ASSET-VEH-001"].id
            )
        )
        is None
    ):
        db.add(
            AssetMaintenanceRecord(
                asset_id=assets["B9-ASSET-VEH-001"].id,
                institution_id=institution.id,
                maintenance_type="preventive",
                performed_date=date(2099, 2, 1),
                description="Mantenimiento ficticio controlado.",
                cost=5,
                currency="DOP",
                status="completed",
                source_id=source.id,
                evidence_id=evidence.id,
                metadata_=marker,
            )
        )
    for code in ("B9-ASSET-LAND-001", "B9-ASSET-VEH-001"):
        if (
            db.scalar(select(AssetValuation).where(AssetValuation.asset_id == assets[code].id))
            is None
        ):
            valuation_amount = assets[code].original_cost or Decimal("0")
            db.add(
                AssetValuation(
                    asset_id=assets[code].id,
                    valuation_date=date(2099, 2, 1),
                    valuation_type="accounting",
                    gross_value=valuation_amount,
                    accumulated_depreciation=0,
                    impairment_amount=0,
                    net_book_value=valuation_amount,
                    currency="DOP",
                    valuation_method="controlled_test",
                    source_id=source.id,
                    evidence_id=evidence.id,
                    metadata_=marker,
                )
            )
    if (
        db.scalar(
            select(AssetInsurancePolicy).where(
                AssetInsurancePolicy.asset_id == assets["B9-ASSET-VEH-001"].id
            )
        )
        is None
    ):
        db.add(
            AssetInsurancePolicy(
                asset_id=assets["B9-ASSET-VEH-001"].id,
                policy_reference_hash="d" * 64,
                coverage_type="controlled_test",
                coverage_start=date(2099, 1, 1),
                coverage_end=date(2099, 12, 31),
                insured_value=100,
                premium_amount=2,
                currency="DOP",
                status="active",
                source_id=source.id,
                evidence_id=evidence.id,
                metadata_=marker,
            )
        )
    inventory = db.scalar(
        select(PhysicalInventory).where(PhysicalInventory.inventory_code == "B9-INV-001")
    )
    if inventory is None:
        inventory = PhysicalInventory(
            institution_id=institution.id,
            location_id=location.id,
            inventory_code="B9-INV-001",
            inventory_date=date(2099, 3, 1),
            scope="Inventario físico ficticio controlado.",
            status="confirmed",
            expected_asset_count=2,
            observed_asset_count=1,
            matched_count=1,
            missing_count=1,
            surplus_count=0,
            source_id=source.id,
            evidence_id=evidence.id,
            metadata_=marker,
        )
        db.add(inventory)
        db.flush()
        db.add_all(
            [
                PhysicalInventoryItem(
                    physical_inventory_id=inventory.id,
                    asset_id=assets["B9-ASSET-TECH-001"].id,
                    observed_reference="CONTROL-OBS-001",
                    observed_name="Equipo tecnológico ficticio B9",
                    observed_condition="good",
                    observed_location_id=location.id,
                    match_status="matched",
                    evidence_id=evidence.id,
                    metadata_=marker,
                ),
                PhysicalInventoryItem(
                    physical_inventory_id=inventory.id,
                    asset_id=assets["B9-ASSET-FURN-001"].id,
                    observed_reference="CONTROL-OBS-002",
                    observed_name="Mobiliario ficticio B9",
                    observed_condition="unknown",
                    match_status="missing",
                    discrepancy_type="missing",
                    notes="Diferencia controlada; no implica robo ni conducta ilícita.",
                    evidence_id=evidence.id,
                    metadata_=marker,
                ),
            ]
        )
    disposable = assets["B9-ASSET-DISP-001"]
    if db.scalar(select(AssetDisposal).where(AssetDisposal.asset_id == disposable.id)) is None:
        db.add(
            AssetDisposal(
                asset_id=disposable.id,
                institution_id=institution.id,
                disposal_type="write_off",
                approval_date=date(2099, 4, 1),
                effective_date=date(2099, 4, 2),
                book_value=10,
                disposal_value=0,
                currency="DOP",
                reason="Baja ficticia para pruebas.",
                legal_basis_id=legal_basis.id,
                status="completed",
                source_id=source.id,
                evidence_id=evidence.id,
                metadata_=marker,
            )
        )
    if db.scalar(select(AssetFinding).where(AssetFinding.inventory_id == inventory.id)) is None:
        db.add(
            AssetFinding(
                finding_type="missing_asset",
                severity="review_required",
                institution_id=institution.id,
                asset_id=assets["B9-ASSET-FURN-001"].id,
                inventory_id=inventory.id,
                observed_value={"present": False, "controlled_test": True},
                expected_or_previous_value={"present": True},
                explanation="Señal ficticia observable; no afirma robo, fraude ni corrupción.",
                evidence_id=evidence.id,
                metadata_=marker,
            )
        )


def main() -> None:
    with SessionLocal() as db:
        seed(db)


if __name__ == "__main__":
    main()
