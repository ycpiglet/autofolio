import { cn } from "@/lib/utils";

import { avatarDataUri, type AvatarVariant } from "../../lib/avatar";

interface AvatarProps {
  /** Stable id (userId / agentId) — deterministically drives the avatar. */
  seed: string;
  /** "account" (notionists, CC0) or "agent" (bottts). Default "account". */
  variant?: AvatarVariant;
  /** Rendered width/height in px. Default 40. */
  size?: number;
  className?: string;
  /** Accessible label. Empty (default) marks the image decorative. */
  alt?: string;
}

/**
 * Avatar — deterministic, self-hosted avatar image.
 *
 * Server-renderable (no "use client"): the SVG is generated at build/SSR time
 * and inlined as a `data:` URI, so it ships with zero client JS and no runtime
 * CDN call. See `src/lib/avatar.ts`.
 */
export function Avatar({
  seed,
  variant = "account",
  size = 40,
  className,
  alt,
}: AvatarProps) {
  return (
    // The avatar is a self-contained inline SVG data: URI (generated at
    // build/SSR, zero client JS). next/image adds a client runtime and cannot
    // optimize an inline data URI, so a plain <img> is intentional here.
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={avatarDataUri(seed, variant)}
      width={size}
      height={size}
      alt={alt ?? ""}
      aria-hidden={alt ? undefined : true}
      className={cn("rounded-full", className)}
    />
  );
}
