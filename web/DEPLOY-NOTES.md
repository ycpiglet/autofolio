# Web deploy notes (TASK-087 A7)

Config files only — these document deploy behavior; nothing here triggers a deploy.

## CSP (`web/vercel.json`)

The Content-Security-Policy is intentionally strict and `self`-scoped:

- **`connect-src 'self'` depends on Next.js server-side proxying.** All backend
  calls go through the Next `/api/*` rewrite (`web/next.config.ts` →
  `API_INTERNAL_URL`), so from the browser they are same-origin. If a future
  change makes the browser call an external origin *directly* (e.g. a market-data
  WebSocket, a CDN chart tile, or a client-side KIS call after a proxy refactor),
  that origin MUST be added to `connect-src` or the CSP will silently block it.
  CSP violations fail quietly — check DevTools → Console for `Refused to connect`.
- **`script-src 'unsafe-inline'`** is required for Next.js hydration (inline
  `<script>` JSON). `unsafe-eval` is intentionally NOT present. Removing
  `unsafe-inline` would require nonce middleware.
- **`style-src 'unsafe-inline'`** is required for Next.js styled-jsx inline
  styles; it is an independent surface (CSS injection) from script-src and should
  be revisited if a nonce/hash strategy is adopted.

## Railway (`railway.json`)

`healthcheckTimeout` is 30s to tolerate Python/uvicorn cold-start. Start command
mirrors the root `Dockerfile` CMD; healthcheck hits `/api/health`.
