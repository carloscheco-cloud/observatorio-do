from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.digital_transparency.methodology import (
    VERSION,
    ComponentInput,
    calculate,
    maturity,
    public_classification,
)
from app.modules.digital_transparency.models import (
    AssessmentComponent,
    ConfidenceLevel,
    DigitalTransparencyLoadRecord,
    DocumentRequirement,
    DocumentResource,
    ManualResearchTask,
    ResourceCheck,
    ResourceCheckStatus,
    ResourceCheckType,
    ReviewerType,
    SearchabilityCheck,
    SearchabilityMethod,
    SearchabilityResult,
    TransparencyAssessment,
    TransparencyObservation,
    VerificationStatus,
)
from app.modules.digital_transparency.resource_checks import create_resource_check
from app.modules.digital_transparency.schemas import ResourceCheckCreate, SearchabilityCheckCreate
from app.modules.digital_transparency.searchability_checks import create_searchability_check
from app.modules.evidence.models import Evidence
from app.modules.institutions.models import Institution
from app.modules.sources.models import Source

MANIFEST_PATH = Path(__file__).with_name("pe06b_manifest.json")
MANIFEST_VERSION = "PE-06B-2026-08-04"
DIMENSIONS = (
    "legal_framework",
    "organizational_structure",
    "official_contact_information",
    "document_searchability",
    "stable_links",
)


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
        raise ValueError("unsupported PE-06B manifest")
    institutions = data.get("institutions")
    if not isinstance(institutions, list) or len(institutions) != 5:
        raise ValueError("PE-06B requires exactly five pilot institutions")
    slugs = {item["slug"] for item in institutions}
    if len(slugs) != 5 or any("presidencia" in slug for slug in slugs):
        raise ValueError("invalid PE-06B institutional scope")
    for institution in institutions:
        resources = institution.get("resources", [])
        if {item["dimension"] for item in resources} != set(DIMENSIONS[:3]):
            raise ValueError(
                "each institution requires attributed legal, structure and contact resources"
            )
        if any(not item["url"].startswith("https://") for item in resources):
            raise ValueError("only explicit official HTTPS resources are accepted")
    return data


def _own(db: Session, kind: str, identifier: uuid.UUID) -> None:
    db.add(
        DigitalTransparencyLoadRecord(
            manifest_version=MANIFEST_VERSION, record_type=kind, record_id=identifier
        )
    )


def _hash(url: str, excerpt: str) -> str:
    return hashlib.sha256(f"{MANIFEST_VERSION}|{url}|{excerpt}".encode()).hexdigest()


def _requirement(db: Session, code: str) -> DocumentRequirement:
    item = db.scalar(
        select(DocumentRequirement).where(
            DocumentRequirement.code == code,
            DocumentRequirement.methodology_version == VERSION,
        )
    )
    if item is None:
        raise ValueError("PE-05 requirements must exist before PE-06B")
    return item


def _source_evidence(
    db: Session,
    institution: dict[str, Any],
    raw: dict[str, Any],
    observed_at: datetime,
    result: Summary,
) -> tuple[Source, Evidence]:
    source = db.scalar(select(Source).where(Source.url == raw["url"]))
    if source is None:
        source = Source(
            id=uuid.uuid4(),
            name=raw["title"],
            url=raw["url"],
            publisher=institution["name"],
            is_official=True,
            retrieved_at=observed_at,
        )
        db.add(source)
        _own(db, "source", source.id)
        result.created += 1
    elif not source.is_official or source.publisher != institution["name"]:
        raise ValueError(f"doubtful institutional attribution: {raw['url']}")
    else:
        result.unchanged += 1
    digest = _hash(raw["url"], raw["excerpt"])
    evidence = db.scalar(select(Evidence).where(Evidence.content_hash == digest))
    if evidence is None:
        evidence = Evidence(
            id=uuid.uuid4(),
            source_id=source.id,
            title=raw["title"],
            excerpt=raw["excerpt"],
            locator=raw["url"],
            content_hash=digest,
            metadata_={"pilot": MANIFEST_VERSION, "consulted_at": observed_at.isoformat()},
            observed_at=observed_at,
        )
        db.add(evidence)
        _own(db, "evidence", evidence.id)
        result.created += 1
    else:
        result.unchanged += 1
    return source, evidence


def _resource(
    db: Session,
    institution: Institution,
    requirement: DocumentRequirement,
    source: Source,
    evidence: Evidence,
    raw: dict[str, Any],
    observed_at: datetime,
    result: Summary,
) -> DocumentResource:
    item = db.scalar(
        select(DocumentResource).where(
            DocumentResource.institution_id == institution.id,
            DocumentResource.requirement_id == requirement.id,
            DocumentResource.canonical_url == raw["url"],
        )
    )
    if item is not None:
        result.unchanged += 1
        return item
    item = DocumentResource(
        id=uuid.uuid4(),
        institution_id=institution.id,
        requirement_id=requirement.id,
        title=raw["title"],
        resource_type="legal_document" if raw["type"] == "pdf" else "official_page",
        canonical_url=raw["url"],
        source_id=source.id,
        retrieved_at=observed_at,
        mime_type=raw["http"]["mime"],
        notes="Recurso oficial atribuido expresamente y comprobado una vez por PE-06B.",
    )
    db.add(item)
    _own(db, "resource", item.id)
    result.created += 1
    db.flush()
    return item


def _checks(
    db: Session,
    resource: DocumentResource,
    evidence: Evidence,
    raw: dict[str, Any],
    observed_at: datetime,
    result: Summary,
) -> None:
    existing_http = db.scalar(
        select(ResourceCheck).where(
            ResourceCheck.resource_id == resource.id,
            ResourceCheck.checked_at == observed_at,
            ResourceCheck.check_type == ResourceCheckType.HTTP_AVAILABILITY,
        )
    )
    if existing_http is None:
        http = raw["http"]
        resource_check = create_resource_check(
            db,
            ResourceCheckCreate(
                resource_id=str(resource.id),
                checked_at=observed_at,
                check_type=ResourceCheckType.HTTP_AVAILABILITY,
                status=ResourceCheckStatus.AVAILABLE,
                http_status=http["status"],
                final_url=raw["url"],
                redirect_count=0,
                response_time_ms=http["ms"],
                mime_type=http["mime"],
                content_length=http["length"],
                attempt_number=1,
                user_agent="ObservatorioDO-PE06B/1.0",
                timeout_seconds=15,
                tool_name="PowerShell Invoke-WebRequest",
                tool_version="7",
                evidence_id=str(evidence.id),
                notes="Una comprobación real; no se infieren propiedades no observadas.",
            ),
        )
        _own(db, "resource_check", resource_check.id)
        result.created += 1
    else:
        result.unchanged += 1
    existing_search = db.scalar(
        select(SearchabilityCheck).where(
            SearchabilityCheck.resource_id == resource.id,
            SearchabilityCheck.checked_at == observed_at,
        )
    )
    if existing_search is None:
        search = raw["search"]
        searchability_check = create_searchability_check(
            db,
            SearchabilityCheckCreate(
                resource_id=str(resource.id),
                checked_at=observed_at,
                method=SearchabilityMethod(search["method"]),
                result=SearchabilityResult(search["result"]),
                text_detected=True,
                selectable_text=True if raw["type"] == "pdf" else None,
                title_detected=search["title"],
                publication_date_detected=search["date"],
                document_number_detected=search["number"],
                tool_name="OpenAI web text extraction"
                if raw["type"] == "pdf"
                else "manual HTML text inspection",
                tool_version="2026-08-04",
                evidence_id=str(evidence.id),
                notes="Sin OCR; los campos no observados permanecen nulos.",
            ),
        )
        _own(db, "searchability_check", searchability_check.id)
        result.created += 1
    else:
        result.unchanged += 1


def _technical_error_check(
    db: Session,
    institution: Institution,
    requirement: DocumentRequirement,
    raw: dict[str, Any],
    observed_at: datetime,
    result: Summary,
) -> None:
    owner = {"name": institution.name}
    source, evidence = _source_evidence(db, owner, raw, observed_at, result)
    resource = db.scalar(
        select(DocumentResource).where(
            DocumentResource.institution_id == institution.id,
            DocumentResource.requirement_id == requirement.id,
            DocumentResource.canonical_url == raw["url"],
        )
    )
    if resource is None:
        resource = DocumentResource(
            id=uuid.uuid4(),
            institution_id=institution.id,
            requirement_id=requirement.id,
            title=raw["title"],
            resource_type="official_page",
            canonical_url=raw["url"],
            source_id=source.id,
            retrieved_at=observed_at,
            notes="Recurso comprobado, excluido de puntuación por error técnico.",
        )
        db.add(resource)
        _own(db, "resource", resource.id)
        result.created += 1
        db.flush()
    else:
        result.unchanged += 1
    existing = db.scalar(
        select(ResourceCheck).where(
            ResourceCheck.resource_id == resource.id,
            ResourceCheck.checked_at == observed_at,
            ResourceCheck.check_type == ResourceCheckType.REDIRECT_RESOLUTION,
        )
    )
    if existing is None:
        http = raw["http"]
        check = create_resource_check(
            db,
            ResourceCheckCreate(
                resource_id=str(resource.id),
                checked_at=observed_at,
                check_type=ResourceCheckType.REDIRECT_RESOLUTION,
                status=ResourceCheckStatus.TECHNICAL_ERROR,
                http_status=http["status"],
                attempt_number=1,
                user_agent="ObservatorioDO-PE06B/1.0",
                timeout_seconds=15,
                response_time_ms=http["ms"],
                error_type=http["error_type"],
                error_message=http["error_message"],
                tool_name="PowerShell Invoke-WebRequest",
                tool_version="7",
                evidence_id=str(evidence.id),
                notes="Bucle de redirección observado; no es broken_link_confirmed.",
            ),
        )
        _own(db, "resource_check", check.id)
        result.created += 1
    else:
        result.unchanged += 1


def _observation(
    db: Session,
    institution: Institution,
    requirement: DocumentRequirement,
    resource: DocumentResource,
    evidence: Evidence,
    finding: str,
    status: VerificationStatus,
    observed_at: datetime,
    result: Summary,
) -> TransparencyObservation:
    item = db.scalar(
        select(TransparencyObservation).where(
            TransparencyObservation.institution_id == institution.id,
            TransparencyObservation.requirement_id == requirement.id,
            TransparencyObservation.evidence_id == evidence.id,
            TransparencyObservation.observed_at == observed_at,
        )
    )
    if item is not None:
        result.unchanged += 1
        return item
    item = TransparencyObservation(
        id=uuid.uuid4(),
        institution_id=institution.id,
        requirement_id=requirement.id,
        resource_id=resource.id,
        verification_status=status,
        observed_at=observed_at,
        reviewer_type=ReviewerType.HYBRID,
        search_scope=(
            "Revisión controlada de recursos expresamente atribuidos en el portal oficial; "
            "no es una búsqueda exhaustiva."
        ),
        finding=finding,
        confidence=ConfidenceLevel.HIGH,
        evidence_id=evidence.id,
        methodology_version=VERSION,
        notes="No localizado no equivale a inexistente; no se envió solicitud SAIP.",
    )
    db.add(item)
    _own(db, "observation", item.id)
    result.created += 1
    db.flush()
    return item


def load(db: Session, *, dry_run: bool = False, path: Path = MANIFEST_PATH) -> Summary:
    data = read_manifest(path)
    result = Summary()
    observed_at = datetime.fromisoformat(data["observed_at"])
    assessment_date = date.fromisoformat(data["assessment_date"])
    try:
        requirements = {code: _requirement(db, code) for code in DIMENSIONS}
        for raw in data["technical_checks"]:
            institution = db.scalar(select(Institution).where(Institution.slug == raw["slug"]))
            if institution is None:
                raise ValueError("technical check institution not found")
            _technical_error_check(
                db, institution, requirements[raw["dimension"]], raw, observed_at, result
            )
        for raw_institution in data["institutions"]:
            institution = db.scalar(
                select(Institution).where(Institution.slug == raw_institution["slug"])
            )
            if institution is None or institution.name != raw_institution["name"]:
                raise ValueError(f"pilot institution not found: {raw_institution['slug']}")

            pending_observations: list[TransparencyObservation] = []
            resource_map: dict[str, tuple[DocumentResource, Evidence]] = {}
            for raw in raw_institution["resources"]:
                source, evidence = _source_evidence(db, raw_institution, raw, observed_at, result)
                resource = _resource(
                    db,
                    institution,
                    requirements[raw["dimension"]],
                    source,
                    evidence,
                    raw,
                    observed_at,
                    result,
                )
                _checks(db, resource, evidence, raw, observed_at, result)
                pending_observations.append(
                    _observation(
                        db,
                        institution,
                        requirements[raw["dimension"]],
                        resource,
                        evidence,
                        raw["excerpt"],
                        VerificationStatus.PARTIALLY_VERIFIED,
                        observed_at,
                        result,
                    )
                )
                resource_map[raw["key"]] = (resource, evidence)

            legal_resource, legal_evidence = resource_map["legal"]
            pending_observations.append(
                _observation(
                    db,
                    institution,
                    requirements["document_searchability"],
                    legal_resource,
                    legal_evidence,
                    "Se extrajo texto del recurso evaluado. OED-TD-1.0 no define una escala "
                    "para transformar este resultado técnico en puntos.",
                    VerificationStatus.PARTIALLY_VERIFIED,
                    observed_at,
                    result,
                )
            )
            pending_observations.append(
                _observation(
                    db,
                    institution,
                    requirements["stable_links"],
                    legal_resource,
                    legal_evidence,
                    (
                        "La URL respondió 200 una vez y el índice general produjo un bucle de "
                        "redirección registrado como technical_error; no hay enlace roto "
                        "confirmado ni estabilidad probada."
                        if raw_institution["slug"]
                        == "ministerio-de-salud-publica-y-asistencia-social"
                        else "La URL respondió 200 una vez; no prueba permanencia futura. "
                        "OED-TD-1.0 no define una escala temporal para esta dimensión."
                    ),
                    VerificationStatus.PARTIALLY_VERIFIED,
                    observed_at,
                    result,
                )
            )

            previous = db.scalar(
                select(TransparencyAssessment)
                .where(
                    TransparencyAssessment.institution_id == institution.id,
                    TransparencyAssessment.methodology_version == VERSION,
                    TransparencyAssessment.assessment_date < assessment_date,
                )
                .order_by(TransparencyAssessment.assessment_date.desc())
            )
            if previous is None:
                raise ValueError("PE-06B requires the prior PE-05 assessment")
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
                raise ValueError("PE-05 components are incomplete or were modified")
            score = calculate(
                [
                    ComponentInput(item.dimension, item.score, item.is_applicable)
                    for item in inherited
                ]
            )
            coverage = sum(
                (item.maximum_score for item in inherited if item.is_applicable), Decimal()
            )
            assessment = db.scalar(
                select(TransparencyAssessment).where(
                    TransparencyAssessment.institution_id == institution.id,
                    TransparencyAssessment.methodology_version == VERSION,
                    TransparencyAssessment.assessment_date == assessment_date,
                )
            )
            if assessment is None:
                assessment = TransparencyAssessment(
                    id=uuid.uuid4(),
                    institution_id=institution.id,
                    methodology_version=VERSION,
                    assessment_date=assessment_date,
                    score=score.raw_score,
                    maximum_score=score.maximum_score,
                    normalized_score=score.normalized_score,
                    coverage_percentage=coverage,
                    observations_count=len(inherited) + len(pending_observations),
                    verified_count=len(inherited),
                    unresolved_count=len(pending_observations),
                    broken_links_count=0,
                    assessor="PE-06B controlled pilot",
                    calculation_details={
                        "formula": "raw / evaluated maximum * 100",
                        "inherited_assessment_id": str(previous.id),
                        "evaluated_dimensions": [item.dimension for item in inherited],
                        "pending_dimensions": list(DIMENSIONS),
                        "limitation": (
                            "Las cinco dimensiones PE-06B tienen observaciones documentales, "
                            "pero OED-TD-1.0 no define sus escalas de puntuación."
                        ),
                    },
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
                    observation = db.get(TransparencyObservation, original.observation_id)
                    if observation is None:
                        raise ValueError("PE-05 component lost its original observation")
                    item = AssessmentComponent(
                        id=uuid.uuid4(),
                        assessment_id=assessment.id,
                        requirement_id=original.requirement_id,
                        dimension=original.dimension,
                        weight=original.weight,
                        score=original.score,
                        maximum_score=original.maximum_score,
                        is_applicable=original.is_applicable,
                        rationale=original.rationale,
                        observation_ids=[str(observation.id)],
                        verification_status=original.verification_status,
                        observation_id=observation.id,
                        evidence_id=original.evidence_id,
                        methodology_version=VERSION,
                        calculation_reason=(
                            f"Heredado sin alteración de PE-05 {previous.id}; conserva "
                            "observación y evidencia originales."
                        ),
                    )
                    db.add(item)
                    _own(db, "component", item.id)
                    result.created += 1
            else:
                result.unchanged += 1 + len(inherited)
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
            select(TransparencyAssessment).where(
                TransparencyAssessment.assessment_date == date(2026, 8, 4),
                TransparencyAssessment.assessor == "PE-06B controlled pilot",
            )
        )
    )
    for assessment in assessments:
        components = list(
            db.scalars(
                select(AssessmentComponent).where(
                    AssessmentComponent.assessment_id == assessment.id
                )
            )
        )
        score = calculate(
            [ComponentInput(item.dimension, item.score, item.is_applicable) for item in components]
        )
        coverage = sum((item.maximum_score for item in components if item.is_applicable), Decimal())
        if (
            assessment.score,
            assessment.maximum_score,
            assessment.normalized_score,
            assessment.coverage_percentage,
        ) != (score.raw_score, score.maximum_score, score.normalized_score, coverage):
            raise ValueError("PE-06B historical assessment differs from its immutable components")
        result.unchanged += 1
    if len(assessments) != 5:
        raise ValueError("PE-06B requires five loaded assessments")
    db.rollback() if dry_run else db.commit()
    return result


def audit_report(db: Session) -> list[dict[str, object]]:
    rows = db.execute(
        select(Institution.name, TransparencyAssessment)
        .join(TransparencyAssessment, TransparencyAssessment.institution_id == Institution.id)
        .where(TransparencyAssessment.assessor == "PE-06B controlled pilot")
        .order_by(Institution.name)
    ).all()
    report: list[dict[str, object]] = []
    for name, item in rows:
        observations = db.execute(
            select(DocumentRequirement, TransparencyObservation, Evidence)
            .join(
                TransparencyObservation,
                TransparencyObservation.requirement_id == DocumentRequirement.id,
            )
            .join(Evidence, Evidence.id == TransparencyObservation.evidence_id)
            .where(
                TransparencyObservation.institution_id == item.institution_id,
                TransparencyObservation.observed_at
                == datetime.fromisoformat("2026-08-04T12:00:00-04:00"),
                DocumentRequirement.code.in_(DIMENSIONS),
            )
            .order_by(DocumentRequirement.code)
        ).all()
        report.append(
            {
                "institution": name,
                "score": str(item.score),
                "normalized_score": str(item.normalized_score),
                "coverage": str(item.coverage_percentage),
                "maturity": item.maturity_status,
                "component_count": 3,
                "inherited_dimensions": [
                    "institutional_identity",
                    "current_authorities",
                    "appointment_acts",
                ],
                "pending_dimensions": list(DIMENSIONS),
                "pending_reason": "OED-TD-1.0 no define escalas para estas dimensiones.",
                "new_dimension_audit": [
                    {
                        "dimension": requirement.code,
                        "requirement": requirement.name,
                        "maximum_weight": str(requirement.weight),
                        "score": None,
                        "observation": observation.finding,
                        "evidence": {"title": evidence.title, "locator": evidence.locator},
                        "verification_status": observation.verification_status.value,
                        "calculation_reason": "pending_evaluation; no se creó componente.",
                        "known_limitation": observation.finding,
                        "oed_td_1_0_rule": (
                            "Peso definido sin escala de transformación; no asignar máximo ni cero."
                        ),
                    }
                    for requirement, observation, evidence in observations
                ],
                "rank": None,
                "comparison_position": None,
                "saip_requests": 0,
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
    models: dict[str, Any] = {
        "component": AssessmentComponent,
        "assessment": TransparencyAssessment,
        "manual_task": ManualResearchTask,
        "observation": TransparencyObservation,
        "resource_check": ResourceCheck,
        "searchability_check": SearchabilityCheck,
        "resource": DocumentResource,
        "evidence": Evidence,
        "source": Source,
    }
    for kind in (
        "component",
        "assessment",
        "manual_task",
        "observation",
        "resource_check",
        "searchability_check",
        "resource",
        "evidence",
        "source",
    ):
        ids = [record.record_id for record in records if record.record_type == kind]
        if ids:
            db.execute(delete(models[kind]).where(models[kind].id.in_(ids)))
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


def counts(db: Session) -> dict[str, int]:
    return {
        "resource_checks": db.scalar(select(func.count()).select_from(ResourceCheck)) or 0,
        "searchability_checks": db.scalar(select(func.count()).select_from(SearchabilityCheck))
        or 0,
    }
