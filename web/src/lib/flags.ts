/**
 * Supported flag codes — the country/region flags inlined in
 * src/components/ui/Flag.tsx (artwork from circle-flags, MIT © HatScripts).
 *
 * Keep this list in sync with the keys of FLAG_SVGS in Flag.tsx.
 */
export const FLAG_CODES = ["kr", "us", "cn", "jp", "eu"] as const;

export type FlagCode = (typeof FLAG_CODES)[number];
