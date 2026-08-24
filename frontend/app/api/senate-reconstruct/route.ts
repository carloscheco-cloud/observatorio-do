import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 300;

// Temporary execution route on PR #29. It is not intended to remain in production.
// Import the library implementation directly: pdf-parse's package entry runs its sample PDF when bundled by Next.
// eslint-disable-next-line @typescript-eslint/no-require-imports
const pdfParse: (buffer: Buffer) => Promise<{ text: string; numpages: number }> = require("pdf-parse/lib/pdf-parse.js");

const ATTENDANCE_INDEX = "https://www.senadord.gob.do/elaboracion-de-actas/asistencia-a-sesiones/";
const ACTAS_INDEX = "https://www.senadord.gob.do/elaboracion-de-actas/actas-de-sesiones/";

const SENATORS: Record<string, string> = {
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
};

const ALIASES: Record<string, string[]> = {
  "casimiro-antonio-marte-familia": ["Antonio Marte", "Casimiro Antonio Marte"],
  "ginnette-altagracia-bournigal": ["Ginette Bournigal", "Ginnette Bournigal"],
  "daniel-enrique-rivera-reyes": ["Daniel Rivera", "Daniel Enrique Rivera Reyes"],
  "lia-ynocencia-diaz-santana": ["Lía Díaz", "Lia Diaz"],
  "ramon-rogelio-genao-duran": ["Ramón Rogelio Genao", "Ramón Genao"],
  "cristobal-venerado-castillo-liriano": ["Cristóbal Venerado Antonio Castillo Liriano"],
};

type Source = { session: number; title: string; url: string; page: number; kind?: "acta" | "attendance" };
type Status = "present" | "excused" | "absent" | "unknown";

type RecordRow = {
  senator_id: string;
  name: string;
  status: Status;
  first_pass: Status;
  final_pass: Status;
  late_arrival: boolean;
};

function normalize(value: string): string {
  return value
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9 ]+/g, " ")
    .toLowerCase()
    .replace(/\s+/g, " ")
    .trim();
}

function decodeHtml(value: string): string {
  return value
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&#8211;|&#x2013;/gi, "–")
    .replace(/&#8212;|&#x2014;/gi, "—")
    .replace(/&#0*([0-9]+);/g, (_, n) => String.fromCharCode(Number(n)))
    .replace(/\s+/g, " ")
    .trim();
}

function extractSessionNumber(text: string): number | null {
  const value = normalize(text);
  for (const pattern of [/sesion no (\d+)/, /acta num (\d+)/, /acta numero (\d+)/, /acta (\d{3,4})/]) {
    const match = value.match(pattern);
    if (match) return Number(match[1]);
  }
  return null;
}

async function fetchBytes(url: string): Promise<Buffer> {
  const response = await fetch(url, {
    cache: "no-store",
    headers: {
      "user-agent": "Mozilla/5.0 OED/1.0 (+https://oedominicano.org)",
      accept: "text/html,application/pdf,application/xhtml+xml,*/*;q=0.8",
    },
  });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText} for ${url}`);
  return Buffer.from(await response.arrayBuffer());
}

async function fetchText(url: string): Promise<string> {
  return (await fetchBytes(url)).toString("utf8");
}

function anchors(html: string, base: string): Array<{ href: string; text: string }> {
  const rows: Array<{ href: string; text: string }> = [];
  const regex = /<a\b[^>]*href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi;
  for (const match of html.matchAll(regex)) {
    try {
      rows.push({ href: new URL(match[1], base).toString(), text: decodeHtml(match[2]) });
    } catch {
      // Ignore malformed links from unrelated page widgets.
    }
  }
  return rows;
}

async function pagedLinks(indexUrl: string, maxPages = 10): Promise<Source[]> {
  const result: Source[] = [];
  const seen = new Set<string>();
  for (let page = 1; page <= maxPages; page += 1) {
    const candidates = page === 1 ? [indexUrl] : [`${indexUrl}page/${page}/`, `${indexUrl}?sf_paged=${page}`];
    let html: string | null = null;
    let pageUrl: string | null = null;
    for (const candidate of candidates) {
      try {
        html = await fetchText(candidate);
        pageUrl = candidate;
        break;
      } catch {
        // Try alternate pagination form.
      }
    }
    if (!html || !pageUrl) break;
    let added = 0;
    for (const link of anchors(html, pageUrl)) {
      const session = extractSessionNumber(link.text);
      if (session === null) continue;
      const key = `${session}|${link.href}|${link.text}`;
      if (seen.has(key)) continue;
      seen.add(key);
      result.push({ session, title: link.text, url: link.href, page });
      added += 1;
    }
    if (page > 1 && added === 0) break;
  }
  return result;
}

async function catalog() {
  const [actas, attendance] = await Promise.all([pagedLinks(ACTAS_INDEX), pagedLinks(ATTENDANCE_INDEX)]);
  return { actas, attendance };
}

async function selectSource(session: number): Promise<Source> {
  const sources = await catalog();
  const acta = sources.actas.find((row) => row.session === session);
  if (acta) return { ...acta, kind: "acta" };
  const attendance = sources.attendance.find((row) => row.session === session);
  if (attendance) return { ...attendance, kind: "attendance" };
  throw new Error(`No official source found for session ${session}`);
}

function sectionChunks(text: string, heading: string, stopHeadings: string[]): string[] {
  const haystack = normalize(text);
  const needle = normalize(heading);
  const stops = stopHeadings.map(normalize);
  const chunks: string[] = [];
  let start = 0;
  while (true) {
    const index = haystack.indexOf(needle, start);
    if (index < 0) break;
    const contentStart = index + needle.length;
    const candidates = stops.map((stop) => haystack.indexOf(stop, contentStart)).filter((value) => value >= 0);
    const contentEnd = candidates.length ? Math.min(...candidates) : Math.min(haystack.length, contentStart + 6000);
    chunks.push(haystack.slice(contentStart, contentEnd));
    start = contentStart;
  }
  return chunks;
}

function senatorInChunks(chunks: string[], senatorId: string): boolean {
  const names = [SENATORS[senatorId], ...(ALIASES[senatorId] ?? [])].map(normalize);
  return chunks.some((chunk) => names.some((name) => chunk.includes(name)));
}

function finalMarkerPositions(text: string): number[] {
  const haystack = normalize(text);
  const marker = normalize("Pase de lista final");
  const positions: number[] = [];
  let start = 0;
  while (true) {
    const index = haystack.indexOf(marker, start);
    if (index < 0) return positions;
    positions.push(index);
    start = index + marker.length;
  }
}

function classify(text: string, senatorId: string, final: boolean): Status {
  const normalized = normalize(text);
  const positions = finalMarkerPositions(text);
  const bodyFinal = positions.length >= 2 ? positions.at(-1)! : null;
  let relevant = normalized;
  if (final) {
    if (bodyFinal === null) return "unknown";
    relevant = normalized.slice(bodyFinal);
  } else if (bodyFinal !== null) {
    relevant = normalized.slice(0, bodyFinal);
  }

  const present = sectionChunks(relevant, "Senadores presentes", [
    "Senadores ausentes con excusa legítima",
    "Senadores ausentes sin excusa legítima",
    "Senadores incorporados después de comprobado el quórum e iniciada la sesión",
    "Comprobación de quórum",
    "Presentación de excusas",
    "Cierre de la sesión",
  ]);
  const excused = sectionChunks(relevant, "Senadores ausentes con excusa legítima", [
    "Senadores ausentes sin excusa legítima",
    "Senadores incorporados después de comprobado el quórum e iniciada la sesión",
    "Comprobación de quórum",
    "Presentación de excusas",
    "Cierre de la sesión",
  ]);
  const absent = sectionChunks(relevant, "Senadores ausentes sin excusa legítima", [
    "Senadores incorporados después de comprobado el quórum e iniciada la sesión",
    "Comprobación de quórum",
    "Presentación de excusas",
    "Cierre de la sesión",
  ]);
  if (senatorInChunks(present, senatorId)) return "present";
  if (senatorInChunks(excused, senatorId)) return "excused";
  if (senatorInChunks(absent, senatorId)) return "absent";
  return "unknown";
}

function lateArrival(text: string, senatorId: string): boolean {
  return senatorInChunks(
    sectionChunks(text, "Senadores incorporados después de comprobado el quórum e iniciada la sesión", [
      "Comprobación de quórum",
      "Presentación de excusas",
      "Desarrollo de la sesión",
      "Pase de lista final",
    ]),
    senatorId,
  );
}

async function reconstructSession(session: number) {
  const source = await selectSource(session);
  const content = await fetchBytes(source.url);
  const parsed = await pdfParse(content);
  const text = parsed.text;
  const hasFinal = finalMarkerPositions(text).length >= 2;
  const records: RecordRow[] = Object.entries(SENATORS).map(([senatorId, name]) => {
    const firstPass = classify(text, senatorId, false);
    const finalPass = hasFinal ? classify(text, senatorId, true) : "unknown";
    const late = lateArrival(text, senatorId);
    const status: Status = finalPass !== "unknown" ? finalPass : late ? "present" : firstPass;
    return { senator_id: senatorId, name, status, first_pass: firstPass, final_pass: finalPass, late_arrival: late };
  });
  return {
    session,
    source,
    page_count: parsed.numpages,
    has_final_pass: hasFinal,
    unknown_count: records.filter((row) => row.status === "unknown").length,
    records,
  };
}

export async function GET(request: NextRequest) {
  const mode = request.nextUrl.searchParams.get("mode") ?? "catalog";
  try {
    if (mode === "catalog") {
      const sources = await catalog();
      return NextResponse.json({
        acta_sessions: [...new Set(sources.actas.map((row) => row.session))].sort((a, b) => a - b),
        attendance_sessions: [...new Set(sources.attendance.map((row) => row.session))].sort((a, b) => a - b),
        actas: sources.actas,
        attendance: sources.attendance,
      });
    }
    if (mode === "session") {
      const session = Number(request.nextUrl.searchParams.get("session"));
      if (!Number.isInteger(session)) return NextResponse.json({ error: "session required" }, { status: 400 });
      return NextResponse.json(await reconstructSession(session));
    }
    return NextResponse.json({ error: "unsupported mode" }, { status: 400 });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
