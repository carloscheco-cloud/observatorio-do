import uuid
from collections.abc import Iterable
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.appointments.models import Appointment
from app.modules.budget.models import (
    BudgetAppropriation,
    BudgetExecutionRecord,
    BudgetModification,
)
from app.modules.employment_relationships.models import EmploymentRelationship
from app.modules.evidence.models import Evidence
from app.modules.institutions.models import Institution, InstitutionEvidence
from app.modules.organizational_units.models import OrganizationalUnit
from app.modules.payroll_entries.models import PayrollEntry
from app.modules.payroll_periods.models import PayrollPeriod
from app.modules.positions.models import Position
from app.modules.procurement_processes.models import (
    ContractPayment,
    ProcurementAward,
    ProcurementBid,
    ProcurementContract,
    ProcurementProcess,
)
from app.modules.public_assets.models import (
    AssetAssignment,
    AssetInsurancePolicy,
    AssetMaintenanceRecord,
    AssetValuation,
    PhysicalInventory,
    PublicAsset,
)
from app.modules.public_debt.models import DebtBalanceSnapshot, DebtInstrument, DebtPayment
from app.modules.risk_engine.engine import (
    EvaluationContext,
    FindingCandidate,
    RuleResult,
    structured_explanation,
)
from app.modules.risk_engine.models import RiskRule
from app.modules.sources.models import Source


class BaseRiskAdapter:
    domain = "other"

    def __init__(self, db: Session, rules: Iterable[RiskRule]) -> None:
        self.db = db
        self.rules = {rule.stable_code.removeprefix("b10."): rule for rule in rules}

    def rule(self, code: str) -> RiskRule | None:
        return self.rules.get(code)

    def percent_threshold(self, code: str, default: Decimal) -> Decimal:
        rule = self.rule(code)
        raw = rule.threshold_config.get("value") if rule else None
        try:
            return Decimal(str(raw)) / Decimal("100") if raw is not None else default
        except (ArithmeticError, ValueError):
            return default

    @staticmethod
    def in_period(
        context: EvaluationContext,
        start: date | datetime | None,
        end: date | datetime | None = None,
    ) -> bool:
        start_date = start.date() if isinstance(start, datetime) else start
        end_date = end.date() if isinstance(end, datetime) else end
        if context.period_start and end_date and end_date < context.period_start:
            return False
        return not (context.period_end and start_date and start_date > context.period_end)

    def candidate(
        self,
        code: str,
        *,
        entity_type: str,
        entity_id: uuid.UUID,
        institution_id: uuid.UUID | None,
        evidence_id: uuid.UUID | None,
        source_id: uuid.UUID | None,
        observed: dict[str, object],
        comparison: dict[str, object] | None,
        threshold: dict[str, object],
        period_start: object | None = None,
        period_end: object | None = None,
    ) -> FindingCandidate | None:
        rule = self.rule(code)
        if rule is None or not rule.enabled:
            return None
        evidence_id = evidence_id or rule.evidence_id
        source_id = source_id or rule.source_id
        if evidence_id is None or source_id is None:
            return None
        explanation = structured_explanation(
            observation=str(observed),
            rule=f"{rule.stable_code} v{rule.version}",
            threshold=str(threshold),
            comparison=str(comparison or "sin comparación disponible"),
            difference=str(observed.get("difference", "observable")),
            period=f"{period_start or 'no especificado'} a {period_end or 'no especificado'}",
            evidence=str(evidence_id),
        )
        return FindingCandidate(
            rule_id=rule.id,
            risk_type_id=rule.risk_type_id,
            domain=rule.domain,
            entity_type=entity_type,
            entity_id=entity_id,
            institution_id=institution_id,
            title=rule.name,
            observed_value=observed,
            comparison_value=comparison,
            threshold_value=threshold,
            public_explanation=explanation,
            internal_explanation=(
                f"Consulta estructurada reproducible; regla={rule.stable_code}; "
                f"versión={rule.version}; observado={observed}; comparación={comparison}; "
                f"umbral={threshold}."
            ),
            severity=rule.severity,
            confidence_level="deterministic",
            evidence_ids=(evidence_id,),
            evidence_links=((evidence_id, source_id, "primary"),),
            metadata={
                "adapter": type(self).__name__,
                "period_start": str(period_start) if period_start else None,
                "period_end": str(period_end) if period_end else None,
            },
        )

    @staticmethod
    def result(candidates: list[FindingCandidate], records: int) -> RuleResult:
        return RuleResult(candidates=tuple(candidates), records_evaluated=records)


class PayrollRiskAdapter(BaseRiskAdapter):
    domain = "payroll"

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        query = select(PayrollPeriod).order_by(
            PayrollPeriod.institution_id, PayrollPeriod.period_start
        )
        if context.institution_id:
            query = query.where(PayrollPeriod.institution_id == context.institution_id)
        periods = [
            row
            for row in self.db.scalars(query)
            if self.in_period(context, row.period_start, row.period_end)
        ]
        entry_query = select(PayrollEntry)
        if context.institution_id:
            entry_query = entry_query.where(PayrollEntry.institution_id == context.institution_id)
        entries = list(self.db.scalars(entry_query))
        by_period: dict[uuid.UUID, list[PayrollEntry]] = {}
        for entry in entries:
            by_period.setdefault(entry.payroll_period_id, []).append(entry)
        candidates: list[FindingCandidate] = []
        previous: dict[uuid.UUID, PayrollPeriod] = {}
        for period in periods:
            prior = previous.get(period.institution_id)
            current_entries = by_period.get(period.id, [])
            if prior:
                old_entries = by_period.get(prior.id, [])
                self._growth_candidates(period, prior, current_entries, old_entries, candidates)
                old_salary = {row.person_id: row for row in old_entries}
                for entry in current_entries:
                    old = old_salary.get(entry.person_id)
                    threshold = self.percent_threshold("significant_salary_change", Decimal("0.2"))
                    if (
                        old
                        and old.base_salary
                        and abs(entry.base_salary - old.base_salary) / old.base_salary >= threshold
                    ):
                        item = self.candidate(
                            "significant_salary_change",
                            entity_type="payroll_entry",
                            entity_id=entry.id,
                            institution_id=entry.institution_id,
                            evidence_id=entry.evidence_id,
                            source_id=entry.source_id,
                            observed={
                                "salary": str(entry.base_salary),
                                "difference": str(entry.base_salary - old.base_salary),
                            },
                            comparison={"previous_salary": str(old.base_salary)},
                            threshold={"percentage": str(threshold * 100)},
                            period_start=period.period_start,
                            period_end=period.period_end,
                        )
                        if item:
                            candidates.append(item)
            previous[period.institution_id] = period
        duplicates: dict[tuple[uuid.UUID, uuid.UUID, Decimal], list[PayrollEntry]] = {}
        for entry in entries:
            duplicates.setdefault(
                (entry.payroll_period_id, entry.person_id, entry.gross_income), []
            ).append(entry)
        for rows in duplicates.values():
            if len(rows) > 1:
                row = rows[0]
                item = self.candidate(
                    "exact_period_duplicate",
                    entity_type="payroll_entry",
                    entity_id=row.id,
                    institution_id=row.institution_id,
                    evidence_id=row.evidence_id,
                    source_id=row.source_id,
                    observed={"duplicate_count": len(rows), "difference": len(rows) - 1},
                    comparison={"expected_count": 1},
                    threshold={"maximum": 1},
                )
                if item:
                    candidates.append(item)
        return self.result(candidates, len(entries))

    def _growth_candidates(
        self,
        period: PayrollPeriod,
        prior: PayrollPeriod,
        current: list[PayrollEntry],
        old: list[PayrollEntry],
        output: list[FindingCandidate],
    ) -> None:
        metrics = (
            ("monthly_employee_growth", Decimal(len(current)), Decimal(len(old))),
            (
                "payroll_mass_growth",
                sum((row.gross_income for row in current), Decimal()),
                sum((row.gross_income for row in old), Decimal()),
            ),
        )
        for code, current_value, previous_value in metrics:
            threshold = self.percent_threshold(code, Decimal("0.2"))
            if previous_value and (current_value - previous_value) / previous_value >= threshold:
                item = self.candidate(
                    code,
                    entity_type="payroll_period",
                    entity_id=period.id,
                    institution_id=period.institution_id,
                    evidence_id=period.evidence_id,
                    source_id=period.source_id,
                    observed={
                        "value": str(current_value),
                        "difference": str(current_value - previous_value),
                    },
                    comparison={"previous": str(previous_value)},
                    threshold={"percentage": str(threshold * 100)},
                    period_start=period.period_start,
                    period_end=period.period_end,
                )
                if item:
                    output.append(item)


class EmploymentRiskAdapter(BaseRiskAdapter):
    domain = "public_employment"

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        relationships = [
            row
            for row in self.db.scalars(select(EmploymentRelationship))
            if self.in_period(context, row.start_date, row.end_date)
        ]
        entries = list(self.db.scalars(select(PayrollEntry)))
        candidates: list[FindingCandidate] = []
        active_by_person: dict[uuid.UUID, list[EmploymentRelationship]] = {}
        for row in relationships:
            if row.relationship_status == "active" and (
                not context.institution_id or row.institution_id == context.institution_id
            ):
                active_by_person.setdefault(row.person_id, []).append(row)
            if row.position_id is None or row.organizational_unit_id is None:
                item = self.candidate(
                    "relationship_without_position_or_unit",
                    entity_type="employment_relationship",
                    entity_id=row.id,
                    institution_id=row.institution_id,
                    evidence_id=row.evidence_id,
                    source_id=row.source_id,
                    observed={
                        "position_present": row.position_id is not None,
                        "unit_present": row.organizational_unit_id is not None,
                        "difference": 1,
                    },
                    comparison={"both_required": True},
                    threshold={"missing_fields": 0},
                    period_start=row.start_date,
                    period_end=row.end_date,
                )
                if item:
                    candidates.append(item)
        for rows in active_by_person.values():
            institutions = {row.institution_id for row in rows}
            if len(institutions) > 1:
                row = rows[0]
                item = self.candidate(
                    "simultaneous_multi_institution_relationship",
                    entity_type="person",
                    entity_id=row.person_id,
                    institution_id=row.institution_id,
                    evidence_id=row.evidence_id,
                    source_id=row.source_id,
                    observed={
                        "institution_count": len(institutions),
                        "difference": len(institutions) - 1,
                    },
                    comparison={"expected_maximum": 1},
                    threshold={"maximum": 1},
                    period_start=context.period_start,
                    period_end=context.period_end,
                )
                if item:
                    candidates.append(item)
        active_ids = {row.id for row in relationships if row.relationship_status == "active"}
        for entry in entries:
            if (
                context.institution_id and entry.institution_id != context.institution_id
            ) or entry.employment_relationship_id in active_ids:
                continue
            item = self.candidate(
                "entry_without_employment",
                entity_type="payroll_entry",
                entity_id=entry.id,
                institution_id=entry.institution_id,
                evidence_id=entry.evidence_id,
                source_id=entry.source_id,
                observed={"active_relationship": False, "difference": 1},
                comparison={"required": True},
                threshold={"required": True},
            )
            if item:
                candidates.append(item)
        return self.result(candidates, len(relationships) + len(entries))


class BudgetRiskAdapter(BaseRiskAdapter):
    domain = "budget"

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        query = select(BudgetExecutionRecord, BudgetAppropriation).join(
            BudgetAppropriation, BudgetAppropriation.id == BudgetExecutionRecord.appropriation_id
        )
        if context.institution_id:
            query = query.where(BudgetExecutionRecord.institution_id == context.institution_id)
        rows = list(self.db.execute(query))
        modifications = list(self.db.scalars(select(BudgetModification)))
        candidates: list[FindingCandidate] = []
        for execution, appropriation in rows:
            ratio = (
                execution.accrued_amount / execution.current_budget
                if execution.current_budget
                else Decimal()
            )
            checks: list[tuple[str, dict[str, object], dict[str, object]]] = []
            if ratio < Decimal("0.5"):
                checks.append(
                    (
                        "under_execution",
                        {"ratio": str(ratio), "difference": str(Decimal("0.5") - ratio)},
                        {"minimum_ratio": "0.5"},
                    )
                )
            if ratio > Decimal("1"):
                checks.append(
                    (
                        "over_execution",
                        {"ratio": str(ratio), "difference": str(ratio - 1)},
                        {"maximum_ratio": "1"},
                    )
                )
            if execution.available_balance < 0:
                checks.append(
                    (
                        "negative_balance",
                        {
                            "balance": str(execution.available_balance),
                            "difference": str(-execution.available_balance),
                        },
                        {"minimum": "0"},
                    )
                )
            if execution.current_budget != (
                appropriation.current_amount or appropriation.approved_amount
            ):
                checks.append(
                    (
                        "approved_current_executed_inconsistency",
                        {
                            "execution_current": str(execution.current_budget),
                            "difference": str(
                                execution.current_budget
                                - (appropriation.current_amount or appropriation.approved_amount)
                            ),
                        },
                        {"equality_required": True},
                    )
                )
            for code, observed, threshold in checks:
                item = self.candidate(
                    code,
                    entity_type="budget_execution_record",
                    entity_id=execution.id,
                    institution_id=execution.institution_id,
                    evidence_id=execution.evidence_id,
                    source_id=execution.source_id,
                    observed=observed,
                    comparison={
                        "appropriation_current": str(
                            appropriation.current_amount or appropriation.approved_amount
                        )
                    },
                    threshold=threshold,
                    period_start=execution.period_start,
                    period_end=execution.period_end,
                )
                if item:
                    candidates.append(item)
        for modification in modifications:
            if modification.previous_balance and abs(modification.amount) / abs(
                modification.previous_balance
            ) >= Decimal("0.2"):
                item = self.candidate(
                    "significant_budget_modification",
                    entity_type="budget_modification",
                    entity_id=modification.id,
                    institution_id=modification.institution_id,
                    evidence_id=modification.evidence_id,
                    source_id=modification.source_id,
                    observed={
                        "amount": str(modification.amount),
                        "difference": str(
                            modification.resulting_balance - modification.previous_balance
                        ),
                    },
                    comparison={"previous_balance": str(modification.previous_balance)},
                    threshold={"percentage": 20},
                    period_start=modification.effective_date,
                    period_end=modification.effective_date,
                )
                if item:
                    candidates.append(item)
        return self.result(candidates, len(rows) + len(modifications))


class ProcurementRiskAdapter(BaseRiskAdapter):
    domain = "procurement"

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        processes = [
            row
            for row in self.db.scalars(select(ProcurementProcess))
            if self.in_period(context, row.publication_date, row.award_date)
        ]
        bids = list(self.db.scalars(select(ProcurementBid)))
        awards = list(self.db.scalars(select(ProcurementAward)))
        contracts = list(self.db.scalars(select(ProcurementContract)))
        payments = list(self.db.scalars(select(ContractPayment)))
        bid_counts: dict[uuid.UUID, int] = {}
        for bid in bids:
            bid_counts[bid.procurement_process_id] = (
                bid_counts.get(bid.procurement_process_id, 0) + 1
            )
        candidates: list[FindingCandidate] = []
        for process in processes:
            if context.institution_id and process.institution_id != context.institution_id:
                continue
            count = bid_counts.get(process.id, 0)
            code = "single_bidder" if count == 1 else "low_competition" if count == 2 else None
            if code:
                item = self.candidate(
                    code,
                    entity_type="procurement_process",
                    entity_id=process.id,
                    institution_id=process.institution_id,
                    evidence_id=process.evidence_id,
                    source_id=process.source_id,
                    observed={"bid_count": count, "difference": 3 - count},
                    comparison={"recommended_minimum": 3},
                    threshold={"minimum": 3},
                    period_start=process.publication_date,
                    period_end=process.submission_deadline,
                )
                if item:
                    candidates.append(item)
            if str(process.procedure_type) == "emergency":
                item = self.candidate(
                    "repeated_emergency_procedure",
                    entity_type="procurement_process",
                    entity_id=process.id,
                    institution_id=process.institution_id,
                    evidence_id=process.evidence_id,
                    source_id=process.source_id,
                    observed={"procedure": "emergency", "difference": 1},
                    comparison={"ordinary_procedure": True},
                    threshold={"review_each": True},
                )
                if item:
                    candidates.append(item)
        total_awarded = sum((row.awarded_amount for row in awards), Decimal())
        by_supplier: dict[uuid.UUID, list[ProcurementAward]] = {}
        for award in awards:
            by_supplier.setdefault(award.supplier_id, []).append(award)
        for supplier_id, rows in by_supplier.items():
            amount = sum((row.awarded_amount for row in rows), Decimal())
            if total_awarded and amount / total_awarded >= Decimal("0.5"):
                row = rows[0]
                award_process = next(
                    (item for item in processes if item.id == row.procurement_process_id), None
                )
                if award_process:
                    item = self.candidate(
                        "award_concentration",
                        entity_type="supplier",
                        entity_id=supplier_id,
                        institution_id=award_process.institution_id,
                        evidence_id=row.evidence_id,
                        source_id=row.source_id,
                        observed={
                            "share": str(amount / total_awarded),
                            "difference": str(amount / total_awarded - Decimal("0.5")),
                        },
                        comparison={"total_awarded": str(total_awarded)},
                        threshold={"maximum_share": "0.5"},
                    )
                    if item:
                        candidates.append(item)
        for contract in contracts:
            if context.institution_id and contract.institution_id != context.institution_id:
                continue
            if (
                contract.original_amount
                and contract.current_amount / contract.original_amount >= Decimal("1.2")
            ):
                item = self.candidate(
                    "accumulated_contract_growth",
                    entity_type="procurement_contract",
                    entity_id=contract.id,
                    institution_id=contract.institution_id,
                    evidence_id=contract.evidence_id,
                    source_id=contract.source_id,
                    observed={
                        "current": str(contract.current_amount),
                        "difference": str(contract.current_amount - contract.original_amount),
                    },
                    comparison={"original": str(contract.original_amount)},
                    threshold={"percentage": 20},
                    period_start=contract.start_date,
                    period_end=contract.end_date,
                )
                if item:
                    candidates.append(item)
        for payment in payments:
            payment_contract = next(
                (row for row in contracts if row.id == payment.contract_id), None
            )
            if payment_contract and payment.gross_amount > payment_contract.current_amount:
                item = self.candidate(
                    "payment_above_contract",
                    entity_type="contract_payment",
                    entity_id=payment.id,
                    institution_id=payment.institution_id,
                    evidence_id=payment.evidence_id,
                    source_id=payment.source_id,
                    observed={
                        "payment": str(payment.gross_amount),
                        "difference": str(payment.gross_amount - payment_contract.current_amount),
                    },
                    comparison={"contract": str(payment_contract.current_amount)},
                    threshold={"maximum": str(payment_contract.current_amount)},
                    period_start=payment.payment_date,
                    period_end=payment.payment_date,
                )
                if item:
                    candidates.append(item)
        return self.result(candidates, len(processes) + len(contracts) + len(payments))


class DebtRiskAdapter(BaseRiskAdapter):
    domain = "public_debt"

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        instruments = [
            row
            for row in self.db.scalars(select(DebtInstrument))
            if self.in_period(context, row.effective_date, row.maturity_date)
        ]
        snapshots = list(
            self.db.scalars(select(DebtBalanceSnapshot).order_by(DebtBalanceSnapshot.snapshot_date))
        )
        candidates: list[FindingCandidate] = []
        by_instrument: dict[uuid.UUID, list[DebtBalanceSnapshot]] = {}
        for snapshot in snapshots:
            by_instrument.setdefault(snapshot.debt_instrument_id, []).append(snapshot)
        total = sum((row.current_principal for row in instruments), Decimal())
        by_creditor: dict[uuid.UUID | None, Decimal] = {}
        for instrument in instruments:
            if (
                context.institution_id
                and instrument.debtor_institution_id != context.institution_id
            ):
                continue
            by_creditor[instrument.creditor_id] = (
                by_creditor.get(instrument.creditor_id, Decimal()) + instrument.current_principal
            )
            checks: list[tuple[str, dict[str, object], dict[str, object]]] = []
            if (
                instrument.maturity_date
                and context.as_of <= instrument.maturity_date <= context.as_of + timedelta(days=90)
            ):
                checks.append(
                    (
                        "upcoming_maturity",
                        {
                            "days": (instrument.maturity_date - context.as_of).days,
                            "difference": 90 - (instrument.maturity_date - context.as_of).days,
                        },
                        {"days": 90},
                    )
                )
            if (
                instrument.maturity_date
                and instrument.maturity_date < context.as_of
                and instrument.current_principal > 0
            ):
                checks.append(
                    (
                        "overdue_debt",
                        {
                            "principal": str(instrument.current_principal),
                            "difference": str(instrument.current_principal),
                        },
                        {"maximum_after_maturity": "0"},
                    )
                )
            if instrument.currency != "DOP":
                checks.append(
                    (
                        "currency_exposure",
                        {"currency": instrument.currency, "difference": 1},
                        {"local_currency": "DOP"},
                    )
                )
            history = by_instrument.get(instrument.id, [])
            if (
                len(history) >= 2
                and history[-2].total_outstanding
                and history[-1].total_outstanding / history[-2].total_outstanding >= Decimal("1.2")
            ):
                checks.append(
                    (
                        "rapid_debt_growth",
                        {
                            "balance": str(history[-1].total_outstanding),
                            "difference": str(
                                history[-1].total_outstanding - history[-2].total_outstanding
                            ),
                        },
                        {"percentage": 20},
                    )
                )
            for snapshot in history:
                components = (
                    snapshot.principal_outstanding
                    + snapshot.interest_accrued
                    + snapshot.arrears_principal
                    + snapshot.arrears_interest
                    + snapshot.fees_outstanding
                )
                if components != snapshot.total_outstanding:
                    checks.append(
                        (
                            "inconsistent_debt_balance",
                            {
                                "total": str(snapshot.total_outstanding),
                                "difference": str(snapshot.total_outstanding - components),
                            },
                            {"expected_components": str(components)},
                        )
                    )
            for code, observed, threshold in checks:
                item = self.candidate(
                    code,
                    entity_type="debt_instrument",
                    entity_id=instrument.id,
                    institution_id=instrument.debtor_institution_id,
                    evidence_id=instrument.evidence_id,
                    source_id=instrument.source_id,
                    observed=observed,
                    comparison={"current_principal": str(instrument.current_principal)},
                    threshold=threshold,
                    period_start=instrument.effective_date,
                    period_end=instrument.maturity_date,
                )
                if item:
                    candidates.append(item)
        for creditor_id, amount in by_creditor.items():
            if creditor_id and total and amount / total >= Decimal("0.5"):
                instrument = next(row for row in instruments if row.creditor_id == creditor_id)
                item = self.candidate(
                    "creditor_concentration",
                    entity_type="creditor",
                    entity_id=creditor_id,
                    institution_id=instrument.debtor_institution_id,
                    evidence_id=instrument.evidence_id,
                    source_id=instrument.source_id,
                    observed={
                        "share": str(amount / total),
                        "difference": str(amount / total - Decimal("0.5")),
                    },
                    comparison={"total_debt": str(total)},
                    threshold={"maximum_share": "0.5"},
                )
                if item:
                    candidates.append(item)
        return self.result(candidates, len(instruments) + len(snapshots))


class AssetRiskAdapter(BaseRiskAdapter):
    domain = "public_assets"

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        assets = [
            row
            for row in self.db.scalars(select(PublicAsset))
            if self.in_period(context, row.acquisition_date)
        ]
        assignments = list(self.db.scalars(select(AssetAssignment)))
        inventories = list(self.db.scalars(select(PhysicalInventory)))
        insurance = {row.asset_id for row in self.db.scalars(select(AssetInsurancePolicy))}
        maintenance = list(self.db.scalars(select(AssetMaintenanceRecord)))
        valuations = list(self.db.scalars(select(AssetValuation)))
        assigned = {row.asset_id for row in assignments if row.status == "active"}
        candidates: list[FindingCandidate] = []
        for asset in assets:
            if context.institution_id and asset.owner_institution_id != context.institution_id:
                continue
            checks: list[tuple[str, dict[str, object], dict[str, object]]] = []
            if asset.id not in assigned and asset.custodian_person_id is None:
                checks.append(
                    (
                        "asset_without_custodian",
                        {"custodian": False, "difference": 1},
                        {"required": True},
                    )
                )
            recent = [
                row
                for row in inventories
                if row.institution_id == asset.owner_institution_id
                and row.inventory_date >= context.as_of - timedelta(days=365)
            ]
            if not recent:
                checks.append(
                    (
                        "stale_inventory",
                        {"recent_inventory": False, "difference": 365},
                        {"maximum_age_days": 365},
                    )
                )
            if (asset.current_book_value or Decimal()) >= Decimal(
                "100"
            ) and asset.id not in insurance:
                checks.append(
                    (
                        "high_value_asset_uninsured",
                        {
                            "insured": False,
                            "value": str(asset.current_book_value),
                            "difference": str(asset.current_book_value),
                        },
                        {"minimum_value": "100"},
                    )
                )
            if asset.location_id is None:
                checks.append(
                    (
                        "inconsistent_location",
                        {"location": None, "difference": 1},
                        {"required": True},
                    )
                )
            for maintenance_row in maintenance:
                if (
                    maintenance_row.asset_id == asset.id
                    and maintenance_row.scheduled_date
                    and maintenance_row.scheduled_date < context.as_of
                    and maintenance_row.performed_date is None
                ):
                    checks.append(
                        (
                            "overdue_maintenance",
                            {
                                "scheduled": str(maintenance_row.scheduled_date),
                                "difference": (context.as_of - maintenance_row.scheduled_date).days,
                            },
                            {"maximum_delay_days": 0},
                        )
                    )
            for valuation_row in valuations:
                if (
                    valuation_row.asset_id == asset.id
                    and valuation_row.net_book_value
                    != valuation_row.gross_value
                    - valuation_row.accumulated_depreciation
                    - valuation_row.impairment_amount
                ):
                    checks.append(
                        (
                            "inconsistent_valuation",
                            {
                                "net": str(valuation_row.net_book_value),
                                "difference": str(
                                    valuation_row.net_book_value
                                    - (
                                        valuation_row.gross_value
                                        - valuation_row.accumulated_depreciation
                                        - valuation_row.impairment_amount
                                    )
                                ),
                            },
                            {"formula": "gross-depreciation-impairment"},
                        )
                    )
            for code, observed, threshold in checks:
                item = self.candidate(
                    code,
                    entity_type="public_asset",
                    entity_id=asset.id,
                    institution_id=asset.owner_institution_id,
                    evidence_id=asset.evidence_id,
                    source_id=asset.source_id,
                    observed=observed,
                    comparison={"asset_value": str(asset.current_book_value)},
                    threshold=threshold,
                    period_start=asset.acquisition_date,
                    period_end=context.as_of,
                )
                if item:
                    candidates.append(item)
        return self.result(candidates, len(assets))


class InstitutionRiskAdapter(BaseRiskAdapter):
    domain = "institutional_growth"

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        rows = list(self.db.scalars(select(Institution)))
        linked = {
            row.institution_id
            for row in self.db.scalars(select(InstitutionEvidence))
            if row.relation == "supports_legal_basis"
        }
        candidates: list[FindingCandidate] = []
        for row in rows:
            if context.institution_id and row.id != context.institution_id:
                continue
            if row.id not in linked:
                item = self.candidate(
                    "active_institution_without_legal_basis",
                    entity_type="institution",
                    entity_id=row.id,
                    institution_id=row.id,
                    evidence_id=None,
                    source_id=None,
                    observed={"evidence_link": False, "difference": 1},
                    comparison={"required": True},
                    threshold={"minimum_evidence": 1},
                )
                if item:
                    candidates.append(item)
        return self.result(candidates, len(rows))


class OrganizationalRiskAdapter(BaseRiskAdapter):
    domain = "organizational_structure"

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        units = list(self.db.scalars(select(OrganizationalUnit)))
        positions = list(self.db.scalars(select(Position)))
        appointments = list(self.db.scalars(select(Appointment)))
        active_positions = {
            row.position_id for row in appointments if row.status == "confirmed" and row.position_id
        }
        candidates: list[FindingCandidate] = []
        for unit in units:
            if context.institution_id and unit.institution_id != context.institution_id:
                continue
            unit_positions = [row for row in positions if row.organizational_unit_id == unit.id]
            if not any(row.id in active_positions for row in unit_positions):
                item = self.candidate(
                    "unit_without_responsible",
                    entity_type="organizational_unit",
                    entity_id=unit.id,
                    institution_id=unit.institution_id,
                    evidence_id=None,
                    source_id=None,
                    observed={"responsible": False, "difference": 1},
                    comparison={"active_occupant_required": True},
                    threshold={"minimum": 1},
                    period_start=unit.valid_from,
                    period_end=unit.valid_to,
                )
                if item:
                    candidates.append(item)
        recent_by_institution: dict[uuid.UUID, list[OrganizationalUnit]] = {}
        for unit in units:
            if unit.valid_from >= context.as_of - timedelta(days=365):
                recent_by_institution.setdefault(unit.institution_id, []).append(unit)
        for institution_id, recent in recent_by_institution.items():
            total = sum(unit.institution_id == institution_id for unit in units)
            if total and len(recent) / total >= 0.3:
                unit = recent[0]
                item = self.candidate(
                    "rapid_structural_growth",
                    entity_type="institution",
                    entity_id=institution_id,
                    institution_id=institution_id,
                    evidence_id=None,
                    source_id=None,
                    observed={"new_units": len(recent), "difference": len(recent)},
                    comparison={"total_units": total},
                    threshold={"annual_share": 0.3},
                    period_start=context.as_of - timedelta(days=365),
                    period_end=context.as_of,
                )
                if item:
                    candidates.append(item)
        return self.result(candidates, len(units))


class AppointmentRiskAdapter(BaseRiskAdapter):
    domain = "appointments"

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        appointments = list(self.db.scalars(select(Appointment)))
        positions = list(self.db.scalars(select(Position)))
        occupied = {
            row.position_id for row in appointments if row.status == "confirmed" and row.position_id
        }
        candidates: list[FindingCandidate] = []
        for row in appointments:
            if context.institution_id and row.institution_id != context.institution_id:
                continue
            if row.status == "confirmed" and (row.evidence_id is None or row.source_id is None):
                item = self.candidate(
                    "appointment_without_evidence",
                    entity_type="appointment",
                    entity_id=row.id,
                    institution_id=row.institution_id,
                    evidence_id=row.evidence_id,
                    source_id=row.source_id,
                    observed={"evidence": False, "difference": 1},
                    comparison={"required": True},
                    threshold={"minimum": 1},
                    period_start=row.start_date,
                    period_end=row.end_date,
                )
                if item:
                    candidates.append(item)
        for position in positions:
            if context.institution_id and position.institution_id != context.institution_id:
                continue
            if position.status == "canonical" and position.id not in occupied:
                item = self.candidate(
                    "active_position_unoccupied",
                    entity_type="position",
                    entity_id=position.id,
                    institution_id=position.institution_id,
                    evidence_id=None,
                    source_id=None,
                    observed={"occupant": False, "difference": 1},
                    comparison={"active_appointment": True},
                    threshold={"minimum": 1},
                    period_start=position.valid_from,
                    period_end=position.valid_to,
                )
                if item:
                    candidates.append(item)
        return self.result(candidates, len(appointments) + len(positions))


class TraceabilityRiskAdapter(BaseRiskAdapter):
    domain = "data_quality"

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        sources = list(self.db.scalars(select(Source)))
        evidence = list(self.db.scalars(select(Evidence)))
        candidates: list[FindingCandidate] = []
        for source in sources:
            age = (context.as_of - source.retrieved_at.date()).days
            if age > 365:
                item = self.candidate(
                    "stale_source",
                    entity_type="source",
                    entity_id=source.id,
                    institution_id=context.institution_id,
                    evidence_id=None,
                    source_id=source.id,
                    observed={"age_days": age, "difference": age - 365},
                    comparison={"retrieved_at": source.retrieved_at.isoformat()},
                    threshold={"maximum_age_days": 365},
                )
                if item:
                    candidates.append(item)
            if not source.url.startswith(("http://", "https://")):
                item = self.candidate(
                    "inaccessible_evidence",
                    entity_type="source",
                    entity_id=source.id,
                    institution_id=context.institution_id,
                    evidence_id=None,
                    source_id=source.id,
                    observed={"accessible_url": False, "difference": 1},
                    comparison={"required_scheme": "http(s)"},
                    threshold={"accessible": True},
                )
                if item:
                    candidates.append(item)
        for item_row in evidence:
            if not item_row.excerpt.strip() or not item_row.locator.strip():
                item = self.candidate(
                    "essential_fields_missing",
                    entity_type="evidence",
                    entity_id=item_row.id,
                    institution_id=context.institution_id,
                    evidence_id=item_row.id,
                    source_id=item_row.source_id,
                    observed={"excerpt_or_locator_missing": True, "difference": 1},
                    comparison={"required": True},
                    threshold={"missing_fields": 0},
                )
                if item:
                    candidates.append(item)
        return self.result(candidates, len(sources) + len(evidence))


class CrossDomainRiskAdapter(BaseRiskAdapter):
    domain = "cross_domain"

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        entries = list(self.db.scalars(select(PayrollEntry)))
        relationships = {row.id: row for row in self.db.scalars(select(EmploymentRelationship))}
        contracts = list(self.db.scalars(select(ProcurementContract)))
        payments = list(self.db.scalars(select(ContractPayment)))
        assets = list(self.db.scalars(select(PublicAsset)))
        debt_payments = list(self.db.scalars(select(DebtPayment)))
        candidates: list[FindingCandidate] = []
        for entry in entries:
            relationship = (
                relationships.get(entry.employment_relationship_id)
                if entry.employment_relationship_id
                else None
            )
            if relationship is None or relationship.relationship_status != "active":
                item = self.candidate(
                    "payroll_without_active_employment",
                    entity_type="payroll_entry",
                    entity_id=entry.id,
                    institution_id=entry.institution_id,
                    evidence_id=entry.evidence_id,
                    source_id=entry.source_id,
                    observed={"active_employment": False, "difference": 1},
                    comparison={"required": True},
                    threshold={"active": True},
                )
                if item:
                    candidates.append(item)
        for contract in contracts:
            if contract.budget_appropriation_id is None:
                item = self.candidate(
                    "contract_without_appropriation",
                    entity_type="procurement_contract",
                    entity_id=contract.id,
                    institution_id=contract.institution_id,
                    evidence_id=contract.evidence_id,
                    source_id=contract.source_id,
                    observed={"appropriation": False, "difference": str(contract.current_amount)},
                    comparison={"required": True},
                    threshold={"linked": True},
                )
                if item:
                    candidates.append(item)
        for payment in payments:
            if payment.budget_execution_record_id is None:
                item = self.candidate(
                    "contract_payments_above_reconciled_execution",
                    entity_type="contract_payment",
                    entity_id=payment.id,
                    institution_id=payment.institution_id,
                    evidence_id=payment.evidence_id,
                    source_id=payment.source_id,
                    observed={"reconciled": False, "difference": str(payment.gross_amount)},
                    comparison={"budget_execution_record": None},
                    threshold={"linked": True},
                    period_start=payment.payment_date,
                    period_end=payment.payment_date,
                )
                if item:
                    candidates.append(item)
        contract_ids = {row.id for row in contracts}
        for asset in assets:
            contract_id = asset.metadata_.get("contract_id")
            if asset.acquisition_method == "purchase" and (
                not contract_id or uuid.UUID(str(contract_id)) not in contract_ids
            ):
                item = self.candidate(
                    "contract_asset_without_link",
                    entity_type="public_asset",
                    entity_id=asset.id,
                    institution_id=asset.owner_institution_id,
                    evidence_id=asset.evidence_id,
                    source_id=asset.source_id,
                    observed={"contract_link": False, "difference": str(asset.original_cost)},
                    comparison={"required_for_purchase": True},
                    threshold={"linked": True},
                    period_start=asset.acquisition_date,
                    period_end=asset.acquisition_date,
                )
                if item:
                    candidates.append(item)
        for debt_payment in debt_payments:
            if debt_payment.budget_execution_record_id is None:
                item = self.candidate(
                    "debt_payment_without_budget_record",
                    entity_type="debt_payment",
                    entity_id=debt_payment.id,
                    institution_id=debt_payment.debtor_institution_id,
                    evidence_id=debt_payment.evidence_id,
                    source_id=debt_payment.source_id,
                    observed={
                        "budget_reconciliation": False,
                        "difference": str(debt_payment.total_paid),
                    },
                    comparison={"required": True},
                    threshold={"linked": True},
                    period_start=debt_payment.payment_date,
                    period_end=debt_payment.payment_date,
                )
                if item:
                    candidates.append(item)
        return self.result(candidates, len(entries) + len(contracts) + len(assets))
