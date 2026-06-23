/**
 * avatar.ts — deterministic, self-hosted avatar generation for Autofolio.
 *
 * Self-hosted: renders avatars locally via the @dicebear npm library at
 * build-time / SSR — there is NO runtime CDN call (api.dicebear.com is never
 * hit). Output is a self-contained SVG / data-URI usable as an <img> src with
 * zero client JS.
 *
 * Deterministic: a stable id (userId / agentId) used as the `seed` always
 * produces the same avatar, so identities stay visually consistent.
 *
 * Styles (both license-clean for commercial use):
 *   - account → "notionists"  (CC0 — public domain)
 *   - agent   → "bottts"      (free for commercial use; robot persona)
 *
 * Pure module: no React, no DOM, no network. Safe to import on the server.
 */
import { createAvatar } from "@dicebear/core";
import { bottts, notionists } from "@dicebear/collection";

/** Which avatar persona to render: an account holder, or an AI agent. */
export type AvatarVariant = "account" | "agent";

/**
 * Render a deterministic avatar as an SVG string.
 *
 * Build-time / SSR only — synchronous, no runtime API call.
 *
 * @param seed    — stable id (e.g. userId or agentId) driving the avatar
 * @param variant — "account" (notionists, CC0) or "agent" (bottts). Default "account".
 * @returns an SVG document string
 */
export function avatarSvg(
  seed: string,
  variant: AvatarVariant = "account",
): string {
  // createAvatar is called per-branch so its generic options type is inferred
  // from the concrete style (bottts and notionists have distinct option types,
  // so a `variant ? bottts : notionists` union would not unify to one Style<O>).
  const result =
    variant === "agent"
      ? createAvatar(bottts, { seed })
      : createAvatar(notionists, { seed });
  return result.toString();
}

/**
 * Render a deterministic avatar as a self-contained `data:image/svg+xml` URI,
 * directly usable as an <img> src with no client JS.
 *
 * @param seed    — stable id driving the avatar
 * @param variant — "account" (default) or "agent"
 * @returns a `data:image/svg+xml,...` URI
 */
export function avatarDataUri(seed: string, variant?: AvatarVariant): string {
  return `data:image/svg+xml,${encodeURIComponent(avatarSvg(seed, variant))}`;
}
