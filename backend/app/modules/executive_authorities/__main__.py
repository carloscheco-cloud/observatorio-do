import argparse
import json

from app.db.session import SessionLocal
from app.modules import models  # noqa: F401
from app.modules.executive_authorities.loader import (
    load_authorities,
    rollback_authorities,
    summary_dict,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", nargs="?", choices=("load", "rollback"), default="load")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    with SessionLocal() as db:
        operation = rollback_authorities if args.action == "rollback" else load_authorities
        print(json.dumps(summary_dict(operation(db, dry_run=args.dry_run)), sort_keys=True))


if __name__ == "__main__":
    main()
