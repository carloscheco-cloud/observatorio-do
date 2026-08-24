from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import asdict
from pathlib import Path

import app.modules.senate_reconstruction as sr


OFFICIAL_SESSION_SOURCES = {
    101: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/55548/acta-num-0101-de-fecha-27-de-febrero-2026"),
    102: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/55656/acta-num-0102-de-fecha-04-de-marzo-2026"),
    103: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/55818/acta-num-0103-de-fecha-11-de-marzo-2026"),
    104: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/55991/acta-num-0104-de-fecha-18-de-marzo-2026"),
    105: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/56400/acta-num-0105-de-fecha-24-de-marzo-2026"),
    106: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/56401/acta-num-0106-de-fecha-15-de-abril-2026"),
    107: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/60668/acta-num-0107-de-fecha-21-de-abril-2026"),
    108: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/60669/acta-num-0108-de-fecha-23-de-abril-2026"),
    109: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/60801/acta-num-0109-de-fecha-29-de-abril-2026"),
    110: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/61039/acta-num-0110-de-fecha-06-de-mayo-2026"),
    111: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/61239/acta-num-0111-de-fecha-13-de-mayo-2026"),
    112: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/61240/acta-num-0112-de-fecha-18-de-mayo-2026"),
    113: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/61414/acta-num-0113-de-fecha-27-de-mayo-2026"),
    114: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/61415/acta-num-0114-de-fecha-02-de-junio-2026"),
    115: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/61803/acta-num-0115-de-fecha-10-de-junio-2026"),
    116: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/61804/acta-num-0116-de-fecha-12-de-junio-2026"),
    117: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/61805/acta-num-0117-de-fecha-17-de-junio-2026"),
    118: ("acta", "https://www.senadord.gob.do/Descargas/1387/actas-de-sesiones/61806/acta-num-0118-de-fecha-17-de-junio-2026-extra"),
    119: ("attendance", "https://www.senadord.gob.do/Descargas/1388/asistencia-a-sesiones/61110/asistencia-de-senadores-al-pleno-sesion-no-119-de-fecha-24-de-junio-2026"),
    120: ("attendance", "https://www.senadord.gob.do/Descargas/1388/asistencia-a-sesiones/61111/asistencia-de-senadores-al-pleno-sesion-no-120-de-fecha-24-de-junio-2026"),
    121: ("attendance", "https://www.senadord.gob.do/Descargas/1388/asistencia-a-sesiones/61499/asistencia-de-senadores-al-pleno-sesion-no-121-de-fecha-30-de-junio-2026"),
    122: ("attendance", "https://www.senadord.gob.do/Descargas/1388/asistencia-a-sesiones/61500/asistencia-de-senadores-al-pleno-sesion-no-122-de-fecha-30-de-junio-2026"),
    123: ("attendance", "https://www.senadord.gob.do/Descargas/1388/asistencia-a-sesiones/61594/asistencia-de-senadores-al-pleno-sesion-no-123-de-fecha-8-de-julio-2026-2"),
    124: ("attendance", "https://www.senadord.gob.do/Descargas/1388/asistencia-a-sesiones/61595/asistencia-de-senadores-al-pleno-sesion-no-124-de-fecha-10-de-julio-2026"),
    125: ("attendance", "https://www.senadord.gob.do/Descargas/1388/asistencia-a-sesiones/61701/asistencia-de-senadores-al-pleno-sesion-no-125-de-fecha-20-de-julio-2026"),
}


def official_sources():
    return [
        sr.SessionSource(session, f"Senate session {session}", url, kind)
        for session, (kind, url) in sorted(OFFICIAL_SESSION_SOURCES.items())
    ]


def ocr_first_page(content: bytes) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        pdf = root / "source.pdf"
        image = root / "page"
        pdf.write_bytes(content)
        try:
            subprocess.run(
                ["pdftoppm", "-f", "1", "-singlefile", "-r", "220", "-png", str(pdf), str(image)],
                check=True,
                capture_output=True,
                text=True,
                timeout=45,
            )
            completed = subprocess.run(
                ["tesseract", str(root / "page.png"), "stdout", "--psm", "6", "-l", "eng"],
                check=True,
                capture_output=True,
                text=True,
                timeout=45,
            )
            return completed.stdout
        except Exception as exc:
            return f"OCR_ERROR {type(exc).__name__}: {exc}"


def print_source_diagnostics(sessions) -> None:
    attendance = next((source for source in sessions if source.source_kind == "attendance"), None)
    if attendance:
        content = sr.fetch(attendance.url)
        text = sr.pdf_text(content)
        print("ATTENDANCE_FORMAT_SESSION", attendance.session)
        print("ATTENDANCE_PYPDF_CHARS", len(text.strip()))
        print("ATTENDANCE_OCR_TEXT", " ".join(ocr_first_page(content).split())[:14000])


def main() -> None:
    sr.attendance_sources = official_sources
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
