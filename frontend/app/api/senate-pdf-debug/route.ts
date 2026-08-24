import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 120;

// eslint-disable-next-line @typescript-eslint/no-require-imports
const pdfParse: (buffer: Buffer) => Promise<{ text: string; numpages: number }> = require("pdf-parse/lib/pdf-parse.js");

const SOURCES: Record<number, string> = {
  118: "https://www.senadord.gob.do/Descargas/1388/asistencia-a-sesiones/60967/asistencia-de-senadores-al-pleno-sesion-no-118-de-fecha-17-de-junio-2026",
  119: "https://www.senadord.gob.do/Descargas/1388/asistencia-a-sesiones/61110/asistencia-de-senadores-al-pleno-sesion-no-119-de-fecha-24-de-junio-2026",
  120: "https://www.senadord.gob.do/Descargas/1388/asistencia-a-sesiones/61111/asistencia-de-senadores-al-pleno-sesion-no-120-de-fecha-24-de-junio-2026",
  121: "https://www.senadord.gob.do/Descargas/1388/asistencia-a-sesiones/61499/asistencia-de-senadores-al-pleno-sesion-no-121-de-fecha-30-de-junio-2026",
  122: "https://www.senadord.gob.do/Descargas/1388/asistencia-a-sesiones/61500/asistencia-de-senadores-al-pleno-sesion-no-122-de-fecha-30-de-junio-2026",
  123: "https://www.senadord.gob.do/Descargas/1388/asistencia-a-sesiones/61593/asistencia-de-senadores-al-pleno-sesion-no-123-de-fecha-8-de-julio-2026",
  124: "https://www.senadord.gob.do/Descargas/1388/asistencia-a-sesiones/61595/asistencia-de-senadores-al-pleno-sesion-no-124-de-fecha-10-de-julio-2026",
  125: "https://www.senadord.gob.do/Descargas/1388/asistencia-a-sesiones/61701/asistencia-de-senadores-al-pleno-sesion-no-125-de-fecha-20-de-julio-2026",
  128: "https://www.senadord.gob.do/Descargas/1388/asistencia-a-sesiones/61807/asistencia-de-senadores-al-pleno-sesion-no-128-de-fecha-24-de-julio-2026",
};

export async function GET(request: NextRequest) {
  const session = Number(request.nextUrl.searchParams.get("session") ?? "128");
  const url = SOURCES[session];
  if (!url) return NextResponse.json({ error: "unsupported session" }, { status: 400 });
  const response = await fetch(url, { cache: "no-store", headers: { "user-agent": "Mozilla/5.0 OED/1.0" } });
  if (!response.ok) return NextResponse.json({ error: `${response.status} ${response.statusText}` }, { status: 502 });
  const parsed = await pdfParse(Buffer.from(await response.arrayBuffer()));
  return NextResponse.json({ session, url, pages: parsed.numpages, text: parsed.text.slice(0, 20000) });
}
