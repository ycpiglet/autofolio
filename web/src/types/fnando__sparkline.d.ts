/**
 * Minimal ambient types for @fnando/sparkline (v0.3.x), which ships no
 * declarations and has no @types package.
 *
 * The library draws an SVG sparkline into a provided <svg> element. The <svg>
 * MUST carry `width`, `height`, and `stroke-width` attributes — the function
 * reads them off `svg.attributes` and throws if `stroke-width` is absent.
 *
 * Only the surface this app uses is typed here (the static, non-interactive
 * path: a numeric series + an optional fetch). The interactive callbacks exist
 * upstream but are intentionally omitted since the inline cell chart is static.
 *
 * Source: node_modules/@fnando/sparkline/src/sparkline.js
 */
declare module "@fnando/sparkline" {
  export interface SparklineOptions {
    /** Map a custom entry shape to its numeric value. */
    fetch?: (entry: unknown) => number;
    /** Spot radius (default 2). */
    spotRadius?: number;
    /** Cursor width (default 2). */
    cursorWidth?: number;
    /** Enable hover cursor/spot. Defaults to false unless onmousemove is set. */
    interactive?: boolean;
  }

  /**
   * Draw a sparkline path into `svg` from `values` (an array of numbers, or
   * objects resolved via `options.fetch`). Existing children are cleared first.
   */
  export function sparkline(
    svg: SVGSVGElement,
    values: number[],
    options?: SparklineOptions,
  ): void;

  export default sparkline;
}
