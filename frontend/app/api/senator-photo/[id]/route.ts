import { senators } from "@/lib/legislators";
import { senatorProfileUrls } from "@/lib/senator-completion";

export const revalidate = 86400;

function normalize(value: string) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function attr(tag: string, name: string) {
  const match = tag.match(new RegExp(`${name}=["']([^"']+)["']`, "i"));
  return match?.[1]?.replace(/&amp;/g, "&");
}

function absoluteUrl(url: string, base: string) {
  try {
    return new URL(url, base).toString();
  } catch {
    return null;
  }
}

export async function GET(
  _request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  const senator = senators.find((item) => item.id === id);
  const profileUrl = senatorProfileUrls[id];

  if (!senator || !profileUrl) {
    return new Response("Senador no encontrado", { status: 404 });
  }

  try {
    const response = await fetch(profileUrl, {
      headers: { "User-Agent": "OEDominicano/1.0 (+https://oedominicano.org)" },
      next: { revalidate: 86400 },
    });

    if (!response.ok) {
      return new Response("Fuente oficial no disponible", { status: 502 });
    }

    const html = await response.text();
    const normalizedName = normalize(senator.fullName);
    const keyTokens = normalizedName.split(" ").filter((token) => token.length > 3);
    const imageTags = html.match(/<img\b[^>]*>/gi) ?? [];

    let bestUrl: string | null = null;
    let bestScore = 0;

    for (const tag of imageTags) {
      const src = attr(tag, "src") ?? attr(tag, "data-src") ?? attr(tag, "data-lazy-src");
      if (!src) continue;

      const descriptor = normalize(
        [attr(tag, "alt"), attr(tag, "title"), src].filter(Boolean).join(" "),
      );
      const score = keyTokens.reduce(
        (total, token) => total + (descriptor.includes(token) ? 1 : 0),
        0,
      );

      if (score > bestScore) {
        bestScore = score;
        bestUrl = absoluteUrl(src, profileUrl);
      }
    }

    if (!bestUrl || bestScore < 2) {
      return new Response("Foto oficial no localizada", { status: 404 });
    }

    return Response.redirect(bestUrl, 307);
  } catch {
    return new Response("No fue posible resolver la foto oficial", { status: 502 });
  }
}
