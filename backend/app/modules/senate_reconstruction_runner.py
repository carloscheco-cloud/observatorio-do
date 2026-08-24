from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from app.modules.senate_reconstruction import (
    reconstruct_attendance,
    summarize_attendance,
    validate_common_cut,
)


def main() -> None:
    output_dir = Path("data/oed/senate")
    output_dir.mkdir(parents=True, exist_ok=True)

    sessions, records = reconstruct_attendance()
    summary = summarize_attendance(records)
    validation = validate_common_cut(summary)

    (output_dir / "senate-attendance-sessions-2026.json").write_text(
        json.dumps([asdict(item) for item in sessions], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "senate-attendance-records-2026.json").write_text(
        json.dumps([asdict(item) for item in records], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "senate-attendance-summary-2026.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "senate-attendance-validation-2026.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
