import type { MetadataRoute } from "next";
export default function robots(): MetadataRoute.Robots { const index = process.env.NEXT_PUBLIC_ROBOTS_INDEX === "true"; const site = process.env.NEXT_PUBLIC_SITE_URL!; return { rules: { userAgent: "*", allow: "/", disallow: ["/api/", "/internal/"] }, sitemap: `${site}/sitemap.xml`, host: index ? new URL(site).host : undefined }; }
