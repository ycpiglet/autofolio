"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import UplotReact from "uplot-react";
import type uPlot from "uplot";
import "uplot/dist/uPlot.min.css";

import { cn } from "@/lib/utils";
import { fmtWonShort } from "../../lib/format";
import {
  equityLineColor,
  toUplotData,
  type EquityPoint,
} from "../../lib/equity-series";

interface EquityChartUplotProps {
  points: EquityPoint[];
  height?: number;
  className?: string;
}

// Neutral chart chrome (matches EquityChart.tsx + chart-palette tokens).
const AXIS_TEXT = "#8B95A1";
const GRID_LINE = "#DDE1E7";

/**
 * Low-alpha area fill derived from the (already sign-chosen) line color.
 * The three KR-convention line colors are known hex strings, so map them to a
 * matching translucent rgba; anything else falls back to a faint neutral.
 */
function fillForLine(line: string): string {
  switch (line) {
    case "#F04452": // 상승 (red)
      return "rgba(240, 68, 82, 0.12)";
    case "#3182F6": // 하락 (blue)
      return "rgba(49, 130, 246, 0.12)";
    default: // 보합 (gray)
      return "rgba(139, 149, 161, 0.10)";
  }
}

/**
 * EquityChartUplot — self-hosted uPlot equity curve (net-new alternative to
 * EquityChart.tsx). Client-only: uPlot inits its canvas in uplot-react's mount
 * effect, so this is SSR-safe as a plain "use client" component (no canvas
 * access during prerender).
 *
 * The line/area is colored by the period's sign per KR convention
 * (up=빨강 #F04452, down=파랑 #3182F6, flat=회색 #8B95A1), mirroring pnlColor.
 *
 * Width is measured from the container (ResizeObserver) for responsiveness;
 * height defaults to 240.
 */
export function EquityChartUplot({
  points,
  height = 240,
  className,
}: EquityChartUplotProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);

  // Track the container's width so uPlot can size to it (uPlot needs an
  // explicit pixel width; it does not auto-fit its parent).
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const measure = () => setWidth(el.clientWidth);
    measure();

    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const lineColor = useMemo(() => equityLineColor(points), [points]);
  const data = useMemo(
    () => toUplotData(points) as unknown as uPlot.AlignedData,
    [points],
  );

  const options = useMemo<uPlot.Options>(() => {
    return {
      width: Math.max(width, 1),
      height,
      // Minimal, clean look: no title, no inline legend, no hover legend.
      legend: { show: false },
      cursor: { show: false },
      scales: {
        x: { time: true },
        y: { auto: true },
      },
      series: [
        {}, // x (time)
        {
          label: "자산",
          stroke: lineColor,
          fill: fillForLine(lineColor),
          width: 2,
          points: { show: false },
        },
      ],
      axes: [
        {
          // x — time axis (uPlot formats unix-seconds splits by default).
          stroke: AXIS_TEXT,
          grid: { stroke: GRID_LINE, width: 1 },
          ticks: { stroke: GRID_LINE, width: 1 },
        },
        {
          // y — value axis, ticks formatted in Korean short won (₩1.2억 …).
          stroke: AXIS_TEXT,
          grid: { stroke: GRID_LINE, width: 1 },
          ticks: { stroke: GRID_LINE, width: 1 },
          values: (_self, splits) => splits.map((v) => fmtWonShort(v)),
        },
      ],
    };
  }, [width, height, lineColor]);

  if (points.length === 0) {
    return (
      <div
        className={cn(
          "flex w-full items-center justify-center rounded-xl bg-muted/40 text-sm text-muted-foreground",
          className,
        )}
        style={{ height }}
        aria-label="자산 추이 차트 (데이터 없음)"
        data-testid="equity-chart-uplot-empty"
      >
        표시할 데이터가 없습니다
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={cn("w-full rounded-xl overflow-hidden", className)}
      style={{ height }}
      aria-label="자산 추이 차트"
      data-testid="equity-chart-uplot"
    >
      {width > 0 ? (
        <UplotReact options={options} data={data} />
      ) : null}
    </div>
  );
}

export default EquityChartUplot;
