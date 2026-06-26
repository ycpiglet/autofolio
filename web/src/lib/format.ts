/**
 * format.ts — number/currency/PnL formatting for Autofolio
 *
 * Ported from app/ui/theme.py (Python):
 *   fmt_won(), fmt_pct(), pnl_color()
 *
 * KR convention (default): 상승=빨강(red), 하락=파랑(blue)
 * Western convention:       상승=초록(green), 하락=빨강(red)
 *
 * The active convention is controlled by the `data-pnl` attribute on <html>:
 *   - default / absent  → KR  (pnl-up=red, pnl-down=blue)
 *   - data-pnl="western" → Western (pnl-up=green, pnl-down=red)
 *
 * CSS utility classes `.text-pnl-up` and `.text-pnl-down` automatically
 * track the toggle via CSS variables defined in globals.css.
 */

import { pnlColorTokens } from "./design-tokens.ts";

// ── Currency ───────────────────────────────────────────────────────────────

/** Format a KRW amount: ₩1,234,567 */
export function fmtWon(value: number): string {
  return `₩${Math.round(value).toLocaleString("ko-KR")}`;
}

/** Format a USD amount: $1,234.56 */
export function fmtUsd(value: number, decimals = 2): string {
  return `$${value.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}`;
}

/**
 * Format a KRW amount in Korean short form (Toss-style 만/억):
 *   ₩1.2만 · ₩1,234.6만 · ₩1.2억 · ₩12.3억
 * Unit boundary is literal: ≥ 1억 (1e8) → 억, ≥ 1만 (1e4) → 만, else plain won.
 * Uses ko-KR grouping so large 만 values stay comma-separated ("1,234.6만").
 * Negative values render as "₩-9.9만" (₩, then sign), matching fmtWon.
 * @param value    — KRW amount
 * @param decimals — max fraction digits in the 만/억 part (default 1)
 */
export function fmtWonShort(value: number, decimals = 1): string {
  const n = Math.abs(value);
  const sign = value < 0 ? "-" : "";
  let core: string;
  if (n >= 1e8) {
    core = `${(n / 1e8).toLocaleString("ko-KR", { maximumFractionDigits: decimals })}억`;
  } else if (n >= 1e4) {
    core = `${(n / 1e4).toLocaleString("ko-KR", { maximumFractionDigits: decimals })}만`;
  } else {
    core = Math.round(n).toLocaleString("ko-KR");
  }
  return `₩${sign}${core}`;
}

/**
 * Like fmtWonShort but with an explicit leading sign for nonzero values,
 * reading as a signed delta: "+₩1.2억", "-₩9.9만", "₩0".
 * (Sign BEFORE the ₩, unlike fmtWonShort.)
 * @param value    — KRW delta
 * @param decimals — max fraction digits in the 만/억 part (default 1)
 */
export function fmtWonShortSigned(value: number, decimals = 1): string {
  if (value === 0) return "₩0";
  const sign = value > 0 ? "+" : "-";
  return `${sign}${fmtWonShort(Math.abs(value), decimals)}`;
}

// ── Percentage ─────────────────────────────────────────────────────────────

/**
 * Format a percentage value with optional sign prefix.
 * @param value  — e.g. 3.14 → "+3.14%"  (matches Python fmt_pct)
 * @param signed — prepend "+" for positive values (default true)
 * @param decimals — decimal places (default 2)
 */
export function fmtPct(value: number, signed = true, decimals = 2): string {
  const sign = signed && value > 0 ? "+" : "";
  return `${sign}${value.toFixed(decimals)}%`;
}

// ── PnL color ──────────────────────────────────────────────────────────────

/**
 * Returns the appropriate Tailwind utility class for a PnL value,
 * reading the current convention from the html[data-pnl] attribute.
 *
 * Usage (in a React component):
 *   <span className={pnlColorClass(change)}>{fmtPct(change)}</span>
 *
 * Note: CSS vars in globals.css handle the actual color toggle —
 * `.text-pnl-up` / `.text-pnl-down` resolve correctly in both modes.
 */
export function pnlColorClass(value: number): string {
  if (value > 0) return "text-pnl-up";
  if (value < 0) return "text-pnl-down";
  return "text-muted-foreground";
}

/**
 * Returns the raw CSS color string for a PnL value.
 * Reads html[data-pnl] to determine KR vs Western convention.
 * Use this only when a Tailwind class is not sufficient (e.g. chart colors).
 *
 * Only callable in browser context (reads document).
 */
export function pnlColor(value: number): string {
  if (typeof document === "undefined") {
    // SSR fallback — return KR defaults
    if (value > 0) return pnlColorTokens.kr.up;
    if (value < 0) return pnlColorTokens.kr.down;
    return pnlColorTokens.flat;
  }

  const isWestern =
    document.documentElement.getAttribute("data-pnl") === "western";

  if (value > 0) return isWestern ? pnlColorTokens.western.up : pnlColorTokens.kr.up;
  if (value < 0) return isWestern ? pnlColorTokens.western.down : pnlColorTokens.kr.down;
  return pnlColorTokens.flat;
}

// ── Tabular numbers ────────────────────────────────────────────────────────

/**
 * Format a number for tabular display (integer with thousands separator).
 * Used in KPI cards and tables where column alignment matters.
 */
export function fmtTabular(value: number, decimals = 0): string {
  return value.toLocaleString("ko-KR", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

// ── Convenience re-exports ─────────────────────────────────────────────────

/** Format PnL value as "₩1,234,567 (+3.14%)" */
export function fmtPnlWon(value: number, pct: number): string {
  return `${fmtWon(value)} (${fmtPct(pct)})`;
}

// ── Symbol label ───────────────────────────────────────────────────────────

/**
 * Format a symbol code with its name from a symbol map.
 * Returns "삼성전자 (005930)" if name exists, or "005930" if not in map.
 */
export function symbolLabel(code: string, map: Record<string, string>): string {
  const name = map[code];
  return name ? `${name} (${code})` : code;
}
