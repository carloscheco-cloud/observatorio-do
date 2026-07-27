import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.risk_engine.models import (
    FindingEvidenceLink,
    FindingGroup,
    FindingReview,
    RiskCategory,
    RiskDomain,
    RiskEvaluationRun,
    RiskFinding,
    RiskRule,
    RiskScore,
    RiskSuppression,
    RiskThreshold,
    RiskType,
)

DOMAINS = (
    "institutional_growth",
    "payroll",
    "public_employment",
    "budget",
    "procurement",
    "public_debt",
    "fiscal_risk",
    "public_assets",
    "organizational_structure",
    "appointments",
    "traceability",
    "data_quality",
    "legal_compliance",
    "concentration",
    "historical_change",
    "cross_domain",
    "other",
)
CATEGORIES = (
    "missing_information",
    "inconsistent_information",
    "unusual_growth",
    "unusual_reduction",
    "duplication",
    "incompatibility",
    "concentration",
    "insufficient_competition",
    "deadline",
    "expired_record",
    "financial_difference",
    "missing_traceability",
    "structural_change",
    "multiple_relationship",
    "historical_break",
    "data_quality",
    "other",
)
RULES = {
    "payroll": (
        "monthly_employee_growth",
        "payroll_mass_growth",
        "significant_salary_change",
        "exact_period_duplicate",
        "payroll_without_traceability",
    ),
    "public_employment": (
        "simultaneous_multi_institution_relationship",
        "entry_without_employment",
        "relationship_without_position_or_unit",
    ),
    "budget": (
        "under_execution",
        "over_execution",
        "significant_budget_modification",
        "rapid_budget_change",
        "approved_current_executed_inconsistency",
        "negative_balance",
        "budget_item_without_evidence",
    ),
    "procurement": (
        "single_bidder",
        "low_competition",
        "recurring_supplier",
        "award_concentration",
        "accumulated_contract_growth",
        "multiple_amendments",
        "short_submission_deadline",
        "payment_above_contract",
        "procurement_without_traceability",
        "repeated_emergency_procedure",
    ),
    "public_debt": (
        "upcoming_maturity",
        "overdue_debt",
        "rapid_debt_growth",
        "creditor_concentration",
        "currency_exposure",
        "variable_rate_exposure",
        "executed_guarantee",
        "refinancing_pressure",
        "inconsistent_debt_balance",
    ),
    "public_assets": (
        "missing_asset",
        "asset_without_custodian",
        "stale_inventory",
        "high_value_asset_uninsured",
        "overdue_maintenance",
        "inconsistent_location",
        "inconsistent_valuation",
        "disposal_without_traceability",
        "expired_license",
        "physical_financial_progress_difference",
    ),
    "organizational_structure": (
        "active_institution_without_legal_basis",
        "unit_without_responsible",
        "rapid_structural_growth",
        "recurring_unit_creation",
        "active_position_unoccupied",
    ),
    "appointments": ("appointment_without_evidence", "incompatible_active_appointments"),
    "data_quality": (
        "canonical_without_evidence",
        "stale_source",
        "inaccessible_evidence",
        "historical_change_without_version",
        "cross_module_incompatible_values",
        "duplicate_entities",
        "sensitive_reference_exposed",
        "essential_fields_missing",
    ),
    "cross_domain": (
        "payroll_without_active_employment",
        "employment_with_inactive_unit",
        "paid_position_without_valid_institution",
        "contract_without_appropriation",
        "contract_payments_above_reconciled_execution",
        "contract_asset_without_link",
        "public_work_without_asset_or_project",
        "debt_payment_without_budget_record",
        "transfer_without_budget_record",
        "supplier_person_coincidence",
        "payroll_growth_budget_reduction",
        "asset_growth_without_acquisition",
        "high_spend_low_evidence_freshness",
    ),
}


def seed_risk_engine(
    db: Session,
    *,
    institution_id: uuid.UUID,
    territory_id: uuid.UUID,
    source_id: uuid.UUID,
    evidence_id: uuid.UUID,
) -> None:
    marker = {"controlled": True, "fictitious": True, "seed": "block-10"}
    valid_from = date(2099, 1, 1)
    for code in DOMAINS:
        if db.scalar(select(RiskDomain).where(RiskDomain.stable_code == code)) is None:
            db.add(
                RiskDomain(
                    stable_code=code,
                    official_name=code.replace("_", " ").title(),
                    description="Dominio controlado de señales observables.",
                    valid_from=valid_from,
                    metadata_=marker,
                )
            )
    for code in CATEGORIES:
        if db.scalar(select(RiskCategory).where(RiskCategory.stable_code == code)) is None:
            db.add(
                RiskCategory(
                    stable_code=code,
                    official_name=code.replace("_", " ").title(),
                    description="Categoría controlada para revisión.",
                    valid_from=valid_from,
                    metadata_=marker,
                )
            )
    db.flush()

    rules: list[RiskRule] = []
    for domain, codes in RULES.items():
        for code in codes:
            risk_type = db.scalar(select(RiskType).where(RiskType.stable_code == code))
            if risk_type is None:
                risk_type = RiskType(
                    stable_code=code,
                    official_name=code.replace("_", " ").title(),
                    description="Señal observable reproducible; no constituye acusación.",
                    domain=domain,
                    category=_category(code),
                    default_severity="review_required",
                    public_explanation_template="Dato observado sujeto a revisión humana.",
                    internal_explanation_template="Comparar valores estructurados y evidencia.",
                    recommended_review_action="Verificar evidencia y contexto.",
                    status="active",
                    valid_from=valid_from,
                    source_id=source_id,
                    evidence_id=evidence_id,
                    metadata_=marker,
                )
                db.add(risk_type)
                db.flush()
            rule = db.scalar(
                select(RiskRule).where(RiskRule.stable_code == f"b10.{code}", RiskRule.version == 1)
            )
            if rule is None:
                rule = RiskRule(
                    stable_code=f"b10.{code}",
                    name=risk_type.official_name,
                    description=risk_type.description,
                    domain=domain,
                    risk_type_id=risk_type.id,
                    rule_type="cross_domain" if domain == "cross_domain" else "threshold",
                    version=1,
                    severity="review_required",
                    threshold_config={"operator": "configured", "value": 1},
                    evaluation_window={"months": 1},
                    required_fields=["entity_id", "evidence_id"],
                    supported_entity_types=[domain],
                    public_message_template="Se observó {observation}.",
                    internal_message_template="Regla {rule}; umbral {threshold}.",
                    enabled=True,
                    valid_from=valid_from,
                    requires_human_review=True,
                    created_by_actor_type="human",
                    source_id=source_id,
                    evidence_id=evidence_id,
                    metadata_=marker,
                )
                db.add(rule)
                db.flush()
            rules.append(rule)
    primary_rule = rules[0]
    threshold = db.scalar(
        select(RiskThreshold).where(RiskThreshold.risk_rule_id == primary_rule.id)
    )
    reviewer_id = uuid.uuid5(uuid.NAMESPACE_URL, "observatorio.test/reviewer")
    if threshold is None:
        db.add(
            RiskThreshold(
                risk_rule_id=primary_rule.id,
                scope_type="institution",
                scope_id=institution_id,
                threshold_key="percentage",
                threshold_value={"value": 20, "unit": "percent"},
                valid_from=valid_from,
                status="approved",
                approved_by_actor_id=reviewer_id,
                metadata_=marker,
            )
        )
    run = db.scalar(
        select(RiskEvaluationRun).where(RiskEvaluationRun.run_code == "B10-SEED-RUN-001")
    )
    if run is None:
        now = datetime(2099, 2, 1, tzinfo=UTC)
        run = RiskEvaluationRun(
            run_code="B10-SEED-RUN-001",
            trigger_type="manual",
            status="completed",
            started_at=now,
            completed_at=now,
            scope={"controlled": True},
            rules_requested=len(rules),
            rules_executed=len(rules),
            records_evaluated=3,
            findings_created=3,
            engine_version="10.0.0",
            initiated_by_actor_type="human",
            initiated_by_actor_id=reviewer_id,
            metadata_=marker,
        )
        db.add(run)
        db.flush()
    examples = (
        ("B10-FINDING-CONFIRMED", "confirmed_signal", "internal", 1),
        ("B10-FINDING-DISMISSED", "dismissed", "internal", 1),
        ("B10-FINDING-RECURRENT", "pending_review", "internal", 3),
    )
    seeded: list[RiskFinding] = []
    for index, (code, status, visibility, occurrences) in enumerate(examples):
        finding = db.scalar(select(RiskFinding).where(RiskFinding.finding_code == code))
        if finding is None:
            finding = RiskFinding(
                finding_code=code,
                deduplication_fingerprint=f"{index + 1:064x}",
                risk_type_id=rules[index].risk_type_id,
                risk_rule_id=rules[index].id,
                evaluation_run_id=run.id,
                domain=rules[index].domain,
                entity_type="institution",
                entity_id=institution_id,
                institution_id=institution_id,
                territory_id=territory_id,
                period_start=valid_from,
                period_end=date(2099, 1, 31),
                observed_value={"controlled": True, "value": index + 1},
                comparison_value={"value": index},
                threshold_value={"value": 1},
                title="Señal ficticia controlada",
                public_explanation=(
                    "Diferencia ficticia para revisión. No permite concluir fraude, corrupción, "
                    "ilegalidad, culpabilidad ni intención."
                ),
                internal_explanation=(
                    "Ejemplo reproducible con valores estructurados y evidencia controlada."
                ),
                severity="review_required",
                confidence_level="deterministic",
                status=status,
                first_detected_at=run.started_at,
                last_detected_at=run.started_at,
                occurrence_count=occurrences,
                evidence_count=1,
                requires_human_review=True,
                reviewer_notes="Revisión ficticia." if status != "pending_review" else None,
                reviewed_by_actor_id=reviewer_id if status != "pending_review" else None,
                reviewed_at=run.started_at if status != "pending_review" else None,
                visibility=visibility,
                metadata_=marker,
            )
            db.add(finding)
            db.flush()
            db.add(
                FindingEvidenceLink(
                    finding_id=finding.id,
                    evidence_id=evidence_id,
                    source_id=source_id,
                    relationship_type="primary",
                    relevance_score=Decimal("1"),
                    excerpt="Evidencia ficticia controlada.",
                    metadata_=marker,
                )
            )
            if status != "pending_review":
                db.add(
                    FindingReview(
                        finding_id=finding.id,
                        reviewer_actor_id=reviewer_id,
                        review_action="confirm" if status == "confirmed_signal" else "dismiss",
                        previous_status="pending_review",
                        new_status=status,
                        review_date=run.started_at,
                        notes="Revisión humana ficticia y controlada.",
                        evidence_added_count=0,
                        severity_before="review_required",
                        severity_after="review_required",
                        metadata_=marker,
                    )
                )
        seeded.append(finding)
    if db.scalar(select(FindingGroup).where(FindingGroup.stable_code == "B10-GROUP-001")) is None:
        db.add(
            FindingGroup(
                stable_code="B10-GROUP-001",
                title="Fenómeno recurrente ficticio",
                domain="payroll",
                first_detected_at=run.started_at,
                last_detected_at=run.started_at,
                metadata_=marker,
            )
        )
    if (
        db.scalar(select(RiskSuppression).where(RiskSuppression.risk_rule_id == primary_rule.id))
        is None
    ):
        db.add(
            RiskSuppression(
                risk_rule_id=primary_rule.id,
                institution_id=institution_id,
                reason="Excepción temporal ficticia con evidencia controlada.",
                valid_from=valid_from,
                valid_to=date(2099, 3, 1),
                approved_by_actor_id=reviewer_id,
                source_id=source_id,
                evidence_id=evidence_id,
                metadata_=marker,
            )
        )
    if (
        db.scalar(
            select(RiskScore).where(
                RiskScore.entity_id == institution_id,
                RiskScore.model_or_formula_version == "observable-v1",
            )
        )
        is None
    ):
        db.add(
            RiskScore(
                entity_type="institution",
                entity_id=institution_id,
                calculation_date=date(2099, 2, 1),
                period_start=valid_from,
                period_end=date(2099, 1, 31),
                total_score=Decimal("16"),
                score_band="moderate",
                component_scores={"review_required": 2},
                finding_count=3,
                high_priority_count=0,
                data_quality_penalty=Decimal("0"),
                model_or_formula_version="observable-v1",
                evaluation_run_id=run.id,
                status="current",
                metadata_=marker,
            )
        )


def _category(code: str) -> str:
    if "duplicate" in code:
        return "duplication"
    if "without" in code or "missing" in code:
        return "missing_information"
    if "concentration" in code:
        return "concentration"
    if "growth" in code:
        return "unusual_growth"
    if "inconsistent" in code or "incompatible" in code:
        return "inconsistent_information"
    if "traceability" in code or "evidence" in code:
        return "missing_traceability"
    return "other"
