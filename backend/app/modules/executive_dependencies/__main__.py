import argparse
import json

from app.db.session import SessionLocal
from app.modules.executive_dependencies.loader import (
    load_dependencies,
    rollback_dependencies,
    summary_dict,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load verified Executive Branch dependencies")
    parser.add_argument("action", nargs="?", choices=("load", "rollback"), default="load")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    with SessionLocal() as db:
        operation = rollback_dependencies if args.action == "rollback" else load_dependencies
        print(json.dumps(summary_dict(operation(db, dry_run=args.dry_run))))


if __name__ == "__main__":
    main()
