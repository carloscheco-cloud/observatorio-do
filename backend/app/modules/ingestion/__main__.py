from __future__ import annotations

import argparse
import json
import uuid

from sqlalchemy import select

from app.db.session import SessionLocal
from app.modules.ingestion import service
from app.modules.ingestion.jobs import claim_next_job
from app.modules.ingestion.models import (
    DataLineageLink,
    IngestionSchedule,
    QuarantineRecord,
    SourceCatalog,
)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Controlled ETL operations")
    commands = root.add_subparsers(dest="command", required=True)
    sources = commands.add_parser("sources")
    sources.add_argument("action", choices=("list", "test"))
    sources.add_argument("--source")
    for command in (
        "discover",
        "ingest",
        "retry",
        "parse",
        "validate",
        "canonicalize",
        "backfill",
        "lineage",
        "schedules",
        "jobs",
        "quarantine",
        "quality",
    ):
        item = commands.add_parser(command)
        item.add_argument("action", nargs="?")
        item.add_argument("--source")
        item.add_argument("--domain")
        item.add_argument("--period")
        item.add_argument("--dry-run", action="store_true")
        item.add_argument("--id")
    return root


def main() -> None:
    args = parser().parse_args()
    with SessionLocal() as db:
        if args.command == "sources" and args.action == "list":
            print(
                json.dumps(
                    [
                        {"id": str(item.id), "code": item.stable_code}
                        for item in service.list_models(db, SourceCatalog)
                    ]
                )
            )
        elif args.command in {"discover", "ingest"}:
            source = db.scalar(
                select(SourceCatalog).where(SourceCatalog.stable_code == args.source)
            )
            if source is None:
                raise SystemExit("source not found")
            run = service.start_run(db, source, "manual", "human", dry_run=args.dry_run)
            print(run.run_code)
        elif args.command == "jobs" and args.action == "work":
            job = claim_next_job(db, "cli-worker")
            db.commit()
            print(job.id if job else "no pending jobs")
        elif args.command == "schedules":
            print(len(service.list_models(db, IngestionSchedule)))
        elif args.command == "quarantine":
            print(len(service.list_models(db, QuarantineRecord)))
        elif args.command == "lineage" and args.id:
            entity_id = uuid.UUID(args.id)
            print(
                len(
                    list(
                        db.scalars(
                            select(DataLineageLink).where(
                                DataLineageLink.canonical_entity_id == entity_id
                            )
                        )
                    )
                )
            )
        elif args.command == "quality":
            print(json.dumps(service.metrics(db), default=str))
        else:
            raise SystemExit("command requires an explicit supported action")


if __name__ == "__main__":
    main()
