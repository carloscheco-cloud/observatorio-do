from __future__ import annotations

import io
import json
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

from pypdf import PdfReader

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
    return [sr.SessionSource(session, f"Senate session {session}", url, kind) for session, (kind, url) in sorted(OFFICIAL_SESSION_SOURCES.items())]


def ocr_all_pages(content: bytes) -> list[str]:
    page_count = len(PdfReader(io.BytesIO(content)).pages)
    texts: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        pdf = root / "source.pdf"
        pdf.write_bytes(content)
        for page in range(1, page_count + 1):
            image = root / f"page-{page}"
            subprocess.run(["pdftoppm", "-f", str(page), "-singlefile", "-r", "240", "-png", str(pdf), str(image)], check=True, capture_output=True, timeout=45)
            completed = subprocess.run(["tesseract", str(image) + ".png", "stdout", "--psm", "6", "-l", "spa"], check=True, capture_output=True, text=True, timeout=45)
            texts.append(completed.stdout)
    return texts


def fetch_source(source: sr.SessionSource) -> tuple[sr.SessionSource, bytes, str]:
    content = sr.fetch(source.url)
    return source, content, sr.pdf_text(content)


def reconstruct_parallel():
    sources = official_sources()
    loaded: dict[int, tuple[bytes, str]] = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch_source, source): source for source in sources}
        for future in as_completed(futures):
            source = futures[future]
            try:
                _, content, text = future.result()
                loaded[source.session] = (content, text)
            except Exception as exc:
                print("SOURCE_FETCH_ERROR", source.session, type(exc).__name__, str(exc))

    records: list[sr.AttendanceRecord] = []
    for source in sources:
        payload = loaded.get(source.session)
        if payload is None:
            continue
        _, text = payload
        has_final = sr.normalize("Pase de lista final") in sr.normalize(text)
        for senator_id in sr.SENATORS:
            first_pass = sr.classify_pass(text, senator_id, final=False)
            final_pass = sr.classify_pass(text, senator_id, final=True) if has_final else "unknown"
            late_arrival = sr.incorporated_late(text, senator_id)
            status = final_pass if final_pass != "unknown" else ("present" if late_arrival else first_pass)
            records.append(sr.AttendanceRecord(session=source.session, senator_id=senator_id, status=status, first_pass=first_pass, final_pass=final_pass, late_arrival=late_arrival, source_url=source.url, source_kind=source.source_kind))
    return sources, records, loaded


def print_context(text: str, needle: str, label: str) -> None:
    normalized = sr.normalize(text)
    pos = normalized.find(sr.normalize(needle))
    if pos < 0:
        print(label, "NOT_FOUND")
        return
    print(label, normalized[max(0, pos - 260): min(len(normalized), pos + 520)])


def main() -> None:
    sr.ALIASES.setdefault("cristobal-venerado-castillo-liriano", []).append("Cristóbal Venerado Antonio Castillo Liriano")
    output_dir = Path("data/oed/senate")
    output_dir.mkdir(parents=True, exist_ok=True)

    sessions, records, loaded = reconstruct_parallel()

    if 119 in loaded:
        content, text = loaded[119]
        print("ATTENDANCE_FORMAT_SESSION", 119)
        print("ATTENDANCE_PYPDF_CHARS", len(text.strip()))
        pages = ocr_all_pages(content)
        print("ATTENDANCE_OCR_PAGES", len(pages))
        for idx, page_text in enumerate(pages, 1):
            print(f"ATTENDANCE_OCR_PAGE_{idx}", " ".join(page_text.split())[:16000])

    for session in (103, 106, 108, 110, 113, 116):
        if session in loaded:
            text = loaded[session][1]
            print_context(text, "Jonhson", f"CONTEXT_{session}_JONHSON")
            print_context(text, "Secundino", f"CONTEXT_{session}_SECUNDINO")
    for session in (105, 110):
        if session in loaded:
            text = loaded[session][1]
            print_context(text, "Antonio Marte", f"CONTEXT_{session}_ANTONIO_MARTE")
            print_context(text, "Félix Ramón Bautista", f"CONTEXT_{session}_FELIX_BAUTISTA")

    summary = sr.summarize_attendance(records)
    validation = sr.validate_common_cut(summary)
    (output_dir / "senate-attendance-sessions-2026.json").write_text(json.dumps([asdict(item) for item in sessions], ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "senate-attendance-records-2026.json").write_text(json.dumps([asdict(item) for item in records], ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "senate-attendance-summary-2026.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "senate-attendance-validation-2026.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
