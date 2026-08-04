import argparse
import json

from app.db.session import SessionLocal
from app.modules import models  # noqa: F401
from app.modules.digital_transparency.loader import (
    audit_report,
    load,
    recalculate,
    rollback,
    summary_dict,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        nargs="?",
        choices=("load", "recalculate", "audit-report", "rollback"),
        default="load",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    with SessionLocal() as db:
        if args.command == "audit-report":
            print(json.dumps(audit_report(db), ensure_ascii=False, sort_keys=True))
        else:
            operation = {"load": load, "recalculate": recalculate, "rollback": rollback}[
                args.command
            ]
            print(json.dumps(summary_dict(operation(db, dry_run=args.dry_run)), sort_keys=True))


if __name__ == "__main__":
    main()
