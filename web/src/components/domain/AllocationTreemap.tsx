// web/src/components/domain/AllocationTreemap.tsx
//
// AllocationTreemap — pure-SVG concentration treemap (no chart library).
//
// Bigger area = bigger weight; color INTENSITY also encodes weight via a
// sequential (unsigned-magnitude) ramp, so the eye reads concentration two
// ways. Renders deterministically from props, so no "use client" is needed —
// it works in both server and client components.

import { layoutTreemap, type TreemapItem } from "../../lib/treemap";
import { sequentialColor, sequentialBlues } from "../../lib/chart-palette";
import { fmtPct } from "../../lib/format";

interface AllocationTreemapProps {
  /** Holdings to plot; `value` is treated as unsigned weight/magnitude. */
  items: TreemapItem[];
  /** SVG user-space width (viewBox units). Default 320. */
  width?: number;
  /** SVG user-space height (viewBox units). Default 200. */
  height?: number;
  className?: string;
  /** Sequential color ramp (light → dark). Default `sequentialBlues`. */
  ramp?: readonly string[];
}

// Below these tile dimensions a label would overflow / clutter, so we skip it.
const MIN_LABEL_W = 44;
const MIN_LABEL_H = 26;

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

/**
 * AllocationTreemap — slice-and-dice treemap of holdings concentration.
 *
 * One `<rect>` per holding (area ∝ value, fill ∝ value via `ramp`), thin white
 * gutters between tiles, and a `<text>` label + percent-of-total inside tiles
 * large enough to fit. Empty input renders a muted placeholder.
 */
export function AllocationTreemap({
  items,
  width = 320,
  height = 200,
  className,
  ramp = sequentialBlues,
}: AllocationTreemapProps) {
  const tiles = layoutTreemap(items, width, height);

  if (tiles.length === 0) {
    return (
      <div
        className={className}
        role="img"
        aria-label="집중도 treemap: 표시할 보유 데이터 없음"
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

  // Normalizers: maxValue drives color intensity; total drives the % label.
  // Both are guarded against divide-by-zero (tiles all have value > 0 here).
  const maxValue = tiles.reduce((m, t) => Math.max(m, t.value), 0) || 1;
  const total = tiles.reduce((s, t) => s + t.value, 0) || 1;

  // Summarize the top holdings for screen readers.
  const ariaLabel =
    "보유 집중도 treemap. 상위 비중: " +
    tiles
      .slice(0, 3)
      .map((t) => `${t.label} ${fmtPct((t.value / total) * 100, false)}`)
      .join(", ");

  return (
    <svg
      className={className}
      viewBox={`0 0 ${width} ${height}`}
      width={width}
      height={height}
      role="img"
      aria-label={ariaLabel}
      data-testid="allocation-treemap"
    >
      {tiles.map((t, i) => {
        const fill = sequentialColor(t.value / maxValue, ramp);
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
                  {fmtPct((t.value / total) * 100, false)}
                </tspan>
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}

export default AllocationTreemap;
