from __future__ import annotations

import io
import json
import re
import subprocess
import tempfile
import time
import unicodedata
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader

ATTENDANCE_INDEX = "https://www.senadord.gob.do/elaboracion-de-actas/asistencia-a-sesiones/"
ACTAS_INDEX = "https://www.senadord.gob.do/elaboracion-de-actas/actas-de-sesiones/"
APPROVED_INDEX = "https://www.senadord.gob.do/secretaria-general-legislativa/iniciativas-aprobadas/"
EXPIRED_INDEX = "https://www.senadord.gob.do/secretaria-general-legislativa/proyectos-perimidos/"
SIL_CURRENT = (
    "https://www.senado.gov.do/wfilemaster/consultante.aspx?bd=C2024-2028&"
    "url=lista_expedientes.aspx%3Fcoleccion%3D53"
)

# The official Senate source set publicly available for this cut is numbered 0101..0125.
# A secondary press benchmark reports 26 sessions. We preserve that discrepancy in
# validation metadata instead of inventing a session 126 that is not published by the Senate.
TARGET_SESSION_MIN = 101
TARGET_SESSION_MAX = 125
TARGET_SESSIONS = tuple(range(TARGET_SESSION_MIN, TARGET_SESSION_MAX + 1))
PRESS_REPORTED_SESSION_TOTAL = 26

OFFICIAL_SESSION_SOURCES: dict[int, tuple[str, str]] = {
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

SENATORS = {
    "lia-ynocencia-diaz-santana": "Lía Ynocencia Díaz Santana",
    "andres-guillermo-lama-perez": "Andrés Guillermo Lama Pérez",
    "moises-ayala-perez": "Moisés Ayala Pérez",
    "manuel-maria-rodriguez-ortega": "Manuel María Rodríguez Ortega",
    "omar-leonel-fernandez-dominguez": "Omar Leonel Fernández Domínguez",
    "franklin-martin-romero-morillo": "Franklin Martín Romero Morillo",
    "santiago-jose-zorrilla": "Santiago José Zorrilla",
    "jonhson-encarnacion-diaz": "Jonhson Encarnación Díaz",
    "carlos-manuel-gomez-urena": "Carlos Manuel Gómez Ureña",
    "cristobal-venerado-castillo-liriano": "Cristóbal Venerado Castillo Liriano",
    "maria-mercedes-ortiz-dilone": "María Mercedes Ortiz Diloné",
    "dagoberto-rodriguez-adames": "Dagoberto Rodríguez Adames",
    "rafael-baron-duluc-rijo": "Rafael Barón Duluc Rijo",
    "eduard-alexis-espiritusanto-castillo": "Eduard Alexis Espiritusanto Castillo",
    "ramon-rogelio-genao-duran": "Ramón Rogelio Genao Durán",
    "alexis-victoria-yeb": "Alexis Victoria Yeb",
    "hector-elpidio-acosta-restituyo": "Héctor Elpidio Acosta Restituyo",
    "bernardo-aleman-rodriguez": "Bernardo Alemán Rodríguez",
    "pedro-antonio-tineo-nunez": "Pedro Antonio Tineo Núñez",
    "secundino-velazquez-pimentel": "Secundino Velázquez Pimentel",
    "julito-fulcar-encarnacion": "Julito Fulcar Encarnación",
    "ginnette-altagracia-bournigal": "Ginnette Altagracia Bournigal Socías de Jiménez",
    "pedro-manuel-catrain-bonilla": "Pedro Manuel Catrain Bonilla",
    "gustavo-lara-salazar": "Gustavo Lara Salazar",
    "milciades-aneudy-ortiz-sajiun": "Milcíades Aneudy Ortiz Sajiun",
    "felix-ramon-bautista-rosario": "Félix Ramón Bautista Rosario",
    "aracelis-villanueva-figueroa": "Aracelis Villanueva Figueroa",
    "ricardo-de-los-santos-polanco": "Ricardo de los Santos Polanco",
    "daniel-enrique-rivera-reyes": "Daniel Enrique de Jesús Rivera Reyes",
    "casimiro-antonio-marte-familia": "Casimiro Antonio Marte Familia",
    "antonio-manuel-taveras-guzman": "Antonio Manuel Taveras Guzmán",
    "odalis-rafael-rodriguez-rodriguez": "Odalis Rafael Rodríguez Rodríguez",
}

ALIASES = {
    "casimiro-antonio-marte-familia": ["Antonio Marte", "Casimiro Antonio Marte"],
    "ginnette-altagracia-bournigal": [
        "Ginette Bournigal",
        "Ginnette Bournigal",
        "Ginette Alt Bournigal",
        "Ginnette Alt Bournigal",
    ],
    "daniel-enrique-rivera-reyes": ["Daniel Rivera", "Daniel Enrique Rivera Reyes"],
    "lia-ynocencia-diaz-santana": ["Lía Díaz", "Lia Diaz", "Lía Ynocencia Díaz Santana de Díaz"],
    "ramon-rogelio-genao-duran": ["Ramón Rogelio Genao", "Ramón Genao"],
    "cristobal-venerado-castillo-liriano": ["Cristóbal Venerado Antonio Castillo Liriano"],
    "jonhson-encarnacion-diaz": [
        "Jonhson Encarnación Díaz",
        "Johnson Encarnación Díaz",
        "Jonhson Encarnacion",
        "Johnson Encarnacion",
    ],
    "secundino-velazquez-pimentel": [
        "Secundino Velázquez Pimentel",
        "Secundino Velazquez",
        "Secundino Velasquez Pimentel",
    ],
}

# Secondary benchmark retained for comparison only. It assumes 26 sessions and therefore
# is not a publication gate for the 25-session primary-source reconstruction.
KNOWN_COMMON_CUT = {
    "andres-guillermo-lama-perez": (26, 0),
    "maria-mercedes-ortiz-dilone": (26, 0),
    "dagoberto-rodriguez-adames": (26, 0),
    "hector-elpidio-acosta-restituyo": (16, 10),
    "ginnette-altagracia-bournigal": (18, 8),
    "felix-ramon-bautista-rosario": (15, 11),
    "ricardo-de-los-santos-polanco": (26, 0),
    "daniel-enrique-rivera-reyes": (26, 0),
    "casimiro-antonio-marte-familia": (26, 0),
    "odalis-rafael-rodriguez-rodriguez": (26, 0),
}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href:
            text = " ".join("".join(self._text).split())
            self.links.append((self._href, text))
            self._href = None
            self._text = []


class TableTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self._row = []
        elif tag in {"td", "th"} and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._cell is not None and self._row is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if any(self._row):
                self.rows.append(self._row)
            self._row = None


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 OED/1.0 (+https://oedominicano.org)",
            "Accept": "text/html,application/pdf,application/xhtml+xml,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()


def fetch_with_retry(url: str, attempts: int = 4) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return fetch(url)
        except Exception as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(attempt * 2)
    assert last_error is not None
    raise last_error


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-zA-Z0-9 ]+", " ", value).lower()
    return " ".join(value.split())


def pdf_text(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def ocr_attendance_text(content: bytes) -> str:
    """OCR a one-page Senate attendance sheet, preserving table rows."""
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
        completed = subprocess.run(
            ["tesseract", str(image) + ".png", "stdout", "--psm", "3", "-l", "spa"],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return completed.stdout


def name_candidates(senator_id: str) -> list[str]:
    return [SENATORS[senator_id], *ALIASES.get(senator_id, [])]


def name_present(text: str, senator_id: str) -> bool:
    haystack = normalize(text)
    return any(normalize(candidate) in haystack for candidate in name_candidates(senator_id))


@dataclass(frozen=True)
class SessionSource:
    session: int
    title: str
    url: str
    source_kind: str


@dataclass(frozen=True)
class AttendanceRecord:
    session: int
    senator_id: str
    status: str
    first_pass: str
    final_pass: str
    late_arrival: bool
    source_url: str
    source_kind: str


@dataclass(frozen=True)
class SilInitiative:
    number: str
    title: str
    raw_columns: list[str]
    source_url: str
    senator_ids: list[str]


def paged_links(index_url: str, max_pages: int = 20) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    seen: set[str] = set()
    for page in range(1, max_pages + 1):
        page_url = index_url if page == 1 else f"{index_url}page/{page}/"
        try:
            html = fetch(page_url).decode("utf-8", errors="replace")
        except Exception:
            if page == 1:
                raise
            break
        parser = LinkParser()
        parser.feed(html)
        added = 0
        for href, text in parser.links:
            full_url = urllib.parse.urljoin(page_url, href)
            key = f"{full_url}|{text}"
            if key in seen:
                continue
            seen.add(key)
            links.append((full_url, text))
            added += 1
        if page > 2 and added == 0:
            break
    return links


def extract_session_number(text: str) -> int | None:
    normalized = normalize(text)
    patterns = (
        r"sesion no (\d+)",
        r"acta num (\d+)",
        r"acta numero (\d+)",
        r"acta (\d{3,4})",
    )
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if match:
            return int(match.group(1))
    return None


def attendance_sources() -> list[SessionSource]:
    return [
        SessionSource(session, f"Senate session {session}", url, kind)
        for session, (kind, url) in sorted(OFFICIAL_SESSION_SOURCES.items())
    ]


def section_chunks(text: str, heading: str, stop_headings: tuple[str, ...]) -> list[str]:
    haystack = normalize(text)
    needle = normalize(heading)
    stops = tuple(normalize(item) for item in stop_headings)
    chunks: list[str] = []
    start = 0
    while True:
        idx = haystack.find(needle, start)
        if idx < 0:
            break
        content_start = idx + len(needle)
        candidates = [haystack.find(stop, content_start) for stop in stops]
        candidates = [value for value in candidates if value >= 0]
        content_end = min(candidates) if candidates else min(len(haystack), content_start + 7000)
        chunks.append(haystack[content_start:content_end])
        start = content_start
    return chunks


def senator_in_chunks(chunks: Iterable[str], senator_id: str) -> bool:
    names = [normalize(candidate) for candidate in name_candidates(senator_id)]
    return any(any(name in chunk for name in names) for chunk in chunks)


def classify_pass(text: str, senator_id: str, *, final: bool) -> str:
    final_marker = normalize("Pase de lista final")
    normalized = normalize(text)
    if final and final_marker in normalized:
        relevant = normalized[normalized.rfind(final_marker):]
    elif not final and final_marker in normalized:
        relevant = normalized[:normalized.find(final_marker)]
    else:
        relevant = normalized

    present_chunks = section_chunks(
        relevant,
        "Senadores presentes",
        (
            "Senadores ausentes con excusa legítima",
            "Senadores ausentes sin excusa legítima",
            "Senadores incorporados después de comprobado el quórum e iniciada la sesión",
            "Comprobación de quórum",
            "Presentación de excusas",
            "Cierre de la sesión",
        ),
    )
    excused_chunks = section_chunks(
        relevant,
        "Senadores ausentes con excusa legítima",
        (
            "Senadores ausentes sin excusa legítima",
            "Senadores incorporados después de comprobado el quórum e iniciada la sesión",
            "Comprobación de quórum",
            "Presentación de excusas",
            "Cierre de la sesión",
        ),
    )
    absent_chunks = section_chunks(
        relevant,
        "Senadores ausentes sin excusa legítima",
        (
            "Senadores incorporados después de comprobado el quórum e iniciada la sesión",
            "Comprobación de quórum",
            "Presentación de excusas",
            "Cierre de la sesión",
        ),
    )

    if senator_in_chunks(present_chunks, senator_id):
        return "present"
    if senator_in_chunks(excused_chunks, senator_id):
        return "excused"
    if senator_in_chunks(absent_chunks, senator_id):
        return "absent"
    return "unknown"


def classify_attendance_sheet(text: str, senator_id: str) -> str:
    """Classify one senator from OCR table rows such as 'NAME PROVINCE PRESENTE'."""
    for raw_line in text.splitlines():
        line = normalize(raw_line)
        if not line:
            continue
        if not any(normalize(candidate) in line for candidate in name_candidates(senator_id)):
            continue
        if "presente" in line:
            return "present"
        if "excusa" in line:
            return "excused"
        if "ausente" in line or "inasistencia" in line:
            return "absent"
    return "unknown"


def incorporated_late(text: str, senator_id: str) -> bool:
    chunks = section_chunks(
        text,
        "Senadores incorporados después de comprobado el quórum e iniciada la sesión",
        (
            "Comprobación de quórum",
            "Presentación de excusas",
            "Desarrollo de la sesión",
            "Pase de lista final",
        ),
    )
    return senator_in_chunks(chunks, senator_id)


def reconstruct_attendance() -> tuple[list[SessionSource], list[AttendanceRecord]]:
    sources = attendance_sources()
    records: list[AttendanceRecord] = []
    for source in sources:
        try:
            content = fetch_with_retry(source.url)
            extracted_text = pdf_text(content)
            text = extracted_text if extracted_text.strip() else ocr_attendance_text(content)
        except Exception as exc:
            print("SENATE_SOURCE_ERROR", source.session, type(exc).__name__, str(exc))
            continue

        if source.source_kind == "attendance":
            for senator_id in SENATORS:
                status = classify_attendance_sheet(text, senator_id)
                records.append(
                    AttendanceRecord(
                        session=source.session,
                        senator_id=senator_id,
                        status=status,
                        first_pass=status,
                        final_pass=status,
                        late_arrival=False,
                        source_url=source.url,
                        source_kind=source.source_kind,
                    )
                )
            continue

        has_final = normalize("Pase de lista final") in normalize(text)
        for senator_id in SENATORS:
            first_pass = classify_pass(text, senator_id, final=False)
            final_pass = classify_pass(text, senator_id, final=True) if has_final else "unknown"
            late_arrival = incorporated_late(text, senator_id)
            if final_pass != "unknown":
                status = final_pass
            elif late_arrival:
                status = "present"
            else:
                status = first_pass
            records.append(
                AttendanceRecord(
                    session=source.session,
                    senator_id=senator_id,
                    status=status,
                    first_pass=first_pass,
                    final_pass=final_pass,
                    late_arrival=late_arrival,
                    source_url=source.url,
                    source_kind=source.source_kind,
                )
            )
    return sources, records


def summarize_attendance(records: Iterable[AttendanceRecord]) -> dict[str, dict[str, int | float]]:
    grouped: dict[str, dict[str, int]] = {
        senator_id: {"present": 0, "excused": 0, "absent": 0, "unknown": 0, "late_arrivals": 0}
        for senator_id in SENATORS
    }
    for record in records:
        grouped[record.senator_id][record.status] += 1
        if record.late_arrival:
            grouped[record.senator_id]["late_arrivals"] += 1
    result: dict[str, dict[str, int | float]] = {}
    source_total = len(TARGET_SESSIONS)
    for senator_id, counts in grouped.items():
        denominator = counts["present"] + counts["excused"] + counts["absent"]
        result[senator_id] = {
            **counts,
            "sessions_total": source_total,
            "sessions_classified": denominator,
            "presence_rate": round((counts["present"] / source_total) * 100, 1),
            "excused_rate": round((counts["excused"] / source_total) * 100, 1),
            "absence_rate": round((counts["absent"] / source_total) * 100, 1),
        }
    return result


def validate_common_cut(summary: dict[str, dict[str, int | float]]) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    for senator_id, (expected_present, expected_excused) in KNOWN_COMMON_CUT.items():
        row = summary[senator_id]
        checks.append(
            {
                "senator_id": senator_id,
                "benchmark_sessions": PRESS_REPORTED_SESSION_TOTAL,
                "official_sessions": len(TARGET_SESSIONS),
                "expected_present": expected_present,
                "actual_present": row["present"],
                "expected_excused": expected_excused,
                "actual_excused": row["excused"],
                "matches": row["present"] == expected_present and row["excused"] == expected_excused,
                "benchmark_is_secondary": True,
            }
        )
    return checks


def legislative_document_links(index_url: str, max_pages: int = 20) -> list[dict[str, str]]:
    documents: list[dict[str, str]] = []
    seen: set[str] = set()
    for url, text in paged_links(index_url, max_pages=max_pages):
        low = normalize(text)
        if not any(token in low for token in ("iniciativa", "aprobada", "perim", "sil", "agenda", "proyecto")):
            continue
        if url in seen:
            continue
        seen.add(url)
        documents.append({"title": text, "url": url})
    return documents


def match_senators(text: str) -> list[str]:
    haystack = normalize(text)
    matched: list[str] = []
    for senator_id in SENATORS:
        if any(normalize(candidate) in haystack for candidate in name_candidates(senator_id)):
            matched.append(senator_id)
    return matched


def extract_sil_inventory() -> list[SilInitiative]:
    html = fetch(SIL_CURRENT).decode("utf-8", errors="replace")
    parser = TableTextParser()
    parser.feed(html)
    initiatives: dict[str, SilInitiative] = {}
    number_pattern = re.compile(r"\b\d{4,5}-\d{4}-(?:PLO|SLO)-SE\b", re.I)
    for row in parser.rows:
        joined = " | ".join(row)
        match = number_pattern.search(joined)
        if not match:
            continue
        number = match.group(0).upper()
        title_candidates = [cell for cell in row if len(cell) >= 25 and number not in cell.upper()]
        title = max(title_candidates, key=len) if title_candidates else joined
        initiatives[number] = SilInitiative(
            number=number,
            title=title,
            raw_columns=row,
            source_url=SIL_CURRENT,
            senator_ids=match_senators(joined),
        )
    return [initiatives[key] for key in sorted(initiatives)]


def discover_legislative_sources() -> dict[str, list[dict[str, str]]]:
    return {
        "approved": legislative_document_links(APPROVED_INDEX),
        "expired": legislative_document_links(EXPIRED_INDEX),
    }


def write_attendance_outputs(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    sessions, records = reconstruct_attendance()
    summary = summarize_attendance(records)
    validation = validate_common_cut(summary)
    discrepancy = {
        "official_numbered_sessions": len(sessions),
        "official_session_range": [TARGET_SESSION_MIN, TARGET_SESSION_MAX],
        "secondary_press_reported_sessions": PRESS_REPORTED_SESSION_TOTAL,
        "resolved": len(sessions) == PRESS_REPORTED_SESSION_TOTAL,
        "publication_rule": "Primary Senate documents control; no unverified session is synthesized.",
    }
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
        json.dumps({"press_benchmark": validation, "session_count_discrepancy": discrepancy}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_outputs(output_dir: Path) -> None:
    write_attendance_outputs(output_dir)
    sil_inventory = extract_sil_inventory()
    (output_dir / "senate-sil-initiatives-2024-2028.json").write_text(
        json.dumps([asdict(item) for item in sil_inventory], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "senate-legislative-source-index.json").write_text(
        json.dumps(discover_legislative_sources(), ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    write_outputs(Path("data/oed/senate"))
