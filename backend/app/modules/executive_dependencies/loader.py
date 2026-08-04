from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import MetaData, Table, delete, func, inspect, select, update
from sqlalchemy.orm import Session

from app.modules.evidence.models import Evidence
from app.modules.executive_dependencies.models import ExecutiveDependencyLoadRecord
from app.modules.institutions.models import (
    CoverageLevel,
    Institution,
    InstitutionEvidence,
    InstitutionRelationship,
    InstitutionRelationshipType,
    InstitutionStatus,
    InstitutionType,
    OperationalStatus,
    StateBranch,
)
from app.modules.sources.models import Source
from app.modules.territories.models import Territory

MANIFEST_PATH = Path(__file__).with_name("manifest.json")
STRUCTURAL_RELATIONSHIPS = {
    InstitutionRelationshipType.ATTACHED,
    InstitutionRelationshipType.DEPENDENT_ON,
    InstitutionRelationshipType.HIERARCHICAL,
}


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
    validate_manifest(data)
    return data


def _relationship_key(item: dict[str, Any]) -> tuple[str, str, str]:
    return item["parent"], item["child"], item["relationship_type"]


def validate_manifest(data: dict[str, Any]) -> None:
    required = {
        "version",
        "territory_code",
        "sources",
        "institutions",
        "institution_evidence",
        "relationships",
        "relationship_evidence",
    }
    if missing := required - data.keys():
        raise InvalidManifest(f"missing manifest fields: {sorted(missing)}")
    sources = data["sources"]
    for key, source in sources.items():
        if not all(
            source.get(field)
            for field in ("name", "url", "publisher", "source_type", "retrieved_at")
        ):
            raise InvalidManifest(f"incomplete official source: {key}")
        if not source["url"].startswith("https://"):
            raise InvalidManifest(f"source must use HTTPS: {key}")
    slugs = [item.get("slug") for item in data["institutions"]]
    if None in slugs or len(slugs) != len(set(slugs)):
        raise InvalidManifest("institution slugs must be present and unique")
    allowed_types = {item.value for item in InstitutionType}
    for item in data["institutions"]:
        needed = {
            "name",
            "slug",
            "institution_type",
            "kind",
            "operational_status",
            "coverage_level",
        }
        if needed - item.keys():
            raise InvalidManifest(f"incomplete institution: {item.get('slug')}")
        if item["institution_type"] not in allowed_types:
            raise InvalidManifest(f"unknown institution type: {item['institution_type']}")
    institution_evidence = {item["institution"] for item in data["institution_evidence"]}
    if set(slugs) != institution_evidence:
        raise InvalidManifest("every institution requires individual evidence")
    for item in data["institution_evidence"] + data["relationship_evidence"]:
        if item.get("source") not in sources or not all(
            item.get(field) for field in ("title", "excerpt", "locator")
        ):
            raise InvalidManifest(
                "all evidence requires a known source, title, excerpt and locator"
            )
    keys: set[tuple[str, str, str]] = set()
    relation_types = {item.value for item in InstitutionRelationshipType}
    for item in data["relationships"]:
        key = _relationship_key(item)
        if item["parent"] == item["child"]:
            raise InvalidManifest("self relationships are forbidden")
        if item["child"] not in slugs:
            raise InvalidManifest("relationship child must be declared in institutions")
        if item["relationship_type"] not in relation_types:
            raise InvalidManifest("unknown relationship type")
        if key in keys:
            raise InvalidManifest("duplicate relationship")
        keys.add(key)
        valid_from = date.fromisoformat(item["valid_from"]) if item.get("valid_from") else None
        valid_to = date.fromisoformat(item["valid_to"]) if item.get("valid_to") else None
        if valid_to and valid_from and valid_to < valid_from:
            raise InvalidManifest("valid_to must not precede valid_from")
        if valid_from is None and not item.get("notes", "").strip():
            raise InvalidManifest("unknown valid_from requires an explicit note")
    evidence_keys = {_relationship_key(item) for item in data["relationship_evidence"]}
    if keys != evidence_keys:
        raise InvalidManifest("every relationship requires exactly one specific evidence entry")


def _hash(source: Source, title: str, excerpt: str, locator: str) -> str:
    value = f"{source.url}\n{title}\n{excerpt}\n{locator}"
    return hashlib.sha256(value.encode()).hexdigest()


def _track(db: Session, version: str, record_type: str, record_id: uuid.UUID) -> None:
    db.add(
        ExecutiveDependencyLoadRecord(
            manifest_version=version,
            record_type=record_type,
            record_id=record_id,
        )
    )


def _remove_record(db: Session, record: ExecutiveDependencyLoadRecord) -> None:
    db.delete(record)


def _has_other_institution_references(db: Session, institution_id: uuid.UUID) -> bool:
    bind = db.get_bind()
    metadata = MetaData()
    for table_name in inspect(bind).get_table_names():
        if table_name in {
            "institutions",
            "institution_evidence",
            "institution_relationships",
            "executive_dependency_load_records",
        }:
            continue
        foreign_keys = inspect(bind).get_foreign_keys(table_name)
        columns = [
            fk["constrained_columns"][0]
            for fk in foreign_keys
            if fk.get("referred_table") == "institutions"
            and len(fk.get("constrained_columns", [])) == 1
        ]
        if not columns:
            continue
        table = Table(table_name, metadata, autoload_with=bind)
        if any(
            db.scalar(
                select(func.count()).select_from(table).where(table.c[column] == institution_id)
            )
            for column in columns
        ):
            return True
    return False


def _would_cycle(db: Session, parent_id: object, child_id: object) -> bool:
    graph: dict[object, set[object]] = {}
    for relation in db.scalars(select(InstitutionRelationship)):
        if relation.relationship_type in STRUCTURAL_RELATIONSHIPS and relation.valid_to is None:
            graph.setdefault(relation.parent_institution_id, set()).add(
                relation.child_institution_id
            )
    graph.setdefault(parent_id, set()).add(child_id)
    pending = [child_id]
    seen: set[object] = set()
    while pending:
        node = pending.pop()
        if node == parent_id:
            return True
        if node not in seen:
            seen.add(node)
            pending.extend(graph.get(node, ()))
    return False


def load_dependencies(
    db: Session, *, dry_run: bool = False, path: Path = MANIFEST_PATH
) -> LoadSummary:
    data = read_manifest(path)
    result = LoadSummary()
    try:
        territory = db.scalar(select(Territory).where(Territory.code == data["territory_code"]))
        if territory is None:
            raise InvalidManifest("PE-02 territory is missing; load executive_inventory first")
        sources: dict[str, Source] = {}
        for key, spec in data["sources"].items():
            source = db.scalar(select(Source).where(Source.url == spec["url"]))
            if source is None:
                source = Source(
                    name=spec["name"],
                    url=spec["url"],
                    publisher=spec["publisher"],
                    is_official=True,
                    retrieved_at=datetime.fromisoformat(spec["retrieved_at"]),
                )
                db.add(source)
                db.flush()
                _track(db, data["version"], "source", source.id)
            elif not source.is_official or source.publisher != spec["publisher"]:
                raise InvalidManifest(f"canonical source divergence: {key}")
            sources[key] = source
        evidence_specs = {item["institution"]: item for item in data["institution_evidence"]}
        institutions: dict[str, Institution] = {}
        for spec in data["institutions"]:
            values = {
                "name": spec["name"],
                "kind": spec["kind"],
                "acronym": spec.get("acronym"),
                "state_branch": StateBranch.EXECUTIVE,
                "institution_type": InstitutionType(spec["institution_type"]),
                "operational_status": OperationalStatus(spec["operational_status"]),
                "coverage_level": CoverageLevel(spec["coverage_level"]),
                "official_website": spec.get("official_website"),
                "functions_summary": spec.get("functions_summary"),
            }
            institution = db.scalar(select(Institution).where(Institution.slug == spec["slug"]))
            if institution is not None and (
                institution.status != InstitutionStatus.CONFIRMED
                or institution.territory_id != territory.id
                or any(getattr(institution, field) != value for field, value in values.items())
            ):
                result.skipped += 1
                continue
            ev_spec = evidence_specs[spec["slug"]]
            source = sources[ev_spec["source"]]
            digest = _hash(source, ev_spec["title"], ev_spec["excerpt"], ev_spec["locator"])
            evidence = db.scalar(select(Evidence).where(Evidence.content_hash == digest))
            if evidence is None:
                evidence = Evidence(
                    source_id=source.id,
                    title=ev_spec["title"],
                    excerpt=ev_spec["excerpt"],
                    locator=ev_spec["locator"],
                    content_hash=digest,
                    metadata_={"manifest_version": data["version"], "evidence_kind": "institution"},
                    observed_at=source.retrieved_at,
                )
                db.add(evidence)
                db.flush()
                _track(db, data["version"], "evidence", evidence.id)
            if institution is None:
                institution = Institution(
                    slug=spec["slug"],
                    territory_id=territory.id,
                    status=InstitutionStatus.DRAFT,
                    last_reviewed_at=source.retrieved_at,
                    **values,
                )
                db.add(institution)
                db.flush()
                _track(db, data["version"], "institution", institution.id)
                link = InstitutionEvidence(institution_id=institution.id, evidence_id=evidence.id)
                db.add(link)
                db.flush()
                _track(db, data["version"], "institution_evidence", link.id)
                institution.status = InstitutionStatus.CONFIRMED
                result.created += 1
            else:
                existing_link = db.scalar(
                    select(InstitutionEvidence).where(
                        InstitutionEvidence.institution_id == institution.id,
                        InstitutionEvidence.evidence_id == evidence.id,
                    )
                )
                if existing_link is None:
                    existing_link = InstitutionEvidence(
                        institution_id=institution.id, evidence_id=evidence.id
                    )
                    db.add(existing_link)
                    db.flush()
                    _track(db, data["version"], "institution_evidence", existing_link.id)
                    result.updated += 1
                else:
                    result.unchanged += 1
            institutions[spec["slug"]] = institution
        rel_evidence = {_relationship_key(item): item for item in data["relationship_evidence"]}
        for spec in data["relationships"]:
            child = institutions.get(spec["child"])
            parent = db.scalar(select(Institution).where(Institution.slug == spec["parent"]))
            if child is None:
                result.skipped += 1
                continue
            if parent is None or parent.status != InstitutionStatus.CONFIRMED:
                raise InvalidManifest(f"confirmed parent institution is missing: {spec['parent']}")
            relation_type = InstitutionRelationshipType(spec["relationship_type"])
            valid_from = date.fromisoformat(spec["valid_from"]) if spec.get("valid_from") else None
            existing = db.scalar(
                select(InstitutionRelationship).where(
                    InstitutionRelationship.parent_institution_id == parent.id,
                    InstitutionRelationship.child_institution_id == child.id,
                    InstitutionRelationship.relationship_type == relation_type,
                    InstitutionRelationship.valid_from == valid_from,
                )
            )
            ev_spec = rel_evidence[_relationship_key(spec)]
            source = sources[ev_spec["source"]]
            digest = _hash(source, ev_spec["title"], ev_spec["excerpt"], ev_spec["locator"])
            evidence = db.scalar(select(Evidence).where(Evidence.content_hash == digest))
            if evidence is None:
                evidence = Evidence(
                    source_id=source.id,
                    title=ev_spec["title"],
                    excerpt=ev_spec["excerpt"],
                    locator=ev_spec["locator"],
                    content_hash=digest,
                    metadata_={
                        "manifest_version": data["version"],
                        "evidence_kind": "relationship",
                    },
                    observed_at=source.retrieved_at,
                )
                db.add(evidence)
                db.flush()
                _track(db, data["version"], "evidence", evidence.id)
            expected = (
                date.fromisoformat(spec["valid_to"]) if spec.get("valid_to") else None,
                spec["notes"],
                evidence.id,
            )
            if existing is not None:
                if (existing.valid_to, existing.notes, existing.evidence_id) != expected:
                    result.skipped += 1
                else:
                    result.unchanged += 1
                continue
            if relation_type in STRUCTURAL_RELATIONSHIPS and _would_cycle(db, parent.id, child.id):
                raise InvalidManifest("structural relationship would create a cycle")
            relationship = InstitutionRelationship(
                parent_institution_id=parent.id,
                child_institution_id=child.id,
                relationship_type=relation_type,
                valid_from=valid_from,
                valid_to=expected[0],
                notes=expected[1],
                evidence_id=evidence.id,
            )
            db.add(relationship)
            db.flush()
            _track(db, data["version"], "relationship", relationship.id)
            result.created += 1
        db.flush()
        db.rollback() if dry_run else db.commit()
    except Exception:
        db.rollback()
        result.errors += 1
        raise
    return result


def rollback_dependencies(
    db: Session, *, dry_run: bool = False, path: Path = MANIFEST_PATH
) -> RollbackSummary:
    data = read_manifest(path)
    result = RollbackSummary()
    try:
        db.expunge_all()
        records = list(
            db.scalars(
                select(ExecutiveDependencyLoadRecord).where(
                    ExecutiveDependencyLoadRecord.manifest_version == data["version"]
                )
            )
        )
        if not records:
            result.unchanged = 1
            db.rollback() if dry_run else db.commit()
            return result
        by_type: dict[str, list[ExecutiveDependencyLoadRecord]] = {}
        for record in records:
            by_type.setdefault(record.record_type, []).append(record)

        owned_relationships = {record.record_id for record in by_type.get("relationship", [])}
        owned_institutions = {record.record_id for record in by_type.get("institution", [])}
        owned_links = {record.record_id for record in by_type.get("institution_evidence", [])}
        safe_institutions: set[uuid.UUID] = set()
        for institution_id in owned_institutions:
            external_evidence = db.scalar(
                select(func.count())
                .select_from(InstitutionEvidence)
                .where(
                    InstitutionEvidence.institution_id == institution_id,
                    InstitutionEvidence.id.not_in(owned_links),
                )
            )
            external_relations = db.scalar(
                select(func.count())
                .select_from(InstitutionRelationship)
                .where(
                    (
                        (InstitutionRelationship.parent_institution_id == institution_id)
                        | (InstitutionRelationship.child_institution_id == institution_id)
                    ),
                    InstitutionRelationship.id.not_in(owned_relationships),
                )
            )
            if (
                external_evidence
                or external_relations
                or _has_other_institution_references(db, institution_id)
            ):
                result.skipped += 1
            else:
                safe_institutions.add(institution_id)

        db.expunge_all()
        for record in by_type.get("relationship", []):
            exists = db.get(InstitutionRelationship, record.record_id) is not None
            statement = delete(InstitutionRelationship).where(
                InstitutionRelationship.id == record.record_id
            )
            db.execute(statement.execution_options(synchronize_session=False))
            if exists:
                result.removed += 1
            _remove_record(db, record)
        db.flush()

        for institution_id in safe_institutions:
            db.execute(
                update(Institution)
                .where(Institution.id == institution_id)
                .values(status=InstitutionStatus.DRAFT)
                .execution_options(synchronize_session=False)
            )
        for record in by_type.get("institution_evidence", []):
            link_row = db.execute(
                select(InstitutionEvidence.institution_id).where(
                    InstitutionEvidence.id == record.record_id
                )
            ).scalar_one_or_none()
            if link_row in safe_institutions:
                db.execute(
                    delete(InstitutionEvidence)
                    .where(InstitutionEvidence.id == record.record_id)
                    .execution_options(synchronize_session=False)
                )
                _remove_record(db, record)
                result.removed += 1
            elif link_row not in owned_institutions and link_row is not None:
                link_count = db.scalar(
                    select(func.count())
                    .select_from(InstitutionEvidence)
                    .where(InstitutionEvidence.institution_id == link_row)
                )
                if link_count is not None and link_count > 1:
                    db.execute(
                        delete(InstitutionEvidence)
                        .where(InstitutionEvidence.id == record.record_id)
                        .execution_options(synchronize_session=False)
                    )
                    _remove_record(db, record)
                    result.removed += 1
                else:
                    result.skipped += 1
        db.flush()
        for record in by_type.get("institution", []):
            if record.record_id not in safe_institutions:
                continue
            db.execute(
                delete(Institution)
                .where(Institution.id == record.record_id)
                .execution_options(synchronize_session=False)
            )
            _remove_record(db, record)
            result.removed += 1
        db.flush()

        for record in by_type.get("evidence", []):
            evidence = db.get(Evidence, record.record_id)
            if evidence is None:
                _remove_record(db, record)
                continue
            institution_refs = db.scalar(
                select(func.count())
                .select_from(InstitutionEvidence)
                .where(InstitutionEvidence.evidence_id == evidence.id)
            )
            relationship_refs = db.scalar(
                select(func.count())
                .select_from(InstitutionRelationship)
                .where(InstitutionRelationship.evidence_id == evidence.id)
            )
            if institution_refs or relationship_refs:
                result.skipped += 1
                continue
            db.delete(evidence)
            _remove_record(db, record)
            result.removed += 1
        db.flush()

        for record in by_type.get("source", []):
            source = db.get(Source, record.record_id)
            if source is None:
                _remove_record(db, record)
                continue
            refs = db.scalar(
                select(func.count()).select_from(Evidence).where(Evidence.source_id == source.id)
            )
            if refs:
                result.skipped += 1
                continue
            db.delete(source)
            _remove_record(db, record)
            result.removed += 1
        db.flush()
        db.rollback() if dry_run else db.commit()
    except Exception:
        db.rollback()
        result.errors += 1
        raise
    return result


def summary_dict(summary: LoadSummary | RollbackSummary) -> dict[str, int]:
    return asdict(summary)
