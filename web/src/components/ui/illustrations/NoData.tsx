import { cn } from "@/lib/utils";

interface IllustrationProps {
  /** Rendered width/height in px (the SVG is square-ish, viewBox 0 0 200 160). Default 160. */
  size?: number;
  className?: string;
}

/**
 * NoData — flat brand illustration for an empty list / no-content state.
 *
 * Original CC0 artwork (authored in-repo, no external license): a tidy empty
 * box/tray with a flat chart baseline, in Toss-blue (#3182F6) over neutrals.
 * Decorative only (`aria-hidden`); the surrounding EmptyState supplies the text.
 */
export function NoData({ size = 160, className }: IllustrationProps) {
  return (
    <svg
      width={size}
      height={(size * 160) / 200}
      viewBox="0 0 200 160"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      className={cn("shrink-0", className)}
    >
      {/* soft backdrop */}
      <ellipse cx="100" cy="136" rx="74" ry="12" fill="#DDE1E7" opacity="0.6" />
      {/* open box body */}
      <path
        d="M48 78l52-22 52 22-52 22-52-22z"
        fill="#3182F6"
        opacity="0.18"
      />
      <path
        d="M48 78v34l52 22V100L48 78z"
        fill="#3182F6"
        opacity="0.32"
      />
      <path
        d="M152 78v34l-52 22V100l52-22z"
        fill="#3182F6"
        opacity="0.5"
      />
      <path
        d="M48 78l52-22 52 22-52 22-52-22z"
        stroke="#3182F6"
        strokeWidth="3"
        strokeLinejoin="round"
      />
      <path
        d="M48 78v34l52 22 52-22V78"
        stroke="#3182F6"
        strokeWidth="3"
        strokeLinejoin="round"
      />
      {/* flat chart baseline floating above, hinting "no data yet" */}
      <line
        x1="58"
        y1="42"
        x2="142"
        y2="42"
        stroke="#8B95A1"
        strokeWidth="3"
        strokeLinecap="round"
        strokeDasharray="2 9"
      />
      <circle cx="58" cy="42" r="4" fill="#8B95A1" />
      <circle cx="142" cy="42" r="4" fill="#8B95A1" />
    </svg>
  );
}
