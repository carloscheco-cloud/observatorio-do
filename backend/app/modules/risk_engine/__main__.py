import argparse
import json
import uuid
from datetime import date

from sqlalchemy import select

from app.db.session import SessionLocal
from app.modules.risk_engine import service
from app.modules.risk_engine.models import RiskEvaluationRun
from app.modules.risk_engine.schemas import EvaluationRequest


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Observable risk-signal engine")
    result.add_argument("command", choices=("run", "dry-run", "backfill", "scores", "summary"))
    result.add_argument("--domain")
    result.add_argument("--institution-id", type=uuid.UUID)
    result.add_argument("--rule-id", type=uuid.UUID)
    result.add_argument("--period-start", type=date.fromisoformat)
    result.add_argument("--period-end", type=date.fromisoformat)
    return result


def main() -> None:
    args = parser().parse_args()
    with SessionLocal() as db:
        if args.command == "summary":
            runs = list(
                db.scalars(
                    select(RiskEvaluationRun)
                    .order_by(RiskEvaluationRun.created_at.desc())
                    .limit(20)
                )
            )
            print(
                json.dumps(
                    [
                        {
                            "run_code": row.run_code,
                            "status": row.status,
                            "findings_created": row.findings_created,
                        }
                        for row in runs
                    ]
                )
            )
            return
        if args.command == "scores":
            raise SystemExit(
                "Use POST /internal/risk-scores/recalculate with an explicit entity and period."
            )
        request = EvaluationRequest(
            trigger_type="backfill" if args.command == "backfill" else "manual",
            domain=args.domain,
            institution_id=args.institution_id,
            rule_id=args.rule_id,
            period_start=args.period_start,
            period_end=args.period_end,
            dry_run=args.command == "dry-run",
            backfill=args.command == "backfill",
        )
        run = service.run_evaluation(db, request, actor_type="service", actor_id=None)
        if request.dry_run:
            db.rollback()
        else:
            db.commit()
        print(
            json.dumps({"run_code": run.run_code, "status": run.status, "dry_run": request.dry_run})
        )


if __name__ == "__main__":
    main()
