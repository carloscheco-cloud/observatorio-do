import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.payroll_entries.models import PayrollEntry
from app.modules.payroll_findings.models import FindingSeverity, PayrollFinding
from app.modules.payroll_periods.models import PayrollPeriod


class InvalidComparison(ValueError):
    pass


def list_findings(db: Session, *, period_id: uuid.UUID | None = None) -> list[PayrollFinding]:
    query = select(PayrollFinding)
    if period_id:
        query = query.where(PayrollFinding.payroll_period_id == period_id)
    return list(db.scalars(query.order_by(PayrollFinding.created_at.desc())))


def compare_periods(
    db: Session, period_id: uuid.UUID, comparison_period_id: uuid.UUID
) -> list[PayrollFinding]:
    current = db.get(PayrollPeriod, period_id)
    previous = db.get(PayrollPeriod, comparison_period_id)
    if current is None or previous is None:
        raise InvalidComparison("Both payroll periods must exist")
    current_rows = list(
        db.scalars(select(PayrollEntry).where(PayrollEntry.payroll_period_id == period_id))
    )
    previous_rows = list(
        db.scalars(
            select(PayrollEntry).where(PayrollEntry.payroll_period_id == comparison_period_id)
        )
    )
    current_by_person = {row.person_id: row for row in current_rows}
    previous_by_person = {row.person_id: row for row in previous_rows}
    findings: list[PayrollFinding] = []

    def add(
        kind: str,
        person_id: uuid.UUID | None,
        explanation: str,
        observed: object,
        old: object,
        severity: FindingSeverity = FindingSeverity.INFORMATIONAL,
    ) -> None:
        findings.append(
            PayrollFinding(
                finding_type=kind,
                severity=severity,
                person_id=person_id,
                institution_id=current.institution_id,
                payroll_period_id=period_id,
                comparison_period_id=comparison_period_id,
                observed_value={"value": str(observed)},
                expected_or_previous_value={"value": str(old)},
                explanation=explanation,
                evidence_id=current.evidence_id,
            )
        )

    for person_id in current_by_person.keys() - previous_by_person.keys():
        add(
            "hire",
            person_id,
            "Person appears in current period but not comparison period",
            True,
            False,
        )
    for person_id in previous_by_person.keys() - current_by_person.keys():
        add("departure", person_id, "Person no longer appears in current period", False, True)
    for person_id in current_by_person.keys() & previous_by_person.keys():
        new, old = current_by_person[person_id], previous_by_person[person_id]
        if new.gross_income != old.gross_income:
            add(
                "salary_change",
                person_id,
                "Gross income changed between periods",
                new.gross_income,
                old.gross_income,
                FindingSeverity.REVIEW_REQUIRED,
            )
        if new.position_id != old.position_id:
            add(
                "position_change",
                person_id,
                "Position changed between periods",
                new.position_id,
                old.position_id,
            )
        if new.organizational_unit_id != old.organizational_unit_id:
            add(
                "unit_change",
                person_id,
                "Organizational unit changed between periods",
                new.organizational_unit_id,
                old.organizational_unit_id,
            )
    gross_current = sum((row.gross_income for row in current_rows), Decimal())
    gross_previous = sum((row.gross_income for row in previous_rows), Decimal())
    if gross_current != gross_previous:
        add(
            "payroll_mass_change",
            None,
            "Aggregate gross payroll changed",
            gross_current,
            gross_previous,
        )
    counts: dict[tuple[uuid.UUID, str | None], int] = {}
    for row in current_rows:
        key = (row.person_id, row.employee_reference_hash)
        counts[key] = counts.get(key, 0) + 1
    for (person_id, _), count in counts.items():
        if count > 1:
            add(
                "duplicate",
                person_id,
                "Person has multiple entries in the same period",
                count,
                1,
                FindingSeverity.UNUSUAL,
            )
    db.add_all(findings)
    db.commit()
    return findings
