import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BASES = {
  attendance: "https://www.senadord.gob.do/elaboracion-de-actas/asistencia-a-sesiones/",
  actas: "https://www.senadord.gob.do/elaboracion-de-actas/actas-de-sesiones/",
};

function clean(value: string) {
  return value.replace(/<[^>]+>/g, " ").replace(/&[^;]+;/g, " ").replace(/\s+/g, " ").trim();
}

function session(value: string) {
  const normalized = clean(value).normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  const match = normalized.match(/(?:sesion no|acta num|acta numero|acta)\D{0,12}(\d{3,4})/);
  return match ? Number(match[1]) : null;
}

async function probe(url: string) {
  const response = await fetch(url, { cache: "no-store", headers: { "user-agent": "Mozilla/5.0 OED/1.0" } });
  const html = await response.text();
  const links: Array<{ session: number; text: string; href: string }> = [];
  const regex = /<a\b[^>]*href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi;
  for (const match of html.matchAll(regex)) {
    const text = clean(match[2]);
    const number = session(text);
    if (number != null) links.push({ session: number, text, href: new URL(match[1], url).toString() });
  }
  return { url, status: response.status, links };
}

export async function GET(request: NextRequest) {
  const kind = request.nextUrl.searchParams.get("kind") === "actas" ? "actas" : "attendance";
  const page = Number(request.nextUrl.searchParams.get("page") ?? "2");
  const base = BASES[kind];
  const candidates = [
    `${base}page/${page}/`,
    `${base}?sf_paged=${page}`,
    `${base}?sf_paged=${page}&sf_data=results`,
  ];
  return NextResponse.json({ kind, page, results: await Promise.all(candidates.map(probe)) });
}
