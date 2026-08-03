import argparse
import json

from app.db.session import SessionLocal
from app.modules.executive_inventory.loader import load_inventory, summary_dict


def main() -> None:
    parser = argparse.ArgumentParser(description="Load the official Executive Branch inventory")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    with SessionLocal() as db:
        print(
            json.dumps(summary_dict(load_inventory(db, dry_run=args.dry_run)), ensure_ascii=False)
        )


if __name__ == "__main__":
    main()
