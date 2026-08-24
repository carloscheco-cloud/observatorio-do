from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import app.modules.senate_reconstruction as sr


_ORIGINAL_PAGED_LINKS = sr.paged_links


def bounded_paged_links(index_url: str, max_pages: int = 20):
    return _ORIGINAL_PAGED_LINKS(index_url, max_pages=min(max_pages, 6))


def print_source_diagnostics(sessions) -> None:
    attendance = next((source for source in sessions if source.source_kind == "attendance"), None)
    if attendance:
        text = sr.pdf_text(sr.fetch(attendance.url))
        print("ATTENDANCE_FORMAT_SESSION", attendance.session)
        print("ATTENDANCE_FORMAT_TEXT", " ".join(text.split())[:10000])

    acta = next((source for source in sessions if source.source_kind == "acta"), None)
    if acta:
        normalized = sr.normalize(sr.pdf_text(sr.fetch(acta.url)))
        for needle in ("cristobal", "jonhson", "secundino"):
            pos = normalized.find(needle)
            start = max(0, pos - 180) if pos >= 0 else 0
            end = min(len(normalized), pos + 420) if pos >= 0 else 0
            print(f"ACTA_NAME_CONTEXT_{needle.upper()}", normalized[start:end] if pos >= 0 else "NOT_FOUND")


def main() -> None:
    sr.paged_links = bounded_paged_links
    sr.ALIASES.setdefault("cristobal-venerado-castillo-liriano", []).append(
        "Cristóbal Venerado Antonio Castillo Liriano"
    )

    output_dir = Path("data/oed/senate")
    output_dir.mkdir(parents=True, exist_ok=True)

    sessions, records = sr.reconstruct_attendance()
    print_source_diagnostics(sessions)
    summary = sr.summarize_attendance(records)
    validation = sr.validate_common_cut(summary)

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
