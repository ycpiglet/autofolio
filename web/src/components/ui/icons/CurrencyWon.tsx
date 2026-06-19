import type { SVGProps } from "react";

export interface CurrencyWonProps extends SVGProps<SVGSVGElement> {
  /** Pixel size for both width and height. Defaults to 24 (Lucide convention). */
  size?: number;
  className?: string;
}

/**
 * CurrencyWon — Korean Won (₩) glyph in the lucide-react outline style.
 *
 * Hand-authored because lucide-react ships dollar/euro/yen/pound/etc. but not won.
 * Matches Lucide defaults: 24×24 viewBox, stroke="currentColor", strokeWidth 2,
 * round linecap/linejoin, fill="none". The double horizontal bar (the diacritic
 * that distinguishes ₩ from a plain W) sits over a W-shaped stem.
 */
export function CurrencyWon({ size = 24, className, ...props }: CurrencyWonProps) {
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
      {/* W-shaped legs: outer-left -> inner-low -> middle-peak -> inner-low -> outer-right */}
      <path d="M4 5l3.2 14L12 8l4.8 11L20 5" />
      {/* double horizontal bar of the won mark */}
      <path d="M3 9.5h18" />
      <path d="M3 13.5h18" />
    </svg>
  );
}

export default CurrencyWon;
