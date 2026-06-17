import type { NextConfig } from "next";

/**
 * next.config.ts — Autofolio Next.js configuration
 *
 * API proxy: /api/:path* → API_INTERNAL_URL/api/:path*
 *
 * This rewrites keep the frontend on same-origin so session cookies
 * (httpOnly, SameSite=Strict) are sent without CORS preflight.
 * No API keys or secrets are exposed to the browser.
 */
const nextConfig: NextConfig = {
  async rewrites() {
    const apiBase = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${apiBase}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
