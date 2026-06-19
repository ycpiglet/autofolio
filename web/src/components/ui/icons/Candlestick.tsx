import type { SVGProps } from "react";

export interface CandlestickProps extends SVGProps<SVGSVGElement> {
  /** Pixel size for both width and height. Defaults to 24 (Lucide convention). */
  size?: number;
  className?: string;
}

/**
 * Candlestick — OHLC candlestick-chart glyph in the lucide-react outline style.
 *
 * Hand-authored: lucide-react has line/area/bar chart icons but no candlestick.
 * Matches Lucide defaults: 24×24 viewBox, stroke="currentColor", strokeWidth 2,
 * round linecap/linejoin, fill="none". Renders three candles, each with a wick
 * (the vertical line) running through a rectangular body.
 */
export function Candlestick({ size = 24, className, ...props }: CandlestickProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={["lucide", className].filter(Boolean).join(" ")}
      aria-hidden="true"
      {...props}
    >
      {/* candle 1 (left): wick + body */}
      <path d="M6 3v3" />
      <path d="M6 14v3" />
      <rect x="4" y="6" width="4" height="8" rx="1" />
      {/* candle 2 (middle): taller wick, shorter body */}
      <path d="M12 2v4" />
      <path d="M12 13v4" />
      <rect x="10" y="6" width="4" height="7" rx="1" />
      {/* candle 3 (right): wick + body */}
      <path d="M18 5v3" />
      <path d="M18 16v3" />
      <rect x="16" y="8" width="4" height="8" rx="1" />
    </svg>
  );
}

export default Candlestick;
