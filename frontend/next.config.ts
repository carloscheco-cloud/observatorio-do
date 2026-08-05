import type { NextConfig } from "next";

const apiUrl = process.env.NEXT_PUBLIC_API_URL;
if (!apiUrl) throw new Error("NEXT_PUBLIC_API_URL is required");
const executiveApiUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
if (!executiveApiUrl) throw new Error("NEXT_PUBLIC_API_BASE_URL is required");
if (!process.env.NEXT_PUBLIC_SITE_URL) throw new Error("NEXT_PUBLIC_SITE_URL is required");
const apiOrigins = [...new Set([new URL(apiUrl).origin, new URL(executiveApiUrl).origin])].join(" ");

const nextConfig: NextConfig = {
  output: "standalone",
  async headers() {
    return [{
      source: "/(.*)",
      headers: [
        { key: "X-Content-Type-Options", value: "nosniff" },
        { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        { key: "Content-Security-Policy", value: `default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self' ${apiOrigins}` }
      ]
    }];
  }
};
export default nextConfig;
