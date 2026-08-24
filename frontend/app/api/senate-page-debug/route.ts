import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BASES = {
  attendance: "https://www.senadord.gob.do/elaboracion-de-actas/asistencia-a-sesiones/",
  actas: "https://www.senadord.gob.do/elaboracion-de-actas/actas-de-sesiones/",
};

function clean(value: string) {
  return value.replace(/<[^>]+>/g, " ").replace(/&nbsp;/gi, " ").replace(/&amp;/gi, "&").replace(/\s+/g, " ").trim();
}

function session(value: string) {
  const normalized = clean(value).normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  const match = normalized.match(/(?:sesion no|acta num|acta numero|acta)\D{0,12}(\d{3,4})/);
  return match ? Number(match[1]) : null;
}

async function probe(url: string) {
  const response = await fetch(url, { cache: "no-store", headers: { "user-agent": "Mozilla/5.0 OED/1.0" } });
  const html = await response.text();
  const sessions: Array<{ session: number; text: string; href: string }> = [];
  const pagination: Array<{ text: string; href: string; attrs: string }> = [];
  const regex = /<a\b([^>]*)href=["']([^"']+)["']([^>]*)>([\s\S]*?)<\/a>/gi;
  for (const match of html.matchAll(regex)) {
    const attrs = `${match[1]} ${match[3]}`.replace(/\s+/g, " ").trim();
    const text = clean(match[4]);
    const href = new URL(match[2], url).toString();
    const number = session(text);
    if (number != null) sessions.push({ session: number, text, href });
    if (/siguiente|anterior|next|prev|page|paged|pagination|^\d+$|\.\.\./i.test(`${text} ${href} ${attrs}`)) {
      pagination.push({ text, href, attrs });
    }
  }
  const searchFilterFragments = [...html.matchAll(/.{0,160}(?:search-filter|sf_paged|sf_data|pagination).{0,240}/gi)]
    .slice(0, 20)
    .map((match) => clean(match[0]));
  return { url, status: response.status, sessions, pagination, searchFilterFragments };
}

export async function GET(request: NextRequest) {
  const kind = request.nextUrl.searchParams.get("kind") === "actas" ? "actas" : "attendance";
  const page = Number(request.nextUrl.searchParams.get("page") ?? "2");
  const base = BASES[kind];
  const candidates = request.nextUrl.searchParams.get("base") === "1"
    ? [base]
    : [`${base}page/${page}/`, `${base}?sf_paged=${page}`, `${base}?sf_paged=${page}&sf_data=results`];
  return NextResponse.json({ kind, page, results: await Promise.all(candidates.map(probe)) });
}
