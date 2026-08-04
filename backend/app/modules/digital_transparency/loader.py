# ruff: noqa: E501
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.modules.appointments.models import Appointment, AppointmentEvidence, AppointmentStatus
from app.modules.digital_transparency.methodology import (
    VERSION,
    WEIGHTS,
    ComponentInput,
    appointment_act_score,
    calculate,
    classification,
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
    ResearchTaskStatus,
    ReviewerType,
    TransparencyAssessment,
    TransparencyObservation,
    VerificationStatus,
)
from app.modules.evidence.models import Evidence
from app.modules.institutions.models import Institution, InstitutionEvidence
from app.modules.persons.models import Person
from app.modules.positions.models import Position
from app.modules.sources.models import Source

MANIFEST_PATH = Path(__file__).with_name("manifest.json")


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
    if data.get("methodology_version") != VERSION or date.fromisoformat(
        data["assessment_date"]
    ) > date.fromisoformat(data["observed_at"][:10]):
        raise ValueError("invalid or incoherent PE-05 manifest")
    return data


def _own(db: Session, version: str, kind: str, identifier: uuid.UUID) -> None:
    db.add(
        DigitalTransparencyLoadRecord(
            manifest_version=version, record_type=kind, record_id=identifier
        )
    )


def _requirements(
    db: Session, data: dict[str, Any], result: Summary
) -> dict[str, DocumentRequirement]:
    names = {
        "institutional_identity": "Identidad institucional y sitio oficial",
        "legal_framework": "Marco legal localizable",
        "organizational_structure": "Estructura y organigrama",
        "current_authorities": "Autoridades actuales",
        "appointment_acts": "Actos de designación",
        "official_contact_information": "Información de contacto y OAI",
        "document_searchability": "Calidad técnica y buscabilidad",
        "stable_links": "Permanencia de enlaces y metadatos",
    }
    found: dict[str, DocumentRequirement] = {}
    for code, weight in WEIGHTS.items():
        item = db.scalar(
            select(DocumentRequirement).where(
                DocumentRequirement.code == code, DocumentRequirement.methodology_version == VERSION
            )
        )
        if item is None:
            item = DocumentRequirement(
                id=uuid.uuid4(),
                code=code,
                name=names[code],
                description=f"Dimensión reproducible {code} de {VERSION}.",
                scope="institution",
                applicable_institution_types=["presidency", "vice_presidency", "ministry"],
                weight=weight,
                required_by_law=False,
                active_from=date.fromisoformat(data["assessment_date"]),
                methodology_version=VERSION,
            )
            db.add(item)
            _own(db, data["version"], "requirement", item.id)
            result.created += 1
        else:
            if (
                item.weight != weight
                or item.name != names[code]
                or item.active_from != date.fromisoformat(data["assessment_date"])
            ):
                raise ValueError(f"{VERSION} is immutable; create a later methodology version")
            result.unchanged += 1
        found[code] = item
    db.flush()
    return found


def _resource(
    db: Session,
    institution: Institution,
    requirement: DocumentRequirement,
    evidence: Evidence,
    source: Source,
    result: Summary,
    version: str,
) -> DocumentResource:
    resource_types = {
        "institutional_identity": "institutional_page",
        "current_authorities": "authority_page",
        "appointment_acts": "legal_document",
    }
    item = db.scalar(
        select(DocumentResource).where(
            DocumentResource.institution_id == institution.id,
            DocumentResource.requirement_id == requirement.id,
            DocumentResource.canonical_url == source.url,
        )
    )
    if item is not None:
        result.unchanged += 1
        return item
    item = DocumentResource(
        id=uuid.uuid4(),
        institution_id=institution.id,
        requirement_id=requirement.id,
        title=evidence.title,
        resource_type=resource_types[requirement.code],
        canonical_url=source.url,
        source_id=source.id,
        retrieved_at=source.retrieved_at,
        checksum=None,
        notes="Recurso reutilizado de evidencia oficial PE-02/PE-04; PE-05 no realizó una nueva comprobación HTTP.",
    )
    db.add(item)
    _own(db, version, "resource", item.id)
    result.created += 1
    db.flush()
    return item


def _observation(
    db: Session,
    institution: Institution,
    requirement: DocumentRequirement,
    evidence: Evidence,
    resource: DocumentResource | None,
    status: VerificationStatus,
    finding: str,
    data: dict[str, Any],
    result: Summary,
) -> TransparencyObservation:
    observed_at = datetime.fromisoformat(data["observed_at"])
    item = db.scalar(
        select(TransparencyObservation).where(
            TransparencyObservation.institution_id == institution.id,
            TransparencyObservation.requirement_id == requirement.id,
            TransparencyObservation.evidence_id == evidence.id,
            TransparencyObservation.observed_at == observed_at,
            TransparencyObservation.verification_status == status,
        )
    )
    if item is not None:
        result.unchanged += 1
        return item
    item = TransparencyObservation(
        id=uuid.uuid4(),
        institution_id=institution.id,
        requirement_id=requirement.id,
        resource_id=resource.id if resource else None,
        verification_status=status,
        observed_at=observed_at,
        reviewer_type=ReviewerType.HUMAN,
        search_scope="Fuentes oficiales ya registradas y consultadas por PE-02 y PE-04 al 3 de agosto de 2026; no implica búsqueda exhaustiva de Internet.",
        finding=finding,
        confidence=ConfidenceLevel.HIGH
        if status == VerificationStatus.VERIFIED_DIGITALLY
        else ConfidenceLevel.MEDIUM,
        evidence_id=evidence.id,
        methodology_version=VERSION,
        notes="No afirma inexistencia jurídica ni incumplimiento.",
    )
    db.add(item)
    _own(db, data["version"], "observation", item.id)
    result.created += 1
    db.flush()
    return item


def load(db: Session, *, dry_run: bool = False, path: Path = MANIFEST_PATH) -> Summary:
    data = read_manifest(path)
    result = Summary()
    try:
        requirements = _requirements(db, data, result)
        institutions = list(
            db.scalars(
                select(Institution)
                .where(
                    Institution.slug.is_not(None),
                    Institution.institution_type.in_(["PRESIDENCY", "VICE_PRESIDENCY", "MINISTRY"]),
                )
                .order_by(Institution.slug)
            )
        )
        if len(institutions) != 25:
            raise ValueError("PE-05 requires the 25 PE-02 institutions")
        pending = set(data["pending_appointment_people"])
        for institution in institutions:
            observations: list[TransparencyObservation] = []
            link = db.scalar(
                select(InstitutionEvidence)
                .where(InstitutionEvidence.institution_id == institution.id)
                .limit(1)
            )
            if link is None:
                raise ValueError(f"institution lacks PE-02 evidence: {institution.slug}")
            evidence = db.get(Evidence, link.evidence_id)
            source = db.get(Source, evidence.source_id) if evidence else None
            if evidence is None or source is None or not source.is_official:
                raise ValueError(f"institution evidence is not official: {institution.slug}")
            identity_resource = _resource(
                db,
                institution,
                requirements["institutional_identity"],
                evidence,
                source,
                result,
                data["version"],
            )
            observations.append(
                _observation(
                    db,
                    institution,
                    requirements["institutional_identity"],
                    evidence,
                    identity_resource,
                    VerificationStatus.VERIFIED_DIGITALLY,
                    "La identidad institucional y un recurso oficial están documentados en la evidencia PE-02.",
                    data,
                    result,
                )
            )
            appointment = db.scalar(
                select(Appointment)
                .join(Position, Appointment.position_id == Position.id)
                .where(
                    Appointment.institution_id == institution.id,
                    Appointment.status == AppointmentStatus.ACTIVE,
                )
            )
            if appointment is None:
                raise ValueError(f"institution lacks active PE-04 appointment: {institution.slug}")
            current_link = db.scalar(
                select(AppointmentEvidence).where(
                    AppointmentEvidence.appointment_id == appointment.id,
                    AppointmentEvidence.relation == "supports_current_status",
                )
            )
            act_link = db.scalar(
                select(AppointmentEvidence).where(
                    AppointmentEvidence.appointment_id == appointment.id,
                    AppointmentEvidence.relation == "supports_appointment",
                )
            )
            if current_link is None or act_link is None:
                raise ValueError(f"appointment lacks separated evidence: {institution.slug}")
            current_evidence = db.get(Evidence, current_link.evidence_id)
            act_evidence = db.get(Evidence, act_link.evidence_id)
            if current_evidence is None or act_evidence is None:
                raise ValueError("missing appointment evidence")
            current_source = db.get(Source, current_evidence.source_id)
            act_source = db.get(Source, act_evidence.source_id)
            if current_source is None or act_source is None:
                raise ValueError("missing official source")
            current_resource = _resource(
                db,
                institution,
                requirements["current_authorities"],
                current_evidence,
                current_source,
                result,
                data["version"],
            )
            observations.append(
                _observation(
                    db,
                    institution,
                    requirements["current_authorities"],
                    current_evidence,
                    current_resource,
                    VerificationStatus.VERIFIED_DIGITALLY,
                    "La autoridad vigente está identificada por evidencia oficial PE-04.",
                    data,
                    result,
                )
            )
            person = db.get(Person, appointment.person_id)
            missing_act = person is not None and person.full_name in pending
            act_resource = (
                None
                if missing_act
                else _resource(
                    db,
                    institution,
                    requirements["appointment_acts"],
                    act_evidence,
                    act_source,
                    result,
                    data["version"],
                )
            )
            status = (
                VerificationStatus.NOT_LOCATED_IN_REVIEWED_SOURCES
                if missing_act
                else VerificationStatus.VERIFIED_DIGITALLY
            )
            finding = (
                "No fue localizado en las fuentes oficiales digitales revisadas hasta la fecha "
                "de evaluación. La evidencia sí acredita el nombramiento y la vigencia."
                if missing_act
                else "El acto de designación está localizado en la evidencia oficial PE-04. Sus propiedades técnicas no fueron comprobadas nuevamente por PE-05."
            )
            observations.append(
                _observation(
                    db,
                    institution,
                    requirements["appointment_acts"],
                    act_evidence,
                    act_resource,
                    status,
                    finding,
                    data,
                    result,
                )
            )
            if missing_act:
                assert person is not None
                task = db.scalar(
                    select(ManualResearchTask).where(
                        ManualResearchTask.institution_id == institution.id,
                        ManualResearchTask.related_entity_type == "appointment",
                        ManualResearchTask.related_entity_id == appointment.id,
                        ManualResearchTask.document_type == "individual_appointment_act",
                    )
                )
                if task is None:
                    task = ManualResearchTask(
                        id=uuid.uuid4(),
                        institution_id=institution.id,
                        related_entity_type="appointment",
                        related_entity_id=appointment.id,
                        document_type="individual_appointment_act",
                        description=(
                            f"Localizar manualmente el acto individual de designación de "
                            f"{person.full_name}; no se presume que el acto no exista. Prioridad "
                            "normal porque la designación y vigencia ya tienen evidencia oficial."
                        ),
                        priority="normal",
                        status=ResearchTaskStatus.OPEN,
                        searched_sources=[
                            {
                                "source_id": str(act_source.id),
                                "url": act_source.url,
                                "reviewed_at": data["observed_at"],
                            }
                        ],
                        result_summary="No fue localizado dentro del alcance documentado por PE-04.",
                    )
                    db.add(task)
                    _own(db, data["version"], "manual_task", task.id)
                    result.created += 1
                else:
                    result.unchanged += 1
            component_values = [
                ("institutional_identity", Decimal("10"), observations[0]),
                ("current_authorities", Decimal("15"), observations[1]),
                (
                    "appointment_acts",
                    appointment_act_score(act_located=not missing_act, appointment_verified=True),
                    observations[2],
                ),
            ]
            score = calculate([ComponentInput(code, value) for code, value, _ in component_values])
            coverage = sum((WEIGHTS[code] for code, _, _ in component_values), Decimal("0"))
            assessment = db.scalar(
                select(TransparencyAssessment).where(
                    TransparencyAssessment.institution_id == institution.id,
                    TransparencyAssessment.methodology_version == VERSION,
                    TransparencyAssessment.assessment_date
                    == date.fromisoformat(data["assessment_date"]),
                )
            )
            if assessment is None:
                assessment = TransparencyAssessment(
                    id=uuid.uuid4(),
                    institution_id=institution.id,
                    methodology_version=VERSION,
                    assessment_date=date.fromisoformat(data["assessment_date"]),
                    score=score.raw_score,
                    maximum_score=score.maximum_score,
                    normalized_score=score.normalized_score,
                    coverage_percentage=coverage,
                    observations_count=3,
                    verified_count=2 if missing_act else 3,
                    unresolved_count=1 if missing_act else 0,
                    broken_links_count=0,
                    assessor="PE-05 controlled loader",
                    calculation_details={
                        "formula": "raw / applicable evaluated maximum * 100",
                        "score_band_internal": classification(score.normalized_score),
                        "evaluated_weight": 45,
                        "methodology_total": 100,
                        "limitation": "Partial assessment from PE-02/PE-04 evidence; five dimensions remain not evaluated.",
                    },
                    status="partial",
                    maturity_status=maturity(coverage),
                    classification_public=public_classification(score.normalized_score, coverage),
                    rank=None,
                    comparison_position=None,
                )
                db.add(assessment)
                _own(db, data["version"], "assessment", assessment.id)
                result.created += 1
                db.flush()
                for code, value, observation in component_values:
                    component = AssessmentComponent(
                        id=uuid.uuid4(),
                        assessment_id=assessment.id,
                        requirement_id=requirements[code].id,
                        dimension=code,
                        weight=WEIGHTS[code],
                        score=value,
                        maximum_score=WEIGHTS[code],
                        is_applicable=True,
                        rationale=observation.finding,
                        observation_ids=[str(observation.id)],
                        verification_status=observation.verification_status,
                        observation_id=observation.id,
                        evidence_id=observation.evidence_id,
                        methodology_version=VERSION,
                        calculation_reason=observation.finding,
                    )
                    db.add(component)
                    _own(db, data["version"], "component", component.id)
                    result.created += 1
            else:
                result.unchanged += 4
        db.flush()
        db.rollback() if dry_run else db.commit()
        return result
    except Exception:
        db.rollback()
        raise


def recalculate(db: Session, *, dry_run: bool = False) -> Summary:
    result = Summary()
    for assessment in db.scalars(
        select(TransparencyAssessment).where(TransparencyAssessment.methodology_version == VERSION)
    ):
        components = list(
            db.scalars(
                select(AssessmentComponent).where(
                    AssessmentComponent.assessment_id == assessment.id
                )
            )
        )
        inputs: list[ComponentInput] = []
        for component in components:
            requirement = db.get(DocumentRequirement, component.requirement_id)
            if requirement is None:
                raise ValueError("assessment component lacks requirement")
            inputs.append(
                ComponentInput(requirement.code, component.score, component.is_applicable)
            )
        score = calculate(inputs)
        if (
            assessment.score == score.raw_score
            and assessment.maximum_score == score.maximum_score
            and assessment.normalized_score == score.normalized_score
        ):
            result.unchanged += 1
        else:
            if assessment.status == "published":
                raise ValueError(
                    "published assessments are immutable; create a historical assessment"
                )
            assessment.score = score.raw_score
            assessment.maximum_score = score.maximum_score
            assessment.normalized_score = score.normalized_score
            assessment.coverage_percentage = score.maximum_score
            assessment.maturity_status = maturity(score.maximum_score)
            assessment.classification_public = public_classification(
                score.normalized_score, score.maximum_score
            )
            assessment.rank = None
            assessment.comparison_position = None
            result.created += 1
    db.rollback() if dry_run else db.commit()
    return result


def create_historical_assessment(
    db: Session,
    previous_assessment_id: uuid.UUID,
    assessment_date: date,
    replacements: dict[str, tuple[Decimal, TransparencyObservation]],
) -> TransparencyAssessment:
    """Create, never overwrite, an assessment snapshot from persisted components."""
    previous = db.get(TransparencyAssessment, previous_assessment_id)
    if previous is None:
        raise ValueError("previous assessment not found")
    if assessment_date <= previous.assessment_date:
        raise ValueError("historical assessment date must advance")
    existing = db.scalar(
        select(TransparencyAssessment).where(
            TransparencyAssessment.institution_id == previous.institution_id,
            TransparencyAssessment.methodology_version == previous.methodology_version,
            TransparencyAssessment.assessment_date == assessment_date,
        )
    )
    if existing is not None:
        return existing
    old_components = list(
        db.scalars(
            select(AssessmentComponent).where(AssessmentComponent.assessment_id == previous.id)
        )
    )
    values: list[tuple[AssessmentComponent, Decimal, TransparencyObservation]] = []
    for component in old_components:
        replacement = replacements.get(component.dimension)
        observation = (
            replacement[1]
            if replacement
            else db.get(TransparencyObservation, component.observation_id)
        )
        if observation is None:
            raise ValueError("component observation not found")
        values.append((component, replacement[0] if replacement else component.score, observation))
    score = calculate(
        [ComponentInput(item.dimension, value, item.is_applicable) for item, value, _ in values]
    )
    snapshot = TransparencyAssessment(
        id=uuid.uuid4(),
        institution_id=previous.institution_id,
        methodology_version=previous.methodology_version,
        assessment_date=assessment_date,
        score=score.raw_score,
        maximum_score=score.maximum_score,
        normalized_score=score.normalized_score,
        coverage_percentage=score.maximum_score,
        observations_count=len(values),
        verified_count=sum(
            observation.verification_status == VerificationStatus.VERIFIED_DIGITALLY
            for _, _, observation in values
        ),
        unresolved_count=sum(
            observation.verification_status == VerificationStatus.NOT_LOCATED_IN_REVIEWED_SOURCES
            for _, _, observation in values
        ),
        broken_links_count=sum(
            observation.verification_status == VerificationStatus.BROKEN_LINK
            for _, _, observation in values
        ),
        assessor="historical recalculation",
        calculation_details={
            "formula": "raw / applicable evaluated maximum * 100",
            "derived_from_assessment_id": str(previous.id),
            "score_band_internal": classification(score.normalized_score),
        },
        status=maturity(score.maximum_score),
        maturity_status=maturity(score.maximum_score),
        classification_public=public_classification(score.normalized_score, score.maximum_score),
        rank=None,
        comparison_position=None,
    )
    db.add(snapshot)
    db.flush()
    for old, value, observation in values:
        db.add(
            AssessmentComponent(
                id=uuid.uuid4(),
                assessment_id=snapshot.id,
                requirement_id=old.requirement_id,
                dimension=old.dimension,
                weight=old.weight,
                score=value,
                maximum_score=old.maximum_score,
                is_applicable=old.is_applicable,
                rationale=observation.finding,
                observation_ids=[str(observation.id)],
                verification_status=observation.verification_status,
                observation_id=observation.id,
                evidence_id=observation.evidence_id,
                methodology_version=snapshot.methodology_version,
                calculation_reason=observation.finding,
            )
        )
    db.commit()
    return snapshot


def audit_report(db: Session) -> list[dict[str, object]]:
    rows = db.execute(
        select(Institution.name, TransparencyAssessment)
        .join(TransparencyAssessment, TransparencyAssessment.institution_id == Institution.id)
        .where(TransparencyAssessment.methodology_version == VERSION)
        .order_by(Institution.name)
    ).all()
    report: list[dict[str, object]] = []
    all_dimensions = list(WEIGHTS)
    for name, item in rows:
        evaluated = list(
            db.scalars(
                select(AssessmentComponent.dimension)
                .where(AssessmentComponent.assessment_id == item.id)
                .order_by(AssessmentComponent.dimension)
            )
        )
        pending = [dimension for dimension in all_dimensions if dimension not in evaluated]
        warning = (
            f"Resultado normalizado sobre el {item.coverage_percentage}% del peso de "
            "dimensiones evaluadas. Esta evaluación es parcial y no debe interpretarse "
            "como una calificación integral ni utilizarse para ranking."
        )
        report.append(
            {
                "institution": name,
                "raw_score": str(item.score),
                "evaluated_maximum": str(item.maximum_score),
                "normalized_score": str(item.normalized_score),
                "coverage_percentage": str(item.coverage_percentage),
                "maturity_status": item.maturity_status,
                "classification_public": item.classification_public,
                "evaluated_dimensions": evaluated,
                "pending_dimensions": pending,
                "methodological_warning": warning,
                "verified_documents": item.verified_count,
                "pending_documents": item.unresolved_count,
                "broken_links": item.broken_links_count,
                "date": item.assessment_date.isoformat(),
                "methodology": item.methodology_version,
                "rank": None,
                "comparison_position": None,
            }
        )
    return report


def rollback(db: Session, *, dry_run: bool = False, path: Path = MANIFEST_PATH) -> Summary:
    data = read_manifest(path)
    result = Summary()
    records = list(
        db.scalars(
            select(DigitalTransparencyLoadRecord).where(
                DigitalTransparencyLoadRecord.manifest_version == data["version"]
            )
        )
    )
    model_by_type = {
        "component": AssessmentComponent,
        "assessment": TransparencyAssessment,
        "manual_task": ManualResearchTask,
        "observation": TransparencyObservation,
        "resource": DocumentResource,
        "requirement": DocumentRequirement,
    }
    for kind in (
        "component",
        "assessment",
        "manual_task",
        "observation",
        "resource",
        "requirement",
    ):
        ids = [record.record_id for record in records if record.record_type == kind]
        if ids:
            model: Any = model_by_type[kind]
            db.execute(delete(model).where(model.id.in_(ids)))
            result.removed += len(ids)
    db.execute(
        delete(DigitalTransparencyLoadRecord).where(
            DigitalTransparencyLoadRecord.manifest_version == data["version"]
        )
    )
    result.removed += len(records)
    db.rollback() if dry_run else db.commit()
    return result
