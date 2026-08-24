from __future__ import annotations

import io
import re
import unicodedata
import urllib.parse
import urllib.request
from html.parser import HTMLParser

from fastapi import FastAPI, HTTPException, Query
from pypdf import PdfReader

app = FastAPI()

ATTENDANCE_INDEX = "https://www.senadord.gob.do/elaboracion-de-actas/asistencia-a-sesiones/"
ACTAS_INDEX = "https://www.senadord.gob.do/elaboracion-de-actas/actas-de-sesiones/"

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
    "cristobal-venerado-castillo-liriano": ["Cristóbal Venerado Antonio Castillo Liriano"],
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
            self.links.append((self._href, " ".join("".join(self._text).split())))
            self._href = None
            self._text = []


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 OED/1.0 (+https://oedominicano.org)",
            "Accept": "text/html,application/pdf,application/xhtml+xml,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as response:
        return response.read()


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-zA-Z0-9 ]+", " ", value).lower()
    return " ".join(value.split())


def extract_session_number(text: str) -> int | None:
    normalized = normalize(text)
    for pattern in (r"sesion no (\d+)", r"acta num (\d+)", r"acta numero (\d+)", r"acta (\d{3,4})"):
        match = re.search(pattern, normalized)
        if match:
            return int(match.group(1))
    return None


def paged_links(index_url: str, max_pages: int = 8) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    seen: set[str] = set()
    for page in range(1, max_pages + 1):
        candidates = [
            index_url if page == 1 else f"{index_url}page/{page}/",
            index_url if page == 1 else f"{index_url}?sf_paged={page}",
        ]
        html = None
        page_url = None
        for candidate in candidates:
            try:
                html = fetch(candidate).decode("utf-8", errors="replace")
                page_url = candidate
                break
            except Exception:
                continue
        if html is None or page_url is None:
            break
        parser = LinkParser()
        parser.feed(html)
        page_added = 0
        for href, text in parser.links:
            session = extract_session_number(text)
            if session is None:
                continue
            full = urllib.parse.urljoin(page_url, href)
            key = f"{session}|{full}|{text}"
            if key in seen:
                continue
            seen.add(key)
            result.append({"session": session, "title": text, "url": full, "page": page})
            page_added += 1
        if page > 1 and page_added == 0:
            break
    return result


def catalog() -> dict[str, list[dict[str, object]]]:
    return {"actas": paged_links(ACTAS_INDEX), "attendance": paged_links(ATTENDANCE_INDEX)}


def select_source(session: int) -> dict[str, object]:
    sources = catalog()
    for kind in ("actas", "attendance"):
        matches = [row for row in sources[kind] if row["session"] == session]
        if matches:
            return {**matches[0], "kind": kind}
    raise HTTPException(status_code=404, detail=f"No official source found for session {session}")


def pdf_text(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def section_chunks(text: str, heading: str, stop_headings: tuple[str, ...]) -> list[str]:
    haystack = normalize(text)
    needle = normalize(heading)
    stops = tuple(normalize(x) for x in stop_headings)
    chunks: list[str] = []
    start = 0
    while True:
        idx = haystack.find(needle, start)
        if idx < 0:
            break
        content_start = idx + len(needle)
        candidates = [haystack.find(stop, content_start) for stop in stops]
        candidates = [value for value in candidates if value >= 0]
        content_end = min(candidates) if candidates else min(len(haystack), content_start + 6000)
        chunks.append(haystack[content_start:content_end])
        start = content_start
    return chunks


def senator_in_chunks(chunks: list[str], senator_id: str) -> bool:
    names = [normalize(SENATORS[senator_id]), *[normalize(x) for x in ALIASES.get(senator_id, [])]]
    return any(any(name in chunk for name in names) for chunk in chunks)


def final_marker_positions(text: str) -> list[int]:
    haystack = normalize(text)
    marker = normalize("Pase de lista final")
    positions: list[int] = []
    start = 0
    while True:
        idx = haystack.find(marker, start)
        if idx < 0:
            return positions
        positions.append(idx)
        start = idx + len(marker)


def classify(text: str, senator_id: str, final: bool) -> str:
    normalized = normalize(text)
    positions = final_marker_positions(text)
    body_final = positions[-1] if len(positions) >= 2 else None
    if final:
        if body_final is None:
            return "unknown"
        relevant = normalized[body_final:]
    else:
        relevant = normalized[:body_final] if body_final is not None else normalized

    present = section_chunks(
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
    excused = section_chunks(
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
    absent = section_chunks(
        relevant,
        "Senadores ausentes sin excusa legítima",
        (
            "Senadores incorporados después de comprobado el quórum e iniciada la sesión",
            "Comprobación de quórum",
            "Presentación de excusas",
            "Cierre de la sesión",
        ),
    )
    if senator_in_chunks(present, senator_id):
        return "present"
    if senator_in_chunks(excused, senator_id):
        return "excused"
    if senator_in_chunks(absent, senator_id):
        return "absent"
    return "unknown"


def late_arrival(text: str, senator_id: str) -> bool:
    chunks = section_chunks(
        text,
        "Senadores incorporados después de comprobado el quórum e iniciada la sesión",
        ("Comprobación de quórum", "Presentación de excusas", "Desarrollo de la sesión", "Pase de lista final"),
    )
    return senator_in_chunks(chunks, senator_id)


def reconstruct_session(session: int) -> dict[str, object]:
    source = select_source(session)
    try:
        content = fetch(str(source["url"]))
        text = pdf_text(content)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to read official PDF: {exc!r}") from exc

    has_final = len(final_marker_positions(text)) >= 2
    records = []
    for senator_id in SENATORS:
        first = classify(text, senator_id, False)
        final = classify(text, senator_id, True) if has_final else "unknown"
        late = late_arrival(text, senator_id)
        status = final if final != "unknown" else ("present" if late else first)
        records.append(
            {
                "senator_id": senator_id,
                "name": SENATORS[senator_id],
                "status": status,
                "first_pass": first,
                "final_pass": final,
                "late_arrival": late,
            }
        )
    return {
        "session": session,
        "source": source,
        "page_count": len(PdfReader(io.BytesIO(content)).pages),
        "has_final_pass": has_final,
        "records": records,
        "unknown_count": sum(1 for r in records if r["status"] == "unknown"),
    }


@app.get("/")
def senate_reconstruct(
    mode: str = Query(default="catalog", pattern="^(catalog|session)$"),
    session: int | None = Query(default=None, ge=90, le=140),
):
    if mode == "catalog":
        sources = catalog()
        return {
            "acta_sessions": sorted({int(x["session"]) for x in sources["actas"]}),
            "attendance_sessions": sorted({int(x["session"]) for x in sources["attendance"]}),
            "actas": sources["actas"],
            "attendance": sources["attendance"],
        }
    if session is None:
        raise HTTPException(status_code=400, detail="session is required for mode=session")
    return reconstruct_session(session)
