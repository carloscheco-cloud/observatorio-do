# mypy: ignore-errors
# ruff: noqa: E501, E701, E702
from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.modules.appointments.models import (
    Appointment,
    AppointmentCapacity,
    AppointmentEvidence,
    AppointmentMechanism,
    AppointmentStatus,
)
from app.modules.evidence.models import Evidence
from app.modules.executive_authorities.models import ExecutiveAuthorityLoadRecord
from app.modules.institutions.models import Institution, InstitutionStatus
from app.modules.legal_basis.models import LegalBasis, LegalInstrumentType
from app.modules.persons.models import Person, PersonEvidence, PersonStatus
from app.modules.persons.service import normalize_name
from app.modules.positions.models import AccessMethod, Position, PositionEvidence, PositionStatus
from app.modules.sources.models import Source

MANIFEST_PATH = Path(__file__).with_name("manifest.json")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SENSITIVE = {"national_id_hash", "birth_date", "address", "phone", "email", "party"}


class InvalidManifest(ValueError):
    pass


@dataclass
class LoadSummary:
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    skipped: int = 0
    errors: int = 0


@dataclass
class RollbackSummary:
    removed: int = 0
    unchanged: int = 0
    skipped: int = 0
    errors: int = 0


def read_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    _expand_compact_manifest(data)
    validate_manifest(data)
    return data


def _expand_compact_manifest(data: dict[str, Any]) -> None:
    """Expand the human-auditable inventory into the seven required sections."""
    people = data["persons"]
    data["persons"] = [
        {"key": key, "official_name": name, "identity_key": normalize_name(name)}
        for key, name in people
    ]
    names = {item["key"]: item["official_name"] for item in data["persons"]}
    authorities = data.pop("authorities")
    act_details = data.pop("act_details")
    current_status = data.pop("current_status")
    data["positions"] = []
    data["appointments"] = []
    data["person_evidence"] = []
    data["position_evidence"] = []
    data["appointment_evidence"] = []
    for key, person, institution, title, kind, mechanism, start, act, source in authorities:
        position_key = f"position-{key}"
        position_source = "constitution"
        data["positions"].append(
            {
                "key": position_key,
                "institution": institution,
                "official_name": title,
                "slug": key,
                "position_type": kind,
                "level": "head_of_state" if kind == "president" else "cabinet",
                "access_method": "election" if kind != "minister" else "appointment",
                "legal_basis": f"PE04-CONSTITUTION-{kind.upper()}",
                "legal_article": "122-126" if kind != "minister" else "134-137",
                "legal_source": position_source,
            }
        )
        data["appointments"].append(
            {
                "key": key,
                "person": person,
                "position": position_key,
                "start_date": start,
                "start_date_basis": (
                    "inicio constitucional del mandato y juramentación"
                    if kind != "minister"
                    else (
                        "fecha de juramentación oficial; no se afirma la fecha de efectos "
                        "de un acto jurídico no localizado"
                        if not act_details[key].get("decree_number")
                        else (
                            f"fecha de efectos expresamente indicada en {act}"
                            if start != act_details[key].get("decree_date")
                            else f"fecha del {act}; la disposición no difiere sus efectos"
                        )
                    )
                ),
                "capacity": "substantive",
                "mechanism": mechanism,
                "status": "active",
                "legal_act": act_details[key].get("legal_act"),
                "decree_number": act_details[key].get("decree_number"),
                "decree_date": act_details[key].get("decree_date"),
                "legal_act_url": data["sources"][source]["url"]
                if act_details[key].get("decree_number")
                else None,
                "legal_act_locator": act_details[key].get("locator"),
                "notes": act_details[key].get("notes"),
            }
        )
        person_source = "mandate" if kind != "minister" else source
        data["person_evidence"].append(
            {
                "person": person,
                "source": person_source,
                "title": f"Identidad pública oficial de {names[person]}",
                "excerpt": f"{names[person]} figura oficialmente como {title}.",
                "locator": names[person],
                "relation": "supports_public_identity",
            }
        )
        data["position_evidence"].append(
            {
                "position": position_key,
                "source": position_source,
                "title": f"Fundamento del cargo {title}",
                "excerpt": f"La Constitución regula el cargo público de {title}.",
                "locator": "artículos 122-126" if kind != "minister" else "artículos 134-137",
                "relation": "supports_legal_existence",
            }
        )
        data["appointment_evidence"].append(
            {
                "appointment": key,
                "source": source,
                "title": f"{act}: {names[person]}",
                "excerpt": f"{act} sustenta a {names[person]} como {title}.",
                "locator": act_details[key]["appointment_locator"],
                "relation": "supports_appointment",
            }
        )
        current = current_status[key]
        data["appointment_evidence"].append(
            {
                "appointment": key,
                "source": current["source"],
                "title": f"Vigencia actual de {names[person]}",
                "excerpt": f"La fuente oficial identifica actualmente a {names[person]} como {title}.",
                "locator": current["locator"],
                "relation": "supports_current_status",
            }
        )


def validate_manifest(data: dict[str, Any]) -> None:
    required = {
        "version",
        "sources",
        "persons",
        "person_evidence",
        "positions",
        "position_evidence",
        "appointments",
        "appointment_evidence",
    }
    if missing := required - data.keys():
        raise InvalidManifest(f"missing manifest fields: {sorted(missing)}")
    for key, source in data["sources"].items():
        if (
            not source.get("url", "").startswith("https://")
            or not source.get("publisher")
            or not source.get("retrieved_at")
        ):
            raise InvalidManifest(f"incomplete official source: {key}")
    person_keys = {item["key"] for item in data["persons"]}
    if len(person_keys) != len(data["persons"]):
        raise InvalidManifest("person keys must be unique")
    for item in data["persons"]:
        if SENSITIVE & item.keys() or normalize_name(item["official_name"]) != item["identity_key"]:
            raise InvalidManifest(f"unsafe or non-conservative identity: {item['key']}")
    position_keys = {item["key"] for item in data["positions"]}
    slugs = [item["slug"] for item in data["positions"]]
    if len(slugs) != len(set(slugs)) or any(not SLUG.fullmatch(slug) for slug in slugs):
        raise InvalidManifest("position slugs must be valid and unique")
    appointment_keys = {item["key"] for item in data["appointments"]}
    for item in data["appointments"]:
        if item["person"] not in person_keys or item["position"] not in position_keys:
            raise InvalidManifest("appointment references an unknown person or position")
        start = date.fromisoformat(item["start_date"]) if item.get("start_date") else None
        end = date.fromisoformat(item["end_date"]) if item.get("end_date") else None
        if start is None and not item.get("start_date_note"):
            raise InvalidManifest("unknown start_date requires an explanation")
        if start and end and end < start:
            raise InvalidManifest("appointment end_date precedes start_date")
        number = item.get("decree_number")
        if number and not all(
            item.get(field) for field in ("decree_date", "legal_act_url", "legal_act_locator")
        ):
            raise InvalidManifest("decree number requires official act traceability")
        if number and item.get("mechanism") != "presidential_decree":
            raise InvalidManifest("decree number requires presidential_decree mechanism")
    for section, keys, field in (
        ("person_evidence", person_keys, "person"),
        ("position_evidence", position_keys, "position"),
        ("appointment_evidence", appointment_keys, "appointment"),
    ):
        covered = {item[field] for item in data[section]}
        if covered != keys:
            raise InvalidManifest(f"{section} must cover every record")
        for item in data[section]:
            if item["source"] not in data["sources"] or not all(
                item.get(k) for k in ("title", "excerpt", "locator", "relation")
            ):
                raise InvalidManifest(f"incomplete evidence in {section}")
    for key in appointment_keys:
        relations = {
            item["relation"] for item in data["appointment_evidence"] if item["appointment"] == key
        }
        if relations != {"supports_appointment", "supports_current_status"}:
            raise InvalidManifest("appointment and current-status evidence must be separate")


def _hash(source: Source, spec: dict[str, Any]) -> str:
    return hashlib.sha256(
        f"{source.url}\n{spec['title']}\n{spec['excerpt']}\n{spec['locator']}".encode()
    ).hexdigest()


def _track(db: Session, version: str, kind: str, identifier: uuid.UUID) -> None:
    db.add(
        ExecutiveAuthorityLoadRecord(
            manifest_version=version, record_type=kind, record_id=identifier
        )
    )


def _evidence(db: Session, version: str, source: Source, spec: dict[str, Any]) -> Evidence:
    digest = _hash(source, spec)
    item = db.scalar(select(Evidence).where(Evidence.content_hash == digest))
    if item is None:
        item = Evidence(
            source_id=source.id,
            title=spec["title"],
            excerpt=spec["excerpt"],
            locator=spec["locator"],
            content_hash=digest,
            metadata_={"manifest_version": version, "pe04": True},
            observed_at=source.retrieved_at,
        )
        db.add(item)
        db.flush()
        _track(db, version, "evidence", item.id)
    return item


def load_authorities(
    db: Session, *, dry_run: bool = False, path: Path = MANIFEST_PATH
) -> LoadSummary:
    data = read_manifest(path)
    result = LoadSummary()
    version = data["version"]
    try:
        sources: dict[str, Source] = {}
        for key, spec in data["sources"].items():
            item = db.scalar(select(Source).where(Source.url == spec["url"]))
            if item is None:
                item = Source(
                    name=spec["name"],
                    url=spec["url"],
                    publisher=spec["publisher"],
                    is_official=True,
                    retrieved_at=datetime.fromisoformat(spec["retrieved_at"]),
                )
                db.add(item)
                db.flush()
                _track(db, version, "source", item.id)
            elif not item.is_official:
                raise InvalidManifest(f"non-official canonical source: {key}")
            sources[key] = item
        evidence: dict[tuple[str, str, str], Evidence] = {}
        for section, field in (
            ("person_evidence", "person"),
            ("position_evidence", "position"),
            ("appointment_evidence", "appointment"),
        ):
            for spec in data[section]:
                evidence[(section, spec[field], spec["relation"])] = _evidence(
                    db, version, sources[spec["source"]], spec
                )
        persons: dict[str, Person] = {}
        for spec in data["persons"]:
            item = db.scalar(select(Person).where(Person.normalized_name == spec["identity_key"]))
            if item and (
                item.full_name != spec["official_name"] or item.status != PersonStatus.CONFIRMED
            ):
                raise InvalidManifest(f"CONFIRMED person divergence: {spec['key']}")
            if item is None:
                item = Person(
                    full_name=spec["official_name"],
                    normalized_name=spec["identity_key"],
                    status=PersonStatus.CONFIRMED,
                    metadata_={"pe04_identity_policy": "exact_normalized_official_name"},
                )
                db.add(item)
                db.flush()
                _track(db, version, "person", item.id)
                result.created += 1
            else:
                result.unchanged += 1
            ev = evidence[("person_evidence", spec["key"], "supports_public_identity")]
            if (
                db.scalar(
                    select(PersonEvidence).where(
                        PersonEvidence.person_id == item.id, PersonEvidence.evidence_id == ev.id
                    )
                )
                is None
            ):
                link = PersonEvidence(
                    person_id=item.id, evidence_id=ev.id, relation="supports_public_identity"
                )
                db.add(link)
                db.flush()
                _track(db, version, "person_evidence", link.id)
            persons[spec["key"]] = item
        institutions = {
            item.slug: item
            for item in db.scalars(
                select(Institution).where(Institution.status == InstitutionStatus.CONFIRMED)
            )
        }
        positions: dict[str, Position] = {}
        for spec in data["positions"]:
            institution = institutions.get(spec["institution"])
            if institution is None:
                raise InvalidManifest(f"missing PE-02 institution: {spec['institution']}")
            ev = evidence[("position_evidence", spec["key"], "supports_legal_existence")]
            basis_ref = spec["legal_basis"]
            basis = db.scalar(select(LegalBasis).where(LegalBasis.reference == basis_ref))
            if basis is None:
                basis = LegalBasis(
                    instrument_type=LegalInstrumentType.CONSTITUTION,
                    title="Constitución de la República Dominicana",
                    reference=basis_ref,
                    article=spec["legal_article"],
                    official_url=sources[spec["legal_source"]].url,
                    evidence_id=ev.id,
                    issuing_body="Asamblea Nacional Revisora",
                    description="Base constitucional del cargo.",
                )
                db.add(basis)
                db.flush()
                _track(db, version, "legal_basis", basis.id)
            item = db.scalar(select(Position).where(Position.code == spec["slug"]))
            values = dict(
                institution_id=institution.id,
                official_name=spec["official_name"],
                position_type=spec["position_type"],
                hierarchy_level=spec["level"],
                access_method=AccessMethod(spec["access_method"]),
                legal_basis_id=basis.id,
                status=PositionStatus.CANONICAL,
                single_occupant=True,
            )
            if item and any(getattr(item, key) != value for key, value in values.items()):
                raise InvalidManifest(f"canonical position divergence: {spec['key']}")
            if item is None:
                item = Position(code=spec["slug"], **values)
                db.add(item)
                db.flush()
                _track(db, version, "position", item.id)
                result.created += 1
            else:
                result.unchanged += 1
            if (
                db.scalar(
                    select(PositionEvidence).where(
                        PositionEvidence.position_id == item.id,
                        PositionEvidence.evidence_id == ev.id,
                    )
                )
                is None
            ):
                link = PositionEvidence(
                    position_id=item.id, evidence_id=ev.id, relation="supports_legal_existence"
                )
                db.add(link)
                db.flush()
                _track(db, version, "position_evidence", link.id)
            positions[spec["key"]] = item
        for spec in data["appointments"]:
            person, position = persons[spec["person"]], positions[spec["position"]]
            item = db.scalar(
                select(Appointment).where(
                    Appointment.person_id == person.id,
                    Appointment.position_id == position.id,
                    Appointment.start_date
                    == (date.fromisoformat(spec["start_date"]) if spec.get("start_date") else None),
                )
            )
            ev = evidence[("appointment_evidence", spec["key"], "supports_appointment")]
            values = dict(
                institution_id=position.institution_id,
                start_date=date.fromisoformat(spec["start_date"])
                if spec.get("start_date")
                else None,
                end_date=date.fromisoformat(spec["end_date"]) if spec.get("end_date") else None,
                appointment_type=spec["capacity"],
                capacity=AppointmentCapacity(spec["capacity"]),
                mechanism=AppointmentMechanism(spec["mechanism"]),
                status=AppointmentStatus(spec["status"]),
                evidence_id=ev.id,
                source_id=ev.source_id,
                legal_act=spec.get("legal_act"),
                decree_number=spec.get("decree_number"),
                decree_date=date.fromisoformat(spec["decree_date"])
                if spec.get("decree_date")
                else None,
                legal_act_url=spec.get("legal_act_url"),
                legal_act_locator=spec.get("legal_act_locator"),
                start_date_basis=spec["start_date_basis"],
                notes=spec.get("notes"),
                metadata_={
                    "start_date_basis": spec["start_date_basis"],
                    "historical_closure_policy": "never infer end date from a later appointment",
                },
            )
            if item and any(getattr(item, key) != value for key, value in values.items()):
                raise InvalidManifest(f"CONFIRMED appointment divergence: {spec['key']}")
            if item is None:
                item = Appointment(
                    person_id=person.id,
                    position_id=position.id,
                    **values,
                )
                db.add(item)
                db.flush()
                _track(db, version, "appointment", item.id)
                result.created += 1
            else:
                result.unchanged += 1
            evidence_specs = [
                evidence_spec
                for evidence_spec in data["appointment_evidence"]
                if evidence_spec["appointment"] == spec["key"]
            ]
            for evidence_spec in evidence_specs:
                linked_evidence = evidence[
                    ("appointment_evidence", spec["key"], evidence_spec["relation"])
                ]
                if (
                    db.scalar(
                        select(AppointmentEvidence).where(
                            AppointmentEvidence.appointment_id == item.id,
                            AppointmentEvidence.evidence_id == linked_evidence.id,
                        )
                    )
                    is None
                ):
                    link = AppointmentEvidence(
                        appointment_id=item.id,
                        evidence_id=linked_evidence.id,
                        relation=evidence_spec["relation"],
                    )
                    db.add(link)
                    db.flush()
                    _track(db, version, "appointment_evidence", link.id)
        db.rollback() if dry_run else db.commit()
    except Exception:
        db.rollback()
        result.errors += 1
        raise
    return result


def rollback_authorities(
    db: Session, *, dry_run: bool = False, version: str | None = None
) -> RollbackSummary:
    version = version or read_manifest()["version"]
    result = RollbackSummary()
    order = (
        "appointment_evidence",
        "appointment",
        "position_evidence",
        "position",
        "person_evidence",
        "person",
        "legal_basis",
        "evidence",
        "source",
    )
    models: dict[str, type[Any]] = {
        "appointment_evidence": AppointmentEvidence,
        "appointment": Appointment,
        "position_evidence": PositionEvidence,
        "position": Position,
        "person_evidence": PersonEvidence,
        "person": Person,
        "legal_basis": LegalBasis,
        "evidence": Evidence,
        "source": Source,
    }
    try:
        for kind in order:
            records = list(
                db.scalars(
                    select(ExecutiveAuthorityLoadRecord).where(
                        ExecutiveAuthorityLoadRecord.manifest_version == version,
                        ExecutiveAuthorityLoadRecord.record_type == kind,
                    )
                )
            )
            for record in records:
                item = db.get(models[kind], record.record_id)
                if item is not None:
                    db.delete(item)
                    result.removed += 1
                else:
                    result.unchanged += 1
                db.delete(record)
            db.flush()
        db.execute(
            delete(ExecutiveAuthorityLoadRecord).where(
                ExecutiveAuthorityLoadRecord.manifest_version == version
            )
        )
        db.rollback() if dry_run else db.commit()
    except Exception:
        db.rollback()
        result.errors += 1
        raise
    return result


def summary_dict(summary: LoadSummary | RollbackSummary) -> dict[str, int]:
    return asdict(summary)
