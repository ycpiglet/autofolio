"use client";

import { useEffect, useRef } from "react";
import sparkline from "@fnando/sparkline";

import { cn } from "@/lib/utils";
import { sparklineTrendColor, SPARKLINE_FLAT_COLOR } from "../../lib/sparkline-util";

interface SparklineProps {
  /** The series to plot. Needs ≥ 2 points to render a line. */
  values: number[];
  /** SVG width in px (default 80). */
  width?: number;
  /** SVG height in px (default 24). */
  height?: number;
  className?: string;
  /**
   * Accessible label. When provided, the SVG gets `aria-label`; when omitted,
   * the SVG is `aria-hidden` (a purely decorative inline cell chart).
   */
  ariaLabel?: string;
}

/** Line thickness for the inline cell chart (also the SVG's stroke-width attr). */
const STROKE_WIDTH = 1.5;

/**
 * Sparkline — tiny, static, self-hosted inline cell chart for holdings-table
 * rows, drawn by @fnando/sparkline (zero-dep, ~50KB) into a single <svg>.
 *
 * @fnando/sparkline only touches `document` inside its draw function (not at
 * module import), so this is SSR-safe as a plain "use client" component and
 * needs no dynamic import (unlike CandleChartKline). The library reads
 * `width`/`height`/`stroke-width` off the <svg> attributes — all three are set
 * below; `stroke-width` is mandatory or the library throws.
 *
 * The stroke color follows KR PnL convention via sparklineTrendColor:
 * rising → 빨강 #F04452, falling → 파랑 #3182F6, flat → 회색 #8B95A1.
 *
 * The chart is non-interactive (no cursor/spot, no hover) — `interactive` is
 * left at its default (false, since no onmousemove is passed). The draw is
 * re-run whenever `values` (or the dimensions) change; @fnando/sparkline clears
 * the <svg> on each call, and we also clear on cleanup for safety.
 *
 * With fewer than 2 points there is no trend to draw, so a minimal muted
 * placeholder line renders instead.
 */
export function Sparkline({
  values,
  width = 80,
  height = 24,
  className,
  ariaLabel,
}: SparklineProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const hasSeries = values.length >= 2;

  useEffect(() => {
    const svg = svgRef.current;
    if (!svg || !hasSeries) return;

    // stroke color is set on the <svg> so the library's line <path>
    // (which it renders with fill:none and no explicit stroke) inherits it.
    svg.setAttribute("stroke", sparklineTrendColor(values));
    // @fnando/sparkline clears existing children before drawing, so this is
    // safe to re-run on every values/size change.
    sparkline(svg, values);

    return () => {
      // Clear on unmount / before the next draw so no stale path lingers.
      while (svg.firstChild) svg.removeChild(svg.firstChild);
    };
  }, [values, width, height, hasSeries]);

  // Insufficient data: render a flat muted baseline placeholder (no library call).
  if (!hasSeries) {
    return (
      <svg
        width={width}
        height={height}
        className={cn("inline-block align-middle", className)}
        aria-hidden="true"
        data-testid="sparkline-empty"
      >
        <line
          x1={2}
          y1={height / 2}
          x2={width - 2}
          y2={height / 2}
          stroke={SPARKLINE_FLAT_COLOR}
          strokeWidth={1}
          strokeDasharray="2 2"
        />
      </svg>
    );
  }

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      strokeWidth={STROKE_WIDTH}
      fill="none"
      className={cn("inline-block align-middle", className)}
      {...(ariaLabel ? { "aria-label": ariaLabel, role: "img" } : { "aria-hidden": "true" })}
      data-testid="sparkline"
    />
  );
}

export default Sparkline;
