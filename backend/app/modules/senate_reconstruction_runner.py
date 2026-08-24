from __future__ import annotations

import io
import json
import subprocess
import tempfile
import time
from dataclasses import asdict
from pathlib import Path

from pypdf import PdfReader

import app.modules.senate_reconstruction as sr

SESSION_119 = sr.SessionSource(
    119,
    "Senate session 119",
    "https://www.senadord.gob.do/Descargas/1388/asistencia-a-sesiones/61110/asistencia-de-senadores-al-pleno-sesion-no-119-de-fecha-24-de-junio-2026",
    "attendance",
)


def fetch_with_retry(url: str, attempts: int = 4) -> bytes:
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return sr.fetch(url)
        except Exception as exc:
            last = exc
            print("FETCH_RETRY", attempt, type(exc).__name__, str(exc))
            if attempt < attempts:
                time.sleep(attempt * 3)
    assert last is not None
    raise last


def ocr_modes(content: bytes) -> tuple[int, dict[int, str]]:
    page_count = len(PdfReader(io.BytesIO(content)).pages)
    outputs: dict[int, str] = {}
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        pdf = root / "source.pdf"
        image = root / "page"
        pdf.write_bytes(content)
        subprocess.run(
            ["pdftoppm", "-f", "1", "-singlefile", "-r", "300", "-png", str(pdf), str(image)],
            check=True,
            capture_output=True,
            timeout=60,
        )
        for psm in (3, 4, 6, 11, 12):
            completed = subprocess.run(
                ["tesseract", str(image) + ".png", "stdout", "--psm", str(psm), "-l", "spa"],
                check=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
            outputs[psm] = completed.stdout
    return page_count, outputs


def main() -> None:
    content = fetch_with_retry(SESSION_119.url)
    page_count, modes = ocr_modes(content)
    print("ATTENDANCE_FORMAT_SESSION", 119)
    print("ATTENDANCE_PAGE_COUNT", page_count)
    print("ATTENDANCE_PYPDF_CHARS", len(sr.pdf_text(content).strip()))
    for psm, text in modes.items():
        print(f"ATTENDANCE_OCR_PSM_{psm}", "\n" + text[:30000])

    output_dir = Path("data/oed/senate")
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = sr.summarize_attendance([])
    validation = sr.validate_common_cut(summary)
    (output_dir / "senate-attendance-sessions-2026.json").write_text(
        json.dumps([asdict(SESSION_119)], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "senate-attendance-records-2026.json").write_text("[]", encoding="utf-8")
    (output_dir / "senate-attendance-summary-2026.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "senate-attendance-validation-2026.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
