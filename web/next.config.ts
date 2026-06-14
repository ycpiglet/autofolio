import type { NextConfig } from "next";

/**
 * next.config.ts — Autofolio Next.js configuration
 *
 * API proxy: /api/:path* → http://127.0.0.1:8000/api/:path*
 *
 * This rewrites keep the frontend on same-origin so session cookies
 * (httpOnly, SameSite=Strict) are sent without CORS preflight.
 * No API keys or secrets are exposed to the browser.
 */
const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
