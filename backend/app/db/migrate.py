"""Run Alembic under a PostgreSQL advisory lock."""

from __future__ import annotations

import argparse
from pathlib import Path

from alembic.config import Config
from sqlalchemy import text

from alembic import command
from app.db.session import engine

MIGRATION_LOCK_ID = 684_331_001


def run_migration(revision: str, *, downgrade: bool = False) -> None:
    config = Config(Path(__file__).parents[2] / "alembic.ini")
    with engine.connect() as lock_connection:
        lock_connection.execute(
            text("SELECT pg_advisory_lock(:lock_id)"), {"lock_id": MIGRATION_LOCK_ID}
        )
        try:
            if downgrade:
                command.downgrade(config, revision)
            else:
                command.upgrade(config, revision)
        finally:
            lock_connection.execute(
                text("SELECT pg_advisory_unlock(:lock_id)"), {"lock_id": MIGRATION_LOCK_ID}
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a serialized Alembic migration")
    parser.add_argument("action", choices=("upgrade", "downgrade"))
    parser.add_argument("revision", help="Alembic revision, for example 'head' or '-1'")
    args = parser.parse_args()
    run_migration(args.revision, downgrade=args.action == "downgrade")


if __name__ == "__main__":
    main()
