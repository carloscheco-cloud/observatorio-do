from __future__ import annotations

import io
import json
import re
import unicodedata
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader

ATTENDANCE_INDEX = "https://www.senadord.gob.do/elaboracion-de-actas/asistencia-a-sesiones/"
INITIATIVES_INDEX = "https://www.senadord.gob.do/secretaria-general-legislativa/iniciativas-legislativas/"
APPROVED_INDEX = "https://www.senadord.gob.do/secretaria-general-legislativa/iniciativas-aprobadas/"
EXPIRED_INDEX = "https://www.senadord.gob.do/secretaria-general-legislativa/proyectos-perimidos/"
SIL_CURRENT = (
    "https://www.senado.gov.do/wfilemaster/consultante.aspx?bd=C2024-2028&"
    "url=lista_expedientes.aspx%3Fcoleccion%3D53"
)

TARGET_SESSION_MIN = 101
TARGET_SESSION_MAX = 126

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
    "ginnette-altagracia-bournigal": ["Ginette Bournigal", "Ginnette Bournigal"],
    "daniel-enrique-rivera-reyes": ["Daniel Rivera", "Daniel Enrique Rivera Reyes"],
    "lia-ynocencia-diaz-santana": ["Lía Díaz", "Lia Diaz"],
    "ramon-rogelio-genao-duran": ["Ramón Rogelio Genao", "Ramón Genao"],
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
            value = " ".join("".join(self._cell).split())
            self._row.append(value)
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


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-zA-Z0-9 ]+", " ", value).lower()
    return " ".join(value.split())


def pdf_text(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def classify_attendance(text: str, senator_id: str) -> str:
    """Return present/excused/absent/unknown from an official attendance document."""
    haystack = normalize(text)
    names = [SENATORS[senator_id], *ALIASES.get(senator_id, [])]
    for raw_name in names:
        name = normalize(raw_name)
        position = haystack.find(name)
        if position < 0:
            continue
        start = max(0, position - 90)
        end = min(len(haystack), position + len(name) + 120)
        context = haystack[start:end]
        if "excusa" in context or "excusado" in context:
            return "excused"
        if "ausente" in context or "inasistencia" in context:
            return "absent"
        if "presente" in context or "asistencia" in context:
            return "present"
        return "present"
    return "unknown"


@dataclass(frozen=True)
class SessionSource:
    session: int
    title: str
    url: str


@dataclass(frozen=True)
class AttendanceRecord:
    session: int
    senator_id: str
    status: str
    source_url: str


@dataclass(frozen=True)
class SilInitiative:
    number: str
    title: str
    raw_columns: list[str]
    source_url: str
    senator_ids: list[str]


def attendance_sources(max_pages: int = 10) -> list[SessionSource]:
    sources: dict[int, SessionSource] = {}
    for page in range(1, max_pages + 1):
        url = ATTENDANCE_INDEX if page == 1 else f"{ATTENDANCE_INDEX}page/{page}/"
        try:
            html = fetch(url).decode("utf-8", errors="replace")
        except Exception:
            if page == 1:
                raise
            break
        parser = LinkParser()
        parser.feed(html)
        found_on_page = 0
        for href, text in parser.links:
            normalized = normalize(text)
            match = re.search(r"sesion no (\d+)", normalized)
            if not match:
                continue
            session = int(match.group(1))
            if TARGET_SESSION_MIN <= session <= TARGET_SESSION_MAX:
                full_url = urllib.parse.urljoin(url, href)
                sources[session] = SessionSource(session, text, full_url)
                found_on_page += 1
        if page > 1 and not found_on_page and sources:
            break
    return [sources[key] for key in sorted(sources)]


def reconstruct_attendance() -> tuple[list[SessionSource], list[AttendanceRecord]]:
    sources = attendance_sources()
    records: list[AttendanceRecord] = []
    for source in sources:
        try:
            content = fetch(source.url)
            text = pdf_text(content)
        except Exception:
            continue
        for senator_id in SENATORS:
            records.append(
                AttendanceRecord(
                    session=source.session,
                    senator_id=senator_id,
                    status=classify_attendance(text, senator_id),
                    source_url=source.url,
                )
            )
    return sources, records


def summarize_attendance(records: Iterable[AttendanceRecord]) -> dict[str, dict[str, int | float]]:
    grouped: dict[str, dict[str, int]] = {
        senator_id: {"present": 0, "excused": 0, "absent": 0, "unknown": 0}
        for senator_id in SENATORS
    }
    for record in records:
        grouped[record.senator_id][record.status] += 1
    result: dict[str, dict[str, int | float]] = {}
    for senator_id, counts in grouped.items():
        denominator = counts["present"] + counts["excused"] + counts["absent"]
        result[senator_id] = {
            **counts,
            "sessions_classified": denominator,
            "presence_rate": round((counts["present"] / denominator) * 100, 1) if denominator else 0.0,
            "excused_rate": round((counts["excused"] / denominator) * 100, 1) if denominator else 0.0,
            "absence_rate": round((counts["absent"] / denominator) * 100, 1) if denominator else 0.0,
        }
    return result


def legislative_document_links(index_url: str, max_pages: int = 20) -> list[dict[str, str]]:
    documents: list[dict[str, str]] = []
    seen: set[str] = set()
    for page in range(1, max_pages + 1):
        url = index_url if page == 1 else f"{index_url}page/{page}/"
        try:
            html = fetch(url).decode("utf-8", errors="replace")
        except Exception:
            if page == 1:
                raise
            break
        parser = LinkParser()
        parser.feed(html)
        added = 0
        for href, text in parser.links:
            low = normalize(text)
            if not any(token in low for token in ("iniciativa", "aprobada", "perim", "sil", "agenda")):
                continue
            full_url = urllib.parse.urljoin(url, href)
            if full_url in seen:
                continue
            seen.add(full_url)
            documents.append({"title": text, "url": full_url})
            added += 1
        if page > 1 and added == 0:
            break
    return documents


def match_senators(text: str) -> list[str]:
    haystack = normalize(text)
    matched: list[str] = []
    for senator_id, full_name in SENATORS.items():
        candidates = [full_name, *ALIASES.get(senator_id, [])]
        if any(normalize(candidate) in haystack for candidate in candidates):
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


def write_outputs(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    sessions, records = reconstruct_attendance()
    summary = summarize_attendance(records)
    sil_inventory = extract_sil_inventory()
    (output_dir / "senate-attendance-sessions-2026.json").write_text(
        json.dumps([asdict(item) for item in sessions], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "senate-attendance-records-2026.json").write_text(
        json.dumps([asdict(item) for item in records], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "senate-attendance-summary-2026.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "senate-sil-initiatives-2024-2028.json").write_text(
        json.dumps([asdict(item) for item in sil_inventory], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "senate-legislative-source-index.json").write_text(
        json.dumps(discover_legislative_sources(), ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    write_outputs(Path("data/oed/senate"))
