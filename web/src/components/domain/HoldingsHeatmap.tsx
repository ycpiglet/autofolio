// web/src/components/domain/HoldingsHeatmap.tsx
//
// HoldingsHeatmap — pure-SVG "Today Gain/Loss" heatmap (Fidelity-style).
//
// Tile AREA encodes position weight (treemap layout); tile COLOR encodes
// today's PnL % on a diverging ramp (KR: red=up / blue=down, neutral midpoint).
// A ▲/▼/→ glyph + the signed percent give a non-color cue so meaning survives
// for colorblind users (WCAG 1.4.1). Renders deterministically from props, so
// no "use client" is needed — it works in server and client components.

import { layoutTreemap } from "../../lib/treemap";
import { pnlDivergingColor } from "../../lib/chart-palette";
import { maxAbs } from "../../lib/heatmap-util";
import { fmtPct } from "../../lib/format";

/** One holding: `weight` sizes the tile, `deltaPct` is today's signed % move. */
export interface HeatmapItem {
  label: string;
  weight: number;
  deltaPct: number;
}

interface HoldingsHeatmapProps {
  /** Holdings to plot. */
  items: HeatmapItem[];
  /** SVG user-space width (viewBox units). Default 320. */
  width?: number;
  /** SVG user-space height (viewBox units). Default 200. */
  height?: number;
  className?: string;
}

// Below these tile dimensions a label would overflow / clutter, so we skip it.
const MIN_LABEL_W = 48;
const MIN_LABEL_H = 30;

/**
 * Perceived luminance (0–1) of a #rrggbb hex, per the WCAG relative-luminance
 * curve. Used to choose readable text color over each tile fill.
 */
function luminance(hex: string): number {
  const m = /^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(hex);
  if (!m) return 1; // unknown → assume light → dark text
  const toLin = (h: string): number => {
    const c = parseInt(h, 16) / 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * toLin(m[1]) + 0.7152 * toLin(m[2]) + 0.0722 * toLin(m[3]);
}

/** Dark ink on light tiles, white on dark tiles (WCAG-ish 0.4 threshold). */
function textColorFor(fill: string): string {
  return luminance(fill) > 0.4 ? "#111927" : "#FFFFFF";
}

/** Direction glyph for the non-color cue (decorative; aria-hidden). */
function deltaGlyph(deltaPct: number): string {
  if (deltaPct > 0) return "▲";
  if (deltaPct < 0) return "▼";
  return "→";
}

/**
 * HoldingsHeatmap — treemap of holdings sized by weight, colored by today's PnL.
 *
 * One `<rect>` per holding (area ∝ weight, fill = diverging PnL color), thin
 * white gutters between tiles, and a `<text>` block (label, signed %, direction
 * glyph) inside tiles large enough to fit. Empty input renders a muted
 * placeholder.
 */
export function HoldingsHeatmap({
  items,
  width = 320,
  height = 200,
  className,
}: HoldingsHeatmapProps) {
  const tiles = layoutTreemap(
    items.map((i) => ({ label: i.label, value: i.weight })),
    width,
    height,
  );

  if (tiles.length === 0) {
    return (
      <div
        className={className}
        role="img"
        aria-label="오늘 손익 히트맵: 표시할 보유 데이터 없음"
        style={{
          width,
          height,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          border: "1px dashed var(--border, #d1d5db)",
          borderRadius: 12,
          color: "var(--muted-foreground, #6b7280)",
          fontSize: 13,
        }}
      >
        보유 데이터 없음
      </div>
    );
  }

  // Map label → today's % so each laid-out tile can recover its signed move.
  // (layoutTreemap sorts/filters, so we can't rely on positional alignment.)
  const deltaByLabel = new Map(items.map((i) => [i.label, i.deltaPct]));
  // Symmetric scale bound across ALL holdings (not just labeled tiles) so the
  // diverging ramp's extremes track the biggest mover in either direction.
  const scaleMax = maxAbs(items.map((i) => i.deltaPct));

  const ariaLabel = `오늘 손익 히트맵: ${tiles.length}개 종목`;

  return (
    <svg
      className={className}
      viewBox={`0 0 ${width} ${height}`}
      width={width}
      height={height}
      role="img"
      aria-label={ariaLabel}
      data-testid="holdings-heatmap"
    >
      {tiles.map((t, i) => {
        const delta = deltaByLabel.get(t.label) ?? 0;
        const fill = pnlDivergingColor(delta, scaleMax);
        const showLabel = t.w >= MIN_LABEL_W && t.h >= MIN_LABEL_H;
        const ink = textColorFor(fill);
        return (
          <g key={`${t.label}-${i}`}>
            <rect
              x={t.x}
              y={t.y}
              width={t.w}
              height={t.h}
              fill={fill}
              stroke="#FFFFFF"
              strokeWidth={1}
            />
            {showLabel && (
              <text
                x={t.x + 6}
                y={t.y + 16}
                fill={ink}
                fontSize={11}
                fontWeight={600}
              >
                <tspan x={t.x + 6} dy={0}>
                  {t.label}
                </tspan>
                <tspan x={t.x + 6} dy={13} fontWeight={400}>
                  <tspan aria-hidden="true">{deltaGlyph(delta)} </tspan>
                  {fmtPct(delta)}
                </tspan>
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}

export default HoldingsHeatmap;
