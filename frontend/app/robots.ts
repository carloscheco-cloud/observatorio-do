import type { MetadataRoute } from "next";
export default function robots(): MetadataRoute.Robots { const index = process.env.NEXT_PUBLIC_ROBOTS_INDEX === "true"; return { rules: { userAgent: "*", allow: "/", disallow: ["/api/", "/internal/"] }, sitemap: `${process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000"}/sitemap.xml`, host: index ? undefined : "localhost" }; }
