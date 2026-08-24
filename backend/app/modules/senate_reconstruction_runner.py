from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import app.modules.senate_reconstruction as sr


_ORIGINAL_PAGED_LINKS = sr.paged_links


def bounded_paged_links(index_url: str, max_pages: int = 20):
    # The 2026 target cohort is recent and should be found in the first pages.
    # Bound discovery during attendance reconstruction so unrelated historical
    # pagination cannot hold the 32x26 matrix hostage for minutes.
    return _ORIGINAL_PAGED_LINKS(index_url, max_pages=min(max_pages, 6))


def main() -> None:
    sr.paged_links = bounded_paged_links

    output_dir = Path("data/oed/senate")
    output_dir.mkdir(parents=True, exist_ok=True)

    sessions, records = sr.reconstruct_attendance()
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
