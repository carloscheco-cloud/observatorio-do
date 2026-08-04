import argparse
import json
import sys

from app.db.session import SessionLocal
from app.modules import models  # noqa: F401
from app.modules.digital_transparency.checks import (
    checks_report,
    rollback_checks,
    validate_manifest,
)
from app.modules.digital_transparency.checks import (
    summary_dict as checks_summary_dict,
)
from app.modules.digital_transparency.loader import (
    audit_report,
    load,
    recalculate,
    rollback,
    summary_dict,
)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "checks":
        checks_parser = argparse.ArgumentParser()
        checks_parser.add_argument("checks_command", choices=("validate", "report", "rollback"))
        checks_parser.add_argument("--dry-run", action="store_true")
        args = checks_parser.parse_args(sys.argv[2:])
        if args.checks_command == "validate":
            print(json.dumps(validate_manifest(), ensure_ascii=False, sort_keys=True))
            return
        with SessionLocal() as db:
            output = (
                checks_report(db)
                if args.checks_command == "report"
                else checks_summary_dict(rollback_checks(db, dry_run=args.dry_run))
            )
            print(json.dumps(output, ensure_ascii=False, sort_keys=True))
        return
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
