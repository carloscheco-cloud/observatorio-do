from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.modules.digital_transparency.methodology import (
    ComponentInput,
    calculate,
    maturity,
    public_classification,
)
from app.modules.digital_transparency.methodology_v1_1 import RULE_BY_CODE, VERSION
from app.modules.digital_transparency.models import (
    AssessmentComponent,
    DigitalTransparencyLoadRecord,
    DocumentRequirement,
    DocumentResource,
    ResourceCheck,
    ResourceCheckStatus,
    SearchabilityCheck,
    TransparencyAssessment,
    TransparencyMethodology,
    TransparencyObservation,
)
from app.modules.evidence.models import Evidence
from app.modules.institutions.models import Institution

MANIFEST_PATH = Path(__file__).with_name("pe06d_manifest.json")
PE06B_MANIFEST_PATH = Path(__file__).with_name("pe06b_manifest.json")
MANIFEST_VERSION = "PE-06D-2026-08-04"
ASSESSOR = "PE-06D OED-TD-1.1 pilot"
NEW_DIMENSIONS = tuple(RULE_BY_CODE[code].dimension for code in RULE_BY_CODE)
EXPECTED_DIMENSIONS = {
    "institutional_identity",
    "legal_framework",
    "organizational_structure",
    "current_authorities",
    "appointment_acts",
    "official_contact_information",
    "document_searchability",
    "stable_links",
}


@dataclass
class Summary:
    created: int = 0
    unchanged: int = 0
    removed: int = 0
    errors: int = 0


def summary_dict(value: Summary) -> dict[str, int]:
    return asdict(value)


def read_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != MANIFEST_VERSION or data.get("methodology_version") != VERSION:
        raise ValueError("unsupported PE-06D manifest")
    institutions = data.get("institutions")
    if not isinstance(institutions, list) or len(institutions) != 5:
        raise ValueError("PE-06D requires exactly five pilot institutions")
    if len({item["slug"] for item in institutions}) != 5:
        raise ValueError("PE-06D institution slugs must be unique")
    required = {
        "dimension",
        "resource_key",
        "rule_code",
        "calculation_reason",
        "public_explanation",
        "limitations",
        "contradictions",
        "check",
    }
    expected_new = EXPECTED_DIMENSIONS - {
        "institutional_identity",
        "current_authorities",
        "appointment_acts",
    }
    for institution in institutions:
        dimensions = institution.get("dimensions", [])
        if len(dimensions) != 5 or {item.get("dimension") for item in dimensions} != expected_new:
            raise ValueError("each PE-06D institution requires exactly five selections")
        for item in dimensions:
            if not required <= item.keys() or any(not str(item[key]).strip() for key in required):
                raise ValueError("PE-06D selection traceability is incomplete")
            rule = RULE_BY_CODE.get(item["rule_code"])
            if rule is None or rule.dimension != item["dimension"]:
                raise ValueError("invalid or mismatched PE-06D rule_code")
    return data


def _pe06b_resources() -> dict[str, dict[str, dict[str, Any]]]:
    data = json.loads(PE06B_MANIFEST_PATH.read_text(encoding="utf-8"))
    return {
        institution["slug"]: {resource["key"]: resource for resource in institution["resources"]}
        for institution in data["institutions"]
    }


def _own(db: Session, kind: str, identifier: uuid.UUID) -> None:
    db.add(
        DigitalTransparencyLoadRecord(
            manifest_version=MANIFEST_VERSION, record_type=kind, record_id=identifier
        )
    )


def _historical_selection(
    db: Session, institution: Institution, raw: dict[str, Any], resource_raw: dict[str, Any]
) -> tuple[
    TransparencyObservation,
    Evidence,
    DocumentResource,
    list[ResourceCheck],
    list[SearchabilityCheck],
]:
    resource = db.scalar(
        select(DocumentResource).where(
            DocumentResource.institution_id == institution.id,
            DocumentResource.canonical_url == resource_raw["url"],
        )
    )
    if resource is None:
        raise ValueError(f"PE-06B resource not found: {resource_raw['url']}")
    requirement = db.scalar(
        select(DocumentRequirement).where(
            DocumentRequirement.code == raw["dimension"],
            DocumentRequirement.methodology_version == "OED-TD-1.0",
        )
    )
    if requirement is None:
        raise ValueError("historical requirement not found")
    observation = db.scalar(
        select(TransparencyObservation).where(
            TransparencyObservation.institution_id == institution.id,
            TransparencyObservation.requirement_id == requirement.id,
            TransparencyObservation.resource_id == resource.id,
            TransparencyObservation.observed_at
            == datetime.fromisoformat("2026-08-04T12:00:00-04:00"),
        )
    )
    if observation is None:
        raise ValueError("representative PE-06B observation not found")
    evidence = db.get(Evidence, observation.evidence_id)
    if evidence is None:
        raise ValueError("representative historical evidence not found")
    resource_checks = list(
        db.scalars(select(ResourceCheck).where(ResourceCheck.resource_id == resource.id))
    )
    if raw["check"] == "resource_with_complementary_technical_error":
        resource_checks.extend(
            db.scalars(
                select(ResourceCheck)
                .join(DocumentResource, DocumentResource.id == ResourceCheck.resource_id)
                .where(
                    DocumentResource.institution_id == institution.id,
                    ResourceCheck.resource_id != resource.id,
                    ResourceCheck.status == ResourceCheckStatus.TECHNICAL_ERROR,
                )
            )
        )
        if not any(item.status.value == "technical_error" for item in resource_checks):
            raise ValueError("MISPAS complementary technical_error check not found")
    search_checks = list(
        db.scalars(select(SearchabilityCheck).where(SearchabilityCheck.resource_id == resource.id))
    )
    if (
        raw["check"]
        in {"resource", "resource_and_searchability", "resource_with_complementary_technical_error"}
        and not resource_checks
    ):
        raise ValueError("required ResourceCheck not found")
    if raw["check"] in {"searchability", "resource_and_searchability"} and not search_checks:
        raise ValueError("required SearchabilityCheck not found")
    return observation, evidence, resource, resource_checks, search_checks


def load(db: Session, *, dry_run: bool = False, path: Path = MANIFEST_PATH) -> Summary:
    data = read_manifest(path)
    resources = _pe06b_resources()
    result = Summary()
    assessment_date = date.fromisoformat(data["assessment_date"])
    try:
        methodology = db.get(TransparencyMethodology, VERSION)
        if methodology is None or methodology.status != "published" or not methodology.is_immutable:
            raise ValueError("published OED-TD-1.1 must exist before PE-06D")
        for raw_institution in data["institutions"]:
            institution = db.scalar(
                select(Institution).where(Institution.slug == raw_institution["slug"])
            )
            if institution is None:
                raise ValueError(f"pilot institution not found: {raw_institution['slug']}")
            existing = db.scalar(
                select(TransparencyAssessment).where(
                    TransparencyAssessment.institution_id == institution.id,
                    TransparencyAssessment.methodology_version == VERSION,
                    TransparencyAssessment.assessment_date == assessment_date,
                )
            )
            previous = db.scalar(
                select(TransparencyAssessment).where(
                    TransparencyAssessment.institution_id == institution.id,
                    TransparencyAssessment.assessor == "PE-06B controlled pilot",
                )
            )
            if previous is None:
                raise ValueError("PE-06D requires PE-06B")
            inherited = list(
                db.scalars(
                    select(AssessmentComponent).where(
                        AssessmentComponent.assessment_id == previous.id
                    )
                )
            )
            if {item.dimension for item in inherited} != {
                "institutional_identity",
                "current_authorities",
                "appointment_acts",
            }:
                raise ValueError("PE-06B inherited components are incomplete")
            selections: list[
                tuple[
                    dict[str, Any],
                    Any,
                    TransparencyObservation,
                    Evidence,
                    DocumentResource,
                    list[ResourceCheck],
                    list[SearchabilityCheck],
                ]
            ] = []
            for raw in raw_institution["dimensions"]:
                rule = RULE_BY_CODE[raw["rule_code"]]
                observation, evidence, resource, resource_checks, search_checks = (
                    _historical_selection(
                        db,
                        institution,
                        raw,
                        resources[raw_institution["slug"]][raw["resource_key"]],
                    )
                )
                selections.append(
                    (raw, rule, observation, evidence, resource, resource_checks, search_checks)
                )
            if existing is not None:
                component_count = len(
                    list(
                        db.scalars(
                            select(AssessmentComponent).where(
                                AssessmentComponent.assessment_id == existing.id
                            )
                        )
                    )
                )
                if existing.assessor != ASSESSOR or component_count != 8:
                    raise ValueError("conflicting OED-TD-1.1 assessment exists")
                result.unchanged += 1 + component_count
                continue
            inputs = [
                ComponentInput(item.dimension, item.score, item.is_applicable) for item in inherited
            ]
            inputs.extend(
                ComponentInput(rule.dimension, rule.awarded_score) for _, rule, *_ in selections
            )
            score = calculate(inputs)
            coverage = score.maximum_score
            details = {
                "formula": "raw / evaluated maximum * 100",
                "source_assessment_id": str(previous.id),
                "inherited_component_ids": [str(item.id) for item in inherited],
                "pending_dimensions": [],
                "selections": [
                    {
                        "dimension": raw["dimension"],
                        "observation_id": str(observation.id),
                        "evidence_id": str(evidence.id),
                        "resource_id": str(resource.id),
                        "complementary_resource_ids": [
                            str(item.id)
                            for item in db.scalars(
                                select(DocumentResource).where(
                                    DocumentResource.institution_id == institution.id,
                                    DocumentResource.id != resource.id,
                                )
                            )
                        ],
                        "resource_check_ids": [str(item.id) for item in resource_checks],
                        "searchability_check_ids": [str(item.id) for item in search_checks],
                        "rule_code": raw["rule_code"],
                        "calculation_reason": raw["calculation_reason"],
                        "public_explanation": raw["public_explanation"],
                        "limitations": raw["limitations"],
                        "contradictions": raw["contradictions"],
                    }
                    for (
                        raw,
                        _,
                        observation,
                        evidence,
                        resource,
                        resource_checks,
                        search_checks,
                    ) in selections
                ],
            }
            assessment = TransparencyAssessment(
                id=uuid.uuid4(),
                institution_id=institution.id,
                methodology_version=VERSION,
                assessment_date=assessment_date,
                score=score.raw_score,
                maximum_score=score.maximum_score,
                normalized_score=score.normalized_score,
                coverage_percentage=coverage,
                observations_count=8,
                verified_count=8,
                unresolved_count=0,
                broken_links_count=0,
                assessor=ASSESSOR,
                calculation_details=details,
                status=maturity(coverage),
                maturity_status=maturity(coverage),
                classification_public=public_classification(score.normalized_score, coverage),
                rank=None,
                comparison_position=None,
            )
            db.add(assessment)
            _own(db, "assessment", assessment.id)
            result.created += 1
            db.flush()
            for original in inherited:
                component = AssessmentComponent(
                    id=uuid.uuid4(),
                    assessment_id=assessment.id,
                    requirement_id=original.requirement_id,
                    dimension=original.dimension,
                    weight=original.weight,
                    score=original.score,
                    maximum_score=original.maximum_score,
                    is_applicable=original.is_applicable,
                    rationale=original.rationale,
                    observation_ids=list(original.observation_ids),
                    verification_status=original.verification_status,
                    observation_id=original.observation_id,
                    evidence_id=original.evidence_id,
                    methodology_version=VERSION,
                    calculation_reason=(
                        f"Heredado sin alteración del componente PE-06B {original.id}, "
                        "cuya referencia procede de PE-05."
                    ),
                    rule_code=None,
                    public_explanation="Componente PE-05 heredado sin recalcular.",
                )
                db.add(component)
                _own(db, "component", component.id)
                result.created += 1
            for raw, rule, observation, evidence, _, _, _ in selections:
                requirement = db.get(DocumentRequirement, observation.requirement_id)
                if requirement is None:
                    raise ValueError("selected requirement missing")
                component = AssessmentComponent(
                    id=uuid.uuid4(),
                    assessment_id=assessment.id,
                    requirement_id=requirement.id,
                    dimension=rule.dimension,
                    weight=rule.maximum_score,
                    score=rule.awarded_score,
                    maximum_score=rule.maximum_score,
                    is_applicable=True,
                    rationale=raw["public_explanation"],
                    observation_ids=[str(observation.id)],
                    verification_status=observation.verification_status,
                    observation_id=observation.id,
                    evidence_id=evidence.id,
                    methodology_version=VERSION,
                    calculation_reason=raw["calculation_reason"],
                    rule_code=rule.rule_code,
                    public_explanation=raw["public_explanation"],
                )
                db.add(component)
                _own(db, "component", component.id)
                result.created += 1
        db.flush()
        db.rollback() if dry_run else db.commit()
        return result
    except Exception:
        db.rollback()
        raise


def recalculate(db: Session, *, dry_run: bool = False) -> Summary:
    result = Summary()
    assessments = list(
        db.scalars(
            select(TransparencyAssessment).where(TransparencyAssessment.assessor == ASSESSOR)
        )
    )
    if len(assessments) != 5:
        raise ValueError("PE-06D requires five loaded assessments")
    for assessment in assessments:
        components = list(
            db.scalars(
                select(AssessmentComponent).where(
                    AssessmentComponent.assessment_id == assessment.id
                )
            )
        )
        if len(components) != 8 or {item.dimension for item in components} != EXPECTED_DIMENSIONS:
            raise ValueError("PE-06D assessment must contain eight dimensions")
        score = calculate(
            [ComponentInput(item.dimension, item.score, item.is_applicable) for item in components]
        )
        coverage = score.maximum_score
        expected = (
            score.raw_score,
            score.maximum_score,
            score.normalized_score,
            coverage,
            maturity(coverage),
            None,
            None,
        )
        actual = (
            assessment.score,
            assessment.maximum_score,
            assessment.normalized_score,
            assessment.coverage_percentage,
            assessment.maturity_status,
            assessment.rank,
            assessment.comparison_position,
        )
        if actual != expected:
            raise ValueError("PE-06D historical assessment differs from immutable components")
        result.unchanged += 1
    db.rollback() if dry_run else db.commit()
    return result


def audit_report(db: Session) -> list[dict[str, object]]:
    rows = db.execute(
        select(Institution.name, TransparencyAssessment)
        .join(TransparencyAssessment, TransparencyAssessment.institution_id == Institution.id)
        .where(TransparencyAssessment.assessor == ASSESSOR)
        .order_by(Institution.name)
    ).all()
    report: list[dict[str, object]] = []
    for name, assessment in rows:
        components = list(
            db.scalars(
                select(AssessmentComponent)
                .where(AssessmentComponent.assessment_id == assessment.id)
                .order_by(AssessmentComponent.dimension)
            )
        )
        selection_by_dimension = {
            item["dimension"]: item for item in assessment.calculation_details["selections"]
        }
        report.append(
            {
                "institution": name,
                "dimensions": [
                    {
                        "dimension": component.dimension,
                        "rule_code": component.rule_code or "INHERITED-PE05-OED-TD-1.0",
                        "score": str(component.score),
                        "maximum_score": str(component.maximum_score),
                        "observation_id": str(component.observation_id),
                        "evidence_id": str(component.evidence_id),
                        "public_explanation": component.public_explanation,
                        "limitations": selection_by_dimension.get(component.dimension, {}).get(
                            "limitations", "Componente histórico heredado sin alteración."
                        ),
                        "calculation_reason": component.calculation_reason,
                    }
                    for component in components
                ],
                "raw_score": str(assessment.score),
                "evaluated_max_score": str(assessment.maximum_score),
                "normalized_score": str(assessment.normalized_score),
                "coverage": str(assessment.coverage_percentage),
                "maturity": assessment.maturity_status,
                "pending_dimensions": [],
                "rank": assessment.rank,
                "comparison_position": assessment.comparison_position,
            }
        )
    return report


def rollback(db: Session, *, dry_run: bool = False) -> Summary:
    records = list(
        db.scalars(
            select(DigitalTransparencyLoadRecord).where(
                DigitalTransparencyLoadRecord.manifest_version == MANIFEST_VERSION
            )
        )
    )
    result = Summary()
    for kind, model in (("component", AssessmentComponent), ("assessment", TransparencyAssessment)):
        ids = [record.record_id for record in records if record.record_type == kind]
        if ids:
            db.execute(delete(model).where(model.id.in_(ids)))
            result.removed += len(ids)
    if records:
        db.execute(
            delete(DigitalTransparencyLoadRecord).where(
                DigitalTransparencyLoadRecord.id.in_([record.id for record in records])
            )
        )
        result.removed += len(records)
    else:
        result.unchanged = 1
    db.rollback() if dry_run else db.commit()
    return result
