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
from app.modules.digital_transparency.pe06b import (
    audit_report as pe06b_audit_report,
)
from app.modules.digital_transparency.pe06b import (
    load as pe06b_load,
)
from app.modules.digital_transparency.pe06b import (
    recalculate as pe06b_recalculate,
)
from app.modules.digital_transparency.pe06b import (
    rollback as pe06b_rollback,
)
from app.modules.digital_transparency.pe06b import (
    summary_dict as pe06b_summary_dict,
)
from app.modules.digital_transparency.pe06d import (
    audit_report as pe06d_audit_report,
)
from app.modules.digital_transparency.pe06d import (
    load as pe06d_load,
)
from app.modules.digital_transparency.pe06d import (
    recalculate as pe06d_recalculate,
)
from app.modules.digital_transparency.pe06d import (
    rollback as pe06d_rollback,
)
from app.modules.digital_transparency.pe06d import (
    summary_dict as pe06d_summary_dict,
)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "pe06d":
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "pe06d_command",
            nargs="?",
            choices=("load", "recalculate", "audit-report", "rollback"),
            default="load",
        )
        parser.add_argument("--dry-run", action="store_true")
        args = parser.parse_args(sys.argv[2:])
        with SessionLocal() as db:
            if args.pe06d_command == "audit-report":
                print(json.dumps(pe06d_audit_report(db), ensure_ascii=False, sort_keys=True))
            else:
                operation = {
                    "load": pe06d_load,
                    "recalculate": pe06d_recalculate,
                    "rollback": pe06d_rollback,
                }[args.pe06d_command]
                print(
                    json.dumps(
                        pe06d_summary_dict(operation(db, dry_run=args.dry_run)), sort_keys=True
                    )
                )
        return
    if len(sys.argv) > 1 and sys.argv[1] == "pe06b":
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "pe06b_command",
            nargs="?",
            choices=("load", "recalculate", "audit-report", "rollback"),
            default="load",
        )
        parser.add_argument("--dry-run", action="store_true")
        args = parser.parse_args(sys.argv[2:])
        with SessionLocal() as db:
            if args.pe06b_command == "audit-report":
                print(json.dumps(pe06b_audit_report(db), ensure_ascii=False, sort_keys=True))
            else:
                pe06b_operation = {
                    "load": pe06b_load,
                    "recalculate": pe06b_recalculate,
                    "rollback": pe06b_rollback,
                }[args.pe06b_command]
                print(
                    json.dumps(
                        pe06b_summary_dict(pe06b_operation(db, dry_run=args.dry_run)),
                        sort_keys=True,
                    )
                )
        return
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
            pe05_operation = {"load": load, "recalculate": recalculate, "rollback": rollback}[
                args.command
            ]
            print(
                json.dumps(summary_dict(pe05_operation(db, dry_run=args.dry_run)), sort_keys=True)
            )


if __name__ == "__main__":
    main()
