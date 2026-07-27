import math
import unicodedata
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.modules.appointments.models import Appointment, AppointmentStatus
from app.modules.budget.models import (
    BudgetAppropriation,
    BudgetExecutionRecord,
    BudgetProgram,
    BudgetStatus,
)
from app.modules.employment_relationships.models import EmploymentRelationship
from app.modules.evidence.models import Evidence
from app.modules.institutions.models import Institution, InstitutionEvidence, InstitutionStatus
from app.modules.legal_basis.models import LegalBasis
from app.modules.organizational_units.models import OrganizationalEvent, OrganizationalUnit
from app.modules.payroll_entries.models import PayrollEntry, PayrollEntryStatus
from app.modules.payroll_periods.models import PayrollPeriod, PayrollPeriodStatus
from app.modules.persons.models import Person, PersonStatus
from app.modules.positions.models import Position, PositionStatus
from app.modules.procurement_processes.models import ProcurementContract, ProcurementProcess
from app.modules.public_assets.models import AssetValuation, PublicAsset
from app.modules.public_debt.models import DebtBalanceSnapshot, DebtInstrument, DebtPayment
from app.modules.risk_engine.models import RiskFinding, RiskType
from app.modules.sources.models import Source
from app.modules.suppliers.models import Supplier
from app.modules.territories.models import Territory

NEVER_PUBLIC = frozenset(
    {
        "raw_payload",
        "reviewer_notes",
        "internal_explanation",
        "internal_message_template",
        "metadata_",
        "national_id_hash",
        "tax_id_hash",
        "registration_hash",
        "vin_hash",
        "serial_hash",
        "policy_hash",
        "content_hash",
        "contract_reference",
        "external_reference",
        "registry_reference_hash",
        "employee_reference_hash",
        "national_id",
        "cedula",
        "cédula",
        "rnc",
        "vin",
        "serial",
        "policy_number",
        "restricted_address",
        "work_location",
        "internal_finding",
        "ai_proposal",
    }
)


def now() -> datetime:
    return datetime.now(UTC)


def normalize_query(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip()
    return " ".join(normalized.split())


def pagination(page: int, page_size: int, total: int) -> dict[str, Any]:
    pages = math.ceil(total / page_size) if total else 0
    return {
        "page": page,
        "page_size": page_size,
        "total_items": total,
        "total_pages": pages,
        "has_next": page < pages,
        "has_previous": page > 1,
    }


def collection(
    data: list[dict[str, Any]],
    page: int,
    page_size: int,
    total: int,
    filters: dict[str, Any] | None = None,
    sort: str = "name",
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "data": data,
        "pagination": pagination(page, page_size, total),
        "filters_applied": filters or {},
        "sort": sort,
        "generated_at": now(),
        "source_freshness": "unknown",
        "warnings": warnings or [],
    }


def empty(page: int, page_size: int, domain: str) -> dict[str, Any]:
    return collection(
        [], page, page_size, 0, warnings=[f"No hay datos públicos disponibles para {domain}."]
    )


def institution_dict(row: Institution) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "name": row.name,
        "kind": row.kind,
        "territory_id": str(row.territory_id),
        "status": str(row.status.value),
    }


def list_institutions(
    db: Session, page: int, page_size: int, q: str | None, sort: str
) -> dict[str, Any]:
    query = select(Institution).where(Institution.status == InstitutionStatus.CONFIRMED)
    count = (
        select(func.count())
        .select_from(Institution)
        .where(Institution.status == InstitutionStatus.CONFIRMED)
    )
    filters: dict[str, Any] = {}
    if q:
        term = normalize_query(q)
        query = query.where(Institution.name.ilike(f"%{term}%"))
        count = count.where(Institution.name.ilike(f"%{term}%"))
        filters["q"] = term
    order = Institution.name.desc() if sort == "-name" else Institution.name.asc()
    total = db.scalar(count) or 0
    rows = db.scalars(query.order_by(order).offset((page - 1) * page_size).limit(page_size))
    return collection(
        [institution_dict(row) for row in rows], page, page_size, total, filters, sort
    )


def get_institution(db: Session, institution_id: uuid.UUID) -> dict[str, Any] | None:
    row = db.scalar(
        select(Institution).where(
            Institution.id == institution_id,
            Institution.status == InstitutionStatus.CONFIRMED,
        )
    )
    return institution_dict(row) if row else None


def public_findings(
    db: Session, page: int, page_size: int, institution_id: uuid.UUID | None = None
) -> dict[str, Any]:
    conditions = [RiskFinding.visibility == "public", RiskFinding.status == "published"]
    if institution_id:
        conditions.append(RiskFinding.institution_id == institution_id)
    query = select(RiskFinding).where(*conditions)
    total = db.scalar(select(func.count()).select_from(RiskFinding).where(*conditions)) or 0
    rows = db.scalars(
        query.order_by(RiskFinding.last_detected_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    data = [
        {
            "id": str(row.id),
            "code": row.finding_code,
            "domain": row.domain,
            "entity_type": row.entity_type,
            "entity_id": str(row.entity_id),
            "institution_id": str(row.institution_id) if row.institution_id else None,
            "title": row.title,
            "explanation": row.public_explanation,
            "severity": row.severity,
            "period_start": row.period_start,
            "period_end": row.period_end,
            "last_detected_at": row.last_detected_at,
        }
        for row in rows
    ]
    return collection(data, page, page_size, total, sort="-last_detected_at")


def search(
    db: Session, q: str, page: int, page_size: int, entity_type: str | None
) -> dict[str, Any]:
    term = normalize_query(q)
    pattern = f"%{term}%"
    results: list[dict[str, Any]] = []
    if entity_type in (None, "institution"):
        institution_rows = db.scalars(
            select(Institution)
            .where(
                Institution.status == InstitutionStatus.CONFIRMED,
                Institution.name.ilike(pattern),
            )
            .order_by(Institution.name)
            .limit(page_size + 1)
        )
        results.extend(
            {
                "id": str(row.id),
                "entity_type": "institution",
                "title": row.name,
                "subtitle": row.kind,
                "url": f"/instituciones/{row.id}",
                "score": 1.0 if row.name.casefold() == term.casefold() else 0.7,
            }
            for row in institution_rows
        )
    if entity_type in (None, "territory"):
        territory_rows = db.scalars(
            select(Territory)
            .where(Territory.name.ilike(pattern))
            .order_by(Territory.name)
            .limit(20)
        )
        results.extend(
            {
                "id": str(row.id),
                "entity_type": "territory",
                "title": row.name,
                "subtitle": row.type.value,
                "url": f"/territorios/{row.id}",
                "score": 0.65,
            }
            for row in territory_rows
        )
    results.sort(key=lambda item: (-float(item["score"]), str(item["title"])))
    start = (page - 1) * page_size
    return collection(
        results[start : start + page_size],
        page,
        page_size,
        len(results),
        {"q": term, **({"entity_type": entity_type} if entity_type else {})},
        "-score",
    )


def counts(db: Session) -> dict[str, int]:
    return {
        "institutions": db.scalar(
            select(func.count())
            .select_from(Institution)
            .where(Institution.status == InstitutionStatus.CONFIRMED)
        )
        or 0,
        "territories": db.scalar(select(func.count()).select_from(Territory)) or 0,
        "people": db.scalar(select(func.count()).select_from(Person)) or 0,
        "positions": db.scalar(select(func.count()).select_from(Position)) or 0,
        "public_findings": db.scalar(
            select(func.count())
            .select_from(RiskFinding)
            .where(RiskFinding.visibility == "public", RiskFinding.status == "published")
        )
        or 0,
    }


def risk_summary(db: Session) -> dict[str, Any]:
    rows = list(
        db.execute(
            select(RiskFinding.domain, RiskFinding.severity, func.count(RiskFinding.id))
            .where(RiskFinding.visibility == "public", RiskFinding.status == "published")
            .group_by(RiskFinding.domain, RiskFinding.severity)
            .order_by(RiskFinding.domain, RiskFinding.severity)
        )
    )
    total = sum(count for _, _, count in rows)
    return _summary(
        {
            "total_public_findings": total,
            "breakdown": [
                {"domain": domain, "severity": severity, "count": count}
                for domain, severity, count in rows
            ],
        },
        bool(total),
    )


def taxonomy(db: Session, page: int, page_size: int) -> dict[str, Any]:
    query = select(RiskType).where(RiskType.status == "active")
    total = (
        db.scalar(select(func.count()).select_from(RiskType).where(RiskType.status == "active"))
        or 0
    )
    rows = db.scalars(
        query.order_by(RiskType.official_name).offset((page - 1) * page_size).limit(page_size)
    )
    data = [
        {
            "id": str(row.id),
            "code": row.stable_code,
            "name": row.official_name,
            "description": row.description,
            "domain": row.domain,
            "category": row.category,
            "default_severity": row.default_severity,
        }
        for row in rows
    ]
    return collection(data, page, page_size, total)


def _number(value: Decimal | int | float | None) -> float | int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    return float(value)


def _availability(has_data: bool, *, stale: bool = False, review: bool = False) -> str:
    if review:
        return "under_review"
    if stale:
        return "stale"
    return "available" if has_data else "not_available"


def _domain_collection(
    rows: list[dict[str, Any]], page: int, page_size: int, domain: str, sort: str
) -> dict[str, Any]:
    start = (page - 1) * page_size
    warning = [] if rows else [f"No hay datos públicos disponibles para {domain}."]
    result = collection(
        rows[start : start + page_size], page, page_size, len(rows), sort=sort, warnings=warning
    )
    result["availability"] = _availability(bool(rows))
    return result


def institution_section(
    db: Session, institution_id: uuid.UUID, section: str, page: int, page_size: int
) -> dict[str, Any]:
    rows: list[dict[str, Any]]
    if section == "history":
        events = db.scalars(
            select(OrganizationalEvent)
            .where(OrganizationalEvent.institution_id == institution_id)
            .order_by(OrganizationalEvent.effective_date.desc())
        )
        rows = [
            {
                "id": str(row.id),
                "event_type": row.event_type.value,
                "effective_date": row.effective_date,
                "unit_id": str(row.unit_id),
                "previous_name": row.previous_name,
                "new_name": row.new_name,
                "description": row.description,
                "legal_basis_id": str(row.legal_basis_id),
                "source_id": str(row.source_id),
            }
            for row in events
        ]
        return _domain_collection(rows, page, page_size, section, "-effective_date")
    if section == "structure":
        units = db.scalars(
            select(OrganizationalUnit)
            .where(
                OrganizationalUnit.institution_id == institution_id,
                OrganizationalUnit.status.in_(["CANONICAL", "INACTIVE"]),
            )
            .order_by(OrganizationalUnit.hierarchy_level, OrganizationalUnit.order_index)
        )
        rows = [
            {
                "id": str(row.id),
                "parent_id": str(row.parent_unit_id) if row.parent_unit_id else None,
                "name": row.official_name,
                "acronym": row.acronym,
                "unit_type": row.unit_type.value,
                "hierarchy_level": row.hierarchy_level,
                "status": row.status.value,
                "valid_from": row.valid_from,
                "valid_to": row.valid_to,
                "legal_basis_id": str(row.legal_basis_id) if row.legal_basis_id else None,
            }
            for row in units
        ]
        return _domain_collection(rows, page, page_size, section, "hierarchy_level")
    if section == "positions":
        positions = db.scalars(
            select(Position)
            .where(
                Position.institution_id == institution_id,
                Position.status.in_([PositionStatus.CANONICAL, PositionStatus.INACTIVE]),
            )
            .order_by(Position.official_name)
        )
        rows = [
            {
                "id": str(row.id),
                "name": row.official_name,
                "position_type": row.position_type,
                "hierarchy_level": row.hierarchy_level,
                "access_method": row.access_method.value,
                "unit_id": str(row.organizational_unit_id) if row.organizational_unit_id else None,
                "status": row.status.value,
                "valid_from": row.valid_from,
                "valid_to": row.valid_to,
                "legal_basis_id": str(row.legal_basis_id),
            }
            for row in positions
        ]
        return _domain_collection(rows, page, page_size, section, "name")
    if section == "employment":
        relationships = db.scalars(
            select(EmploymentRelationship)
            .where(
                EmploymentRelationship.institution_id == institution_id,
                EmploymentRelationship.relationship_status != "PENDING",
            )
            .order_by(EmploymentRelationship.start_date.desc())
        )
        rows = [
            {
                "id": str(row.id),
                "person_id": str(row.person_id),
                "position_id": str(row.position_id) if row.position_id else None,
                "unit_id": str(row.organizational_unit_id) if row.organizational_unit_id else None,
                "employment_type": row.employment_type.value,
                "status": row.relationship_status.value,
                "start_date": row.start_date,
                "end_date": row.end_date,
                "source_id": str(row.source_id),
            }
            for row in relationships
        ]
        return _domain_collection(rows, page, page_size, section, "-start_date")
    if section == "payroll":
        return payroll_records(db, page, page_size, institution_id)
    if section == "budget":
        return budget_execution(db, page, page_size, institution_id)
    if section == "procurement":
        return procurement_contracts(db, page, page_size, institution_id)
    if section == "debt":
        return debt_instruments(db, page, page_size, institution_id)
    if section == "assets":
        return assets(db, page, page_size, institution_id)
    if section == "sources":
        sources = db.execute(
            select(Source, Evidence.title, Evidence.observed_at, InstitutionEvidence.relation)
            .join(Evidence, Evidence.source_id == Source.id)
            .join(InstitutionEvidence, InstitutionEvidence.evidence_id == Evidence.id)
            .where(InstitutionEvidence.institution_id == institution_id)
            .order_by(Source.retrieved_at.desc())
        )
        rows = [
            {
                "id": str(source.id),
                "name": source.name,
                "url": source.url,
                "publisher": source.publisher,
                "is_official": source.is_official,
                "retrieved_at": source.retrieved_at,
                "evidence_title": title,
                "observed_at": observed_at,
                "relation": relation,
            }
            for source, title, observed_at, relation in sources
        ]
        return _domain_collection(rows, page, page_size, section, "-retrieved_at")
    return empty(page, page_size, section)


def institution_profile(db: Session, institution_id: uuid.UUID) -> dict[str, Any] | None:
    base = get_institution(db, institution_id)
    if base is None:
        return None
    legal = db.execute(
        select(LegalBasis)
        .join(Evidence, Evidence.id == LegalBasis.evidence_id)
        .join(InstitutionEvidence, InstitutionEvidence.evidence_id == Evidence.id)
        .where(InstitutionEvidence.institution_id == institution_id)
        .order_by(LegalBasis.effective_from.desc().nullslast())
        .limit(1)
    ).scalar_one_or_none()
    domains = {
        "employment": (EmploymentRelationship, EmploymentRelationship.institution_id),
        "payroll": (PayrollPeriod, PayrollPeriod.institution_id),
        "budget": (BudgetAppropriation, BudgetAppropriation.institution_id),
        "procurement": (ProcurementProcess, ProcurementProcess.institution_id),
        "debt": (DebtInstrument, DebtInstrument.debtor_institution_id),
        "assets": (PublicAsset, PublicAsset.owner_institution_id),
    }
    counts_by_domain: dict[str, int] = {}
    for name, (model, column) in domains.items():
        counts_by_domain[name] = (
            db.scalar(select(func.count()).select_from(model).where(column == institution_id)) or 0
        )
    latest = db.scalar(
        select(func.max(Source.retrieved_at))
        .join(Evidence, Evidence.source_id == Source.id)
        .join(InstitutionEvidence, InstitutionEvidence.evidence_id == Evidence.id)
        .where(InstitutionEvidence.institution_id == institution_id)
    )
    return {
        **base,
        "legal_basis": (
            {
                "title": legal.title,
                "instrument_type": legal.instrument_type.value,
                "reference": legal.reference,
                "article": legal.article,
                "official_url": legal.official_url,
                "effective_from": legal.effective_from,
            }
            if legal
            else None
        ),
        "parent_institution": None,
        "metrics": {key: value for key, value in counts_by_domain.items()},
        "coverage": {
            key: ("complete" if value > 0 else "not_available")
            for key, value in counts_by_domain.items()
        },
        "data_quality": "reviewed" if latest else "under_review",
        "last_updated": latest,
    }


def payroll_records(
    db: Session, page: int, page_size: int, institution_id: uuid.UUID | None = None
) -> dict[str, Any]:
    conditions = [PayrollEntry.status == PayrollEntryStatus.CONFIRMED]
    if institution_id:
        conditions.append(PayrollEntry.institution_id == institution_id)
    rows = db.execute(
        select(PayrollEntry, PayrollPeriod)
        .join(PayrollPeriod, PayrollPeriod.id == PayrollEntry.payroll_period_id)
        .where(*conditions, PayrollPeriod.status == PayrollPeriodStatus.CONFIRMED)
        .order_by(PayrollPeriod.period_end.desc(), PayrollEntry.listed_name)
    )
    data = [
        {
            "id": str(entry.id),
            "institution_id": str(entry.institution_id),
            "period": f"{period.year:04d}-{period.month:02d}",
            "listed_name": entry.listed_name,
            "position_id": str(entry.position_id) if entry.position_id else None,
            "employment_type": entry.employment_type,
            "gross_income": _number(entry.gross_income),
            "total_deductions": _number(entry.total_deductions),
            "net_income": _number(entry.net_income),
            "currency": entry.currency,
            "source_id": str(entry.source_id),
        }
        for entry, period in rows
    ]
    return _domain_collection(data, page, page_size, "payroll", "-period")


def budget_execution(
    db: Session, page: int, page_size: int, institution_id: uuid.UUID | None = None
) -> dict[str, Any]:
    conditions = [BudgetExecutionRecord.status == BudgetStatus.CONFIRMED]
    if institution_id:
        conditions.append(BudgetExecutionRecord.institution_id == institution_id)
    records = db.scalars(
        select(BudgetExecutionRecord)
        .where(*conditions)
        .order_by(BudgetExecutionRecord.period_end.desc())
    )
    data = [
        {
            "id": str(row.id),
            "institution_id": str(row.institution_id),
            "period": row.execution_period,
            "period_start": row.period_start,
            "period_end": row.period_end,
            "initial_budget": _number(row.initial_budget),
            "current_budget": _number(row.current_budget),
            "committed_amount": _number(row.committed_amount),
            "accrued_amount": _number(row.accrued_amount),
            "paid_amount": _number(row.paid_amount),
            "available_balance": _number(row.available_balance),
            "currency": row.currency,
            "source_id": str(row.source_id),
        }
        for row in records
    ]
    return _domain_collection(data, page, page_size, "budget", "-period")


def procurement_contracts(
    db: Session, page: int, page_size: int, institution_id: uuid.UUID | None = None
) -> dict[str, Any]:
    conditions = [ProcurementContract.validation_status == "confirmed"]
    if institution_id:
        conditions.append(ProcurementContract.institution_id == institution_id)
    records = db.scalars(
        select(ProcurementContract)
        .where(*conditions)
        .order_by(ProcurementContract.signature_date.desc())
    )
    data = [
        {
            "id": str(row.id),
            "institution_id": str(row.institution_id),
            "process_id": str(row.procurement_process_id),
            "supplier_id": str(row.supplier_id),
            "code": row.contract_code,
            "title": row.title,
            "signature_date": row.signature_date,
            "start_date": row.start_date,
            "end_date": row.end_date,
            "original_amount": _number(row.original_amount),
            "current_amount": _number(row.current_amount),
            "paid_amount": _number(row.paid_amount),
            "currency": row.currency,
            "status": row.contract_status,
            "source_id": str(row.source_id),
        }
        for row in records
    ]
    return _domain_collection(data, page, page_size, "procurement", "-signature_date")


def debt_instruments(
    db: Session, page: int, page_size: int, institution_id: uuid.UUID | None = None
) -> dict[str, Any]:
    conditions = [DebtInstrument.validation_status == "confirmed"]
    if institution_id:
        conditions.append(DebtInstrument.debtor_institution_id == institution_id)
    records = db.scalars(
        select(DebtInstrument).where(*conditions).order_by(DebtInstrument.effective_date.desc())
    )
    data = [
        {
            "id": str(row.id),
            "institution_id": str(row.debtor_institution_id),
            "creditor_id": str(row.creditor_id),
            "title": row.title,
            "instrument_type": row.instrument_type,
            "currency": row.currency,
            "original_principal": _number(row.original_principal),
            "current_principal": _number(row.current_principal),
            "effective_date": row.effective_date,
            "maturity_date": row.maturity_date,
            "status": row.status,
            "source_id": str(row.source_id),
        }
        for row in records
    ]
    return _domain_collection(data, page, page_size, "debt", "-effective_date")


def assets(
    db: Session, page: int, page_size: int, institution_id: uuid.UUID | None = None
) -> dict[str, Any]:
    conditions = [PublicAsset.validation_status == "confirmed"]
    if institution_id:
        conditions.append(
            or_(
                PublicAsset.owner_institution_id == institution_id,
                PublicAsset.managing_institution_id == institution_id,
            )
        )
    records = db.scalars(select(PublicAsset).where(*conditions).order_by(PublicAsset.official_name))
    data = [
        {
            "id": str(row.id),
            "owner_institution_id": str(row.owner_institution_id),
            "managing_institution_id": (
                str(row.managing_institution_id) if row.managing_institution_id else None
            ),
            "category_id": str(row.asset_category_id),
            "name": row.official_name,
            "acquisition_date": row.acquisition_date,
            "current_book_value": _number(row.current_book_value),
            "estimated_market_value": _number(row.estimated_market_value),
            "currency": row.currency,
            "quantity": _number(row.quantity),
            "status": row.status,
            "condition": row.condition_status,
            "territory_id": str(row.territory_id) if row.territory_id else None,
            "source_id": str(row.source_id),
        }
        for row in records
    ]
    return _domain_collection(data, page, page_size, "assets", "name")


def _summary(data: dict[str, Any], has_data: bool, period: object = None) -> dict[str, Any]:
    return {
        "data": data,
        "availability": _availability(has_data),
        "period": period,
        "generated_at": now(),
        "source_freshness": "available" if has_data else "not_available",
        "warnings": []
        if has_data
        else ["No hay datos confirmados para los filtros seleccionados."],
    }


def aggregate(db: Session, domain: str, institution_id: uuid.UUID | None = None) -> dict[str, Any]:
    if domain.startswith("payroll/"):
        conditions = [
            PayrollEntry.status == PayrollEntryStatus.CONFIRMED,
            PayrollPeriod.status == PayrollPeriodStatus.CONFIRMED,
        ]
        if institution_id:
            conditions.append(PayrollEntry.institution_id == institution_id)
        grouped = list(
            db.execute(
                select(
                    PayrollPeriod.year,
                    PayrollPeriod.month,
                    PayrollEntry.currency,
                    func.count(PayrollEntry.id),
                    func.sum(PayrollEntry.gross_income),
                    func.sum(PayrollEntry.total_deductions),
                    func.sum(PayrollEntry.net_income),
                )
                .join(PayrollPeriod, PayrollPeriod.id == PayrollEntry.payroll_period_id)
                .where(*conditions)
                .group_by(PayrollPeriod.year, PayrollPeriod.month, PayrollEntry.currency)
                .order_by(PayrollPeriod.year, PayrollPeriod.month)
            )
        )
        series = [
            {
                "period": f"{year:04d}-{month:02d}",
                "employee_count": count,
                "gross_total": _number(gross),
                "deductions_total": _number(deductions),
                "net_total": _number(net),
                "currency": currency,
                "status": "available",
            }
            for year, month, currency, count, gross, deductions, net in grouped
        ]
        latest = series[-1] if series else None
        return _summary(
            {"latest": latest, "series": series, "comparison": series[-2:]},
            bool(series),
            latest["period"] if latest else None,
        )
    if domain.startswith("budget/"):
        conditions = [BudgetExecutionRecord.status == BudgetStatus.CONFIRMED]
        if institution_id:
            conditions.append(BudgetExecutionRecord.institution_id == institution_id)
        grouped = list(
            db.execute(
                select(
                    BudgetExecutionRecord.period_end,
                    BudgetExecutionRecord.currency,
                    func.sum(BudgetExecutionRecord.current_budget),
                    func.sum(BudgetExecutionRecord.accrued_amount),
                    func.sum(BudgetExecutionRecord.paid_amount),
                )
                .where(*conditions)
                .group_by(BudgetExecutionRecord.period_end, BudgetExecutionRecord.currency)
                .order_by(BudgetExecutionRecord.period_end)
            )
        )
        series = [
            {
                "period": str(period),
                "current_budget": _number(current),
                "accrued_amount": _number(accrued),
                "paid_amount": _number(paid),
                "execution_rate": (
                    float(accrued / current * 100) if current not in (None, 0) else None
                ),
                "currency": currency,
                "status": "available",
            }
            for period, currency, current, accrued, paid in grouped
        ]
        latest = series[-1] if series else None
        return _summary(
            {"latest": latest, "series": series, "comparison": series[-2:]},
            bool(series),
            latest["period"] if latest else None,
        )
    if domain == "procurement/metrics":
        conditions = [ProcurementContract.validation_status == "confirmed"]
        if institution_id:
            conditions.append(ProcurementContract.institution_id == institution_id)
        count, contracted, paid, suppliers = db.execute(
            select(
                func.count(ProcurementContract.id),
                func.sum(ProcurementContract.current_amount),
                func.sum(ProcurementContract.paid_amount),
                func.count(func.distinct(ProcurementContract.supplier_id)),
            ).where(*conditions)
        ).one()
        return _summary(
            {
                "contract_count": count,
                "contracted_amount": _number(contracted),
                "paid_amount": _number(paid),
                "supplier_count": suppliers,
            },
            bool(count),
        )
    if domain.startswith("debt/"):
        instrument_conditions = [DebtInstrument.validation_status == "confirmed"]
        if institution_id:
            instrument_conditions.append(DebtInstrument.debtor_institution_id == institution_id)
        instruments = list(db.scalars(select(DebtInstrument).where(*instrument_conditions)))
        ids = [row.id for row in instruments]
        balances = (
            list(
                db.execute(
                    select(
                        DebtBalanceSnapshot.snapshot_date,
                        DebtBalanceSnapshot.currency,
                        func.sum(DebtBalanceSnapshot.total_outstanding),
                    )
                    .where(DebtBalanceSnapshot.debt_instrument_id.in_(ids))
                    .group_by(DebtBalanceSnapshot.snapshot_date, DebtBalanceSnapshot.currency)
                    .order_by(DebtBalanceSnapshot.snapshot_date)
                )
            )
            if ids
            else []
        )
        payments = (
            list(
                db.execute(
                    select(
                        DebtPayment.payment_date,
                        DebtPayment.currency,
                        func.sum(DebtPayment.total_paid),
                    )
                    .where(DebtPayment.debt_instrument_id.in_(ids))
                    .group_by(DebtPayment.payment_date, DebtPayment.currency)
                    .order_by(DebtPayment.payment_date)
                )
            )
            if ids
            else []
        )
        return _summary(
            {
                "instrument_count": len(instruments),
                "current_principal": _number(
                    sum((row.current_principal for row in instruments), Decimal(0))
                )
                if instruments
                else None,
                "balances": [
                    {
                        "period": str(period),
                        "total_outstanding": _number(value),
                        "currency": currency,
                        "status": "available",
                    }
                    for period, currency, value in balances
                ],
                "service": [
                    {
                        "period": str(period),
                        "total_paid": _number(value),
                        "currency": currency,
                        "status": "available",
                    }
                    for period, currency, value in payments
                ],
            },
            bool(instruments),
        )
    if domain.startswith("assets/"):
        conditions = [PublicAsset.validation_status == "confirmed"]
        if institution_id:
            conditions.append(PublicAsset.owner_institution_id == institution_id)
        asset_rows = list(db.scalars(select(PublicAsset).where(*conditions)))
        ids = [row.id for row in asset_rows]
        valuations = (
            list(
                db.execute(
                    select(
                        AssetValuation.valuation_date,
                        AssetValuation.currency,
                        func.sum(AssetValuation.net_book_value),
                        func.sum(AssetValuation.market_value),
                    )
                    .where(AssetValuation.asset_id.in_(ids))
                    .group_by(AssetValuation.valuation_date, AssetValuation.currency)
                    .order_by(AssetValuation.valuation_date)
                )
            )
            if ids
            else []
        )
        return _summary(
            {
                "asset_count": len(asset_rows),
                "book_value": _number(
                    sum(
                        (
                            row.current_book_value
                            for row in asset_rows
                            if row.current_book_value is not None
                        ),
                        Decimal(0),
                    )
                )
                if asset_rows
                else None,
                "series": [
                    {
                        "period": str(period),
                        "net_book_value": _number(book),
                        "market_value": _number(market),
                        "currency": currency,
                        "status": "available",
                    }
                    for period, currency, book, market in valuations
                ],
            },
            bool(asset_rows),
        )
    raise ValueError(f"Unsupported aggregate: {domain}")


def general_collection(db: Session, domain: str, page: int, page_size: int) -> dict[str, Any]:
    if domain == "payroll/records":
        return payroll_records(db, page, page_size)
    if domain == "budget/execution":
        return budget_execution(db, page, page_size)
    if domain == "procurement/contracts":
        return procurement_contracts(db, page, page_size)
    if domain == "debt/instruments":
        return debt_instruments(db, page, page_size)
    if domain == "assets":
        return assets(db, page, page_size)
    if domain in {
        "payroll/summary",
        "payroll/evolution",
        "payroll/comparison",
        "budget/summary",
        "budget/evolution",
        "budget/comparison",
        "procurement/metrics",
        "debt/summary",
        "debt/service",
        "debt/evolution",
        "assets/summary",
        "assets/evolution",
    }:
        return aggregate(db, domain)
    model_map: dict[str, tuple[Any, list[Any], Any]] = {
        "persons": (Person, [Person.status == PersonStatus.CONFIRMED], Person.full_name),
        "positions": (
            Position,
            [Position.status.in_([PositionStatus.CANONICAL, PositionStatus.INACTIVE])],
            Position.official_name,
        ),
        "appointments": (
            Appointment,
            [Appointment.status == AppointmentStatus.CONFIRMED],
            Appointment.start_date.desc(),
        ),
        "territories": (Territory, [], Territory.name),
        "budget/programs": (
            BudgetProgram,
            [BudgetProgram.status == BudgetStatus.CONFIRMED],
            BudgetProgram.official_name,
        ),
        "procurement/processes": (
            ProcurementProcess,
            [ProcurementProcess.validation_status == "confirmed"],
            ProcurementProcess.publication_date.desc(),
        ),
        "procurement/suppliers": (
            Supplier,
            [Supplier.validation_status == "confirmed"],
            Supplier.legal_name,
        ),
        "sources": (Source, [], Source.retrieved_at.desc()),
    }
    if domain not in model_map:
        return empty(page, page_size, domain)
    model, conditions, ordering = model_map[domain]
    records = list(db.scalars(select(model).where(*conditions).order_by(ordering)))
    safe_fields: dict[str, tuple[str, ...]] = {
        "persons": ("id", "full_name", "nationality", "status"),
        "positions": (
            "id",
            "institution_id",
            "official_name",
            "position_type",
            "hierarchy_level",
            "status",
        ),
        "appointments": (
            "id",
            "person_id",
            "position_id",
            "institution_id",
            "start_date",
            "end_date",
            "appointment_type",
            "status",
            "source_id",
        ),
        "territories": ("id", "name", "code", "type", "parent_id"),
        "budget/programs": (
            "id",
            "institution_id",
            "program_code",
            "official_name",
            "program_type",
            "start_date",
            "end_date",
            "status",
            "source_id",
        ),
        "procurement/processes": (
            "id",
            "institution_id",
            "process_code",
            "title",
            "procurement_type",
            "procedure_type",
            "process_status",
            "publication_date",
            "estimated_amount",
            "currency",
            "source_id",
        ),
        "procurement/suppliers": (
            "id",
            "legal_name",
            "trade_name",
            "supplier_type",
            "country",
            "registration_status",
            "economic_activity",
            "is_public_entity",
            "is_nonprofit",
            "source_id",
        ),
        "sources": ("id", "name", "url", "publisher", "is_official", "retrieved_at"),
    }
    data = [
        {
            field: (
                str(value)
                if isinstance(value, uuid.UUID)
                else value.value
                if hasattr(value, "value")
                else _number(value)
                if isinstance(value, Decimal)
                else value
            )
            for field in safe_fields[domain]
            if (value := getattr(row, field)) is not None
        }
        for row in records
    ]
    return _domain_collection(data, page, page_size, domain, "canonical")


def freshness(db: Session) -> dict[str, Any]:
    rows = list(db.scalars(select(Source).order_by(Source.retrieved_at.desc())))
    data = []
    current = now()
    for row in rows:
        age_days = (current - row.retrieved_at).days
        state = "stale" if age_days > 90 else "available"
        data.append(
            {
                "source_id": str(row.id),
                "name": row.name,
                "publisher": row.publisher,
                "retrieved_at": row.retrieved_at,
                "age_days": age_days,
                "status": state,
            }
        )
    return _summary({"sources": data}, bool(data))


def compare_entities(
    db: Session, entity_ids: list[uuid.UUID], metrics: list[str], entity_type: str
) -> list[dict[str, Any]]:
    allowed = {"institutions", "payroll", "budget", "procurement", "debt", "assets"}
    if entity_type not in allowed:
        return [
            {"entity_id": str(item), "metrics": {metric: None for metric in metrics}}
            for item in entity_ids
        ]
    result = []
    for item in entity_ids:
        institution = get_institution(db, item)
        values: dict[str, Any] = {}
        payroll = aggregate(db, "payroll/summary", item)["data"]
        budget = aggregate(db, "budget/summary", item)["data"]
        procurement = aggregate(db, "procurement/metrics", item)["data"]
        debt = aggregate(db, "debt/summary", item)["data"]
        asset_data = aggregate(db, "assets/summary", item)["data"]
        available = {
            "name": institution["name"] if institution else None,
            "employees": (payroll.get("latest") or {}).get("employee_count"),
            "payroll": (payroll.get("latest") or {}).get("gross_total"),
            "budget": (budget.get("latest") or {}).get("current_budget"),
            "execution": (budget.get("latest") or {}).get("execution_rate"),
            "contracts": procurement.get("contract_count"),
            "procurement": procurement.get("contracted_amount"),
            "debt": debt.get("current_principal"),
            "assets": asset_data.get("book_value"),
        }
        for metric in metrics:
            values[metric] = available.get(metric)
        result.append({"entity_id": str(item), "metrics": values})
    return result


def time_series(
    db: Session, metric: str, institution_id: uuid.UUID | None = None
) -> dict[str, Any]:
    if metric in {"employees", "payroll"}:
        data = aggregate(db, "payroll/evolution", institution_id)["data"]["series"]
        points = [
            {
                "period": row["period"],
                "value": row["employee_count"] if metric == "employees" else row["gross_total"],
                "unit": "people" if metric == "employees" else row["currency"],
                "status": "available",
            }
            for row in data
        ]
    elif metric in {"budget", "execution"}:
        data = aggregate(db, "budget/evolution", institution_id)["data"]["series"]
        points = [
            {
                "period": row["period"],
                "value": row["current_budget"] if metric == "budget" else row["accrued_amount"],
                "unit": row["currency"],
                "status": "available",
            }
            for row in data
        ]
    elif metric == "contracts":
        conditions = [ProcurementContract.validation_status == "confirmed"]
        if institution_id:
            conditions.append(ProcurementContract.institution_id == institution_id)
        rows = db.execute(
            select(
                ProcurementContract.signature_date,
                ProcurementContract.currency,
                func.sum(ProcurementContract.current_amount),
            )
            .where(*conditions)
            .group_by(ProcurementContract.signature_date, ProcurementContract.currency)
            .order_by(ProcurementContract.signature_date)
        )
        points = [
            {
                "period": str(period),
                "value": _number(value),
                "unit": currency,
                "status": "available",
            }
            for period, currency, value in rows
        ]
    elif metric == "debt":
        rows = aggregate(db, "debt/evolution", institution_id)["data"]["balances"]
        points = [
            {
                "period": row["period"],
                "value": row["total_outstanding"],
                "unit": row["currency"],
                "status": "available",
            }
            for row in rows
        ]
    elif metric == "assets":
        rows = aggregate(db, "assets/evolution", institution_id)["data"]["series"]
        points = [
            {
                "period": row["period"],
                "value": row["net_book_value"],
                "unit": row["currency"],
                "status": "available",
            }
            for row in rows
        ]
    else:
        conditions = [RiskFinding.visibility == "public", RiskFinding.status == "published"]
        if institution_id:
            conditions.append(RiskFinding.institution_id == institution_id)
        rows = db.execute(
            select(func.date(RiskFinding.last_detected_at), func.count(RiskFinding.id))
            .where(*conditions)
            .group_by(func.date(RiskFinding.last_detected_at))
            .order_by(func.date(RiskFinding.last_detected_at))
        )
        points = [
            {"period": str(period), "value": count, "unit": "findings", "status": "available"}
            for period, count in rows
        ]
    return _summary({"metric": metric, "series": points}, bool(points))


def public_detail(db: Session, domain: str, item_id: uuid.UUID) -> dict[str, Any] | None:
    collection_domain = {
        "persons/{item_id}": "persons",
        "positions/{item_id}": "positions",
        "territories/{item_id}": "territories",
        "procurement/processes/{item_id}": "procurement/processes",
        "procurement/contracts/{item_id}": "procurement/contracts",
        "procurement/suppliers/{item_id}": "procurement/suppliers",
        "debt/instruments/{item_id}": "debt/instruments",
        "assets/{item_id}": "assets",
        "sources/{item_id}": "sources",
    }.get(domain)
    if collection_domain:
        payload = general_collection(db, collection_domain, 1, 100_000)
        item = next((row for row in payload["data"] if row.get("id") == str(item_id)), None)
        if item:
            return {
                "data": item,
                "generated_at": now(),
                "source_freshness": payload.get("source_freshness", "unknown"),
                "traceability": {},
                "warnings": [],
            }
        return None
    if domain == "persons/{item_id}/public-history":
        rows = list(
            db.scalars(
                select(Appointment)
                .where(
                    Appointment.person_id == item_id,
                    Appointment.status == AppointmentStatus.CONFIRMED,
                )
                .order_by(Appointment.start_date.desc())
            )
        )
        return _domain_collection(
            [
                {
                    "id": str(row.id),
                    "institution_id": str(row.institution_id),
                    "position_id": str(row.position_id),
                    "start_date": row.start_date,
                    "end_date": row.end_date,
                    "appointment_type": row.appointment_type,
                    "source_id": str(row.source_id),
                }
                for row in rows
            ],
            1,
            100,
            "person history",
            "-start_date",
        )
    territory = db.get(Territory, item_id)
    if territory is None:
        return None
    if domain == "territories/{item_id}/institutions":
        return list_institutions_by_territory(db, item_id)
    if domain == "territories/{item_id}/findings":
        conditions = [
            RiskFinding.territory_id == item_id,
            RiskFinding.visibility == "public",
            RiskFinding.status == "published",
        ]
        finding_rows = list(db.scalars(select(RiskFinding).where(*conditions)))
        data = [
            {
                "id": str(row.id),
                "title": row.title,
                "domain": row.domain,
                "severity": row.severity,
                "explanation": row.public_explanation,
                "last_detected_at": row.last_detected_at,
            }
            for row in finding_rows
        ]
        return _domain_collection(data, 1, 100, "territory findings", "-last_detected_at")
    if domain == "territories/{item_id}/metrics":
        institution_count = (
            db.scalar(
                select(func.count())
                .select_from(Institution)
                .where(
                    Institution.territory_id == item_id,
                    Institution.status == InstitutionStatus.CONFIRMED,
                )
            )
            or 0
        )
        return _summary({"institution_count": institution_count}, True)
    return None


def list_institutions_by_territory(db: Session, territory_id: uuid.UUID) -> dict[str, Any]:
    rows = list(
        db.scalars(
            select(Institution)
            .where(
                Institution.territory_id == territory_id,
                Institution.status == InstitutionStatus.CONFIRMED,
            )
            .order_by(Institution.name)
        )
    )
    return _domain_collection(
        [institution_dict(row) for row in rows], 1, 100, "territory institutions", "name"
    )
