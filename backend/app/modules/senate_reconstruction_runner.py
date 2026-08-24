from __future__ import annotations

import json
from pathlib import Path

import app.modules.senate_reconstruction as sr


def main() -> None:
    # Session 120 OCR deforms Jonhson's given name, while preserving the unique
    # surname signature "Encarnación Díaz" on the same attendance row.
    sr.ALIASES.setdefault("jonhson-encarnacion-diaz", []).append("Encarnación Díaz")

    output_dir = Path("data/oed/senate")
    sr.write_attendance_outputs(output_dir)

    records = json.loads((output_dir / "senate-attendance-records-2026.json").read_text(encoding="utf-8"))
    unknown = [row for row in records if row["status"] == "unknown"]
    print("PRIMARY_SOURCE_SESSIONS", len(sr.TARGET_SESSIONS), list(sr.TARGET_SESSIONS))
    print("PRIMARY_SOURCE_RECORDS", len(records))
    print("PRIMARY_SOURCE_UNKNOWN", len(unknown))
    if unknown:
        print("PRIMARY_SOURCE_UNKNOWN_SAMPLE", json.dumps(unknown[:30], ensure_ascii=False))


if __name__ == "__main__":
    main()
