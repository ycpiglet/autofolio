import { cn } from "@/lib/utils";

interface IllustrationProps {
  /** Rendered width/height in px (the SVG is square-ish, viewBox 0 0 200 160). Default 160. */
  size?: number;
  className?: string;
}

/**
 * NoResults — flat brand illustration for an empty search / no-matches state.
 *
 * Original CC0 artwork (authored in-repo, no external license): a magnifier
 * hovering over a short flat list, in Toss-blue (#3182F6) over neutrals.
 * Decorative only (`aria-hidden`); the surrounding EmptyState supplies the text.
 */
export function NoResults({ size = 160, className }: IllustrationProps) {
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
      {/* list card behind the lens */}
      <rect x="44" y="40" width="84" height="80" rx="10" fill="#DDE1E7" opacity="0.5" />
      <rect x="58" y="58" width="56" height="6" rx="3" fill="#8B95A1" />
      <rect x="58" y="74" width="40" height="6" rx="3" fill="#8B95A1" opacity="0.7" />
      <rect x="58" y="90" width="48" height="6" rx="3" fill="#8B95A1" opacity="0.5" />
      {/* magnifier — transparent lens (visible blue ring on any surface; white fill
          would vanish on white cards) */}
      <circle cx="120" cy="92" r="30" fill="none" />
      <circle
        cx="120"
        cy="92"
        r="30"
        stroke="#3182F6"
        strokeWidth="6"
      />
      <line
        x1="142"
        y1="114"
        x2="160"
        y2="132"
        stroke="#3182F6"
        strokeWidth="8"
        strokeLinecap="round"
      />
      {/* glint */}
      <path
        d="M110 84a14 14 0 0 1 10-7"
        stroke="#3182F6"
        strokeWidth="4"
        strokeLinecap="round"
        opacity="0.5"
      />
    </svg>
  );
}
