/**
 * empty-illustration.ts — illustration keys for the EmptyState component.
 *
 * Pure module: no React, no DOM, no network. It only declares the small set of
 * named illustration kinds (and the list of them) so they can be referenced and
 * unit-tested in isolation. The EmptyState component owns the name→component
 * mapping; keeping this file React-free makes it safe to import anywhere.
 */

/** Which built-in EmptyState illustration to render. */
export type EmptyIllustration = "no-data" | "no-results" | "error";

/** All supported illustration keys, in a stable order. */
export const EMPTY_ILLUSTRATIONS: readonly EmptyIllustration[] = [
  "no-data",
  "no-results",
  "error",
];
