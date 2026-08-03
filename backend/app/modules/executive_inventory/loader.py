from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.evidence.models import Evidence
from app.modules.institutions.models import (
    CoverageLevel,
    Institution,
    InstitutionEvidence,
    InstitutionStatus,
    InstitutionType,
    OperationalStatus,
    StateBranch,
)
from app.modules.sources.models import Source
from app.modules.territories.models import Territory, TerritoryType

MANIFEST_PATH = Path(__file__).with_name("manifest.json")


class InvalidManifest(ValueError):
    pass


@dataclass
class LoadSummary:
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    skipped: int = 0
    errors: int = 0


def read_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    validate_manifest(data)
    return data


def validate_manifest(data: dict[str, Any]) -> None:
    required = {"version", "territory", "sources", "institutions", "relationships"}
    if not required.issubset(data):
        raise InvalidManifest(f"missing manifest fields: {sorted(required - data.keys())}")
    sources = data["sources"]
    slugs: set[str] = set()
    for item in data["institutions"]:
        needed = {"name", "slug"}
        if not needed.issubset(item):
            raise InvalidManifest("every institution requires name and slug")
        slug = item["slug"]
        if (
            slug in slugs
            or not slug
            or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in slug)
        ):
            raise InvalidManifest(f"invalid or duplicate slug: {slug}")
        slugs.add(slug)
        source_key = item.get("source", data.get("default_institution_source"))
        if source_key not in sources:
            raise InvalidManifest(f"unknown source for {slug}")
        source = sources[source_key]
        if (
            not source.get("url")
            or not source.get("name")
            or not source.get("source_type")
            or not source.get("retrieved_at")
        ):
            raise InvalidManifest(f"incomplete official source for {slug}")
        if not item.get("excerpt") and not item.get("sector"):
            raise InvalidManifest(f"missing evidence for {slug}")
        locator = item.get("locator")
        if source_key == "coedom" and (
            not isinstance(locator, str)
            or not locator.startswith("https://map.gob.do/COEDOM/Home/Details/")
        ):
            raise InvalidManifest(f"missing individual COEDOM locator for {slug}")
    for relation in data["relationships"]:
        if relation["parent"] == relation["child"]:
            raise InvalidManifest("self relationships are forbidden")
        if relation["parent"] not in slugs or relation["child"] not in slugs:
            raise InvalidManifest("relationship references unknown institution")


def _fingerprint(source_url: str, locator: str, slug: str, excerpt: str) -> str:
    return hashlib.sha256(f"{source_url}\n{locator}\n{slug}\n{excerpt}".encode()).hexdigest()


def load_inventory(
    db: Session, *, dry_run: bool = False, path: Path = MANIFEST_PATH
) -> LoadSummary:
    data = read_manifest(path)
    result = LoadSummary()
    try:
        territory_data = data["territory"]
        territory = db.scalar(select(Territory).where(Territory.code == territory_data["code"]))
        if territory is None:
            territory = Territory(
                name=territory_data["name"],
                code=territory_data["code"],
                type=TerritoryType(territory_data["type"]),
            )
            db.add(territory)
            db.flush()
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
            sources[key] = source
        for spec in data["institutions"]:
            source_key = spec.get("source", data["default_institution_source"])
            source = sources[source_key]
            excerpt = (
                spec.get("excerpt")
                or f"{spec['name']} — Tipología: Ministerio; Sector: {spec['sector']}."
            )
            locator = spec.get("locator", f"fila {spec['name']}")
            values = {
                "name": spec["name"],
                "kind": spec.get("institution_type", "ministry"),
                "acronym": spec.get("acronym"),
                "state_branch": StateBranch.EXECUTIVE,
                "institution_type": InstitutionType(spec.get("institution_type", "ministry")),
                "operational_status": OperationalStatus.ACTIVE,
                "coverage_level": CoverageLevel.BASIC,
                "official_website": spec.get("official_website"),
                "functions_summary": spec.get("functions_summary")
                or f"Órgano ministerial del sector {spec['sector']}.",
                "last_reviewed_at": datetime.fromisoformat(
                    data["sources"][source_key]["retrieved_at"]
                ),
            }
            existing = db.scalar(select(Institution).where(Institution.slug == spec["slug"]))
            if existing is not None and not (
                existing.territory_id == territory.id
                and existing.status == InstitutionStatus.CONFIRMED
                and all(
                    getattr(existing, key) == value
                    for key, value in values.items()
                    if key != "last_reviewed_at"
                )
            ):
                result.skipped += 1
                continue

            digest = _fingerprint(source.url, locator, spec["slug"], excerpt)
            evidence = db.scalar(select(Evidence).where(Evidence.content_hash == digest))
            if evidence is None:
                evidence = Evidence(
                    source_id=source.id,
                    title=f"Existencia oficial de {spec['name']}",
                    excerpt=excerpt,
                    locator=locator,
                    content_hash=digest,
                    metadata_={
                        "manifest_version": data["version"],
                        "source_type": data["sources"][source_key]["source_type"],
                    },
                    observed_at=datetime.fromisoformat(data["sources"][source_key]["retrieved_at"]),
                )
                db.add(evidence)
                db.flush()
            if existing is None:
                existing = Institution(
                    slug=spec["slug"],
                    territory_id=territory.id,
                    status=InstitutionStatus.DRAFT,
                    **values,
                )
                db.add(existing)
                db.flush()
                db.add(
                    InstitutionEvidence(
                        institution_id=existing.id,
                        evidence_id=evidence.id,
                        relation="supports_existence",
                    )
                )
                db.flush()
                existing.status = InstitutionStatus.CONFIRMED
                result.created += 1
            else:
                link = db.scalar(
                    select(InstitutionEvidence).where(
                        InstitutionEvidence.institution_id == existing.id,
                        InstitutionEvidence.evidence_id == evidence.id,
                    )
                )
                if link is None:
                    db.add(
                        InstitutionEvidence(
                            institution_id=existing.id,
                            evidence_id=evidence.id,
                            relation="supports_existence",
                        )
                    )
                    result.updated += 1
                else:
                    result.unchanged += 1
        db.flush()
        if dry_run:
            db.rollback()
        else:
            db.commit()
    except Exception:
        db.rollback()
        result.errors += 1
        raise
    return result


def summary_dict(summary: LoadSummary) -> dict[str, int]:
    return asdict(summary)
