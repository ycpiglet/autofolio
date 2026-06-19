import { cn } from "@/lib/utils";

interface IllustrationProps {
  /** Rendered width/height in px (the SVG is square-ish, viewBox 0 0 200 160). Default 160. */
  size?: number;
  className?: string;
}

/**
 * ErrorState — flat brand illustration for a load-failed / error state.
 *
 * Original CC0 artwork (authored in-repo, no external license): a gentle,
 * rounded alert triangle in Toss-blue (#3182F6) over neutrals — friendly,
 * not alarming. Decorative only (`aria-hidden`); EmptyState supplies the text.
 */
export function ErrorState({ size = 160, className }: IllustrationProps) {
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
      {/* rounded alert triangle */}
      <path
        d="M100 34c4 0 7.7 2.1 9.7 5.5l44 76c4 6.9-1 15.5-9 15.5H55.3c-8 0-13-8.6-9-15.5l44-76C92.3 36.1 96 34 100 34z"
        fill="#3182F6"
        opacity="0.16"
      />
      <path
        d="M100 34c4 0 7.7 2.1 9.7 5.5l44 76c4 6.9-1 15.5-9 15.5H55.3c-8 0-13-8.6-9-15.5l44-76C92.3 36.1 96 34 100 34z"
        stroke="#3182F6"
        strokeWidth="4"
        strokeLinejoin="round"
      />
      {/* exclamation mark */}
      <rect x="94" y="64" width="12" height="34" rx="6" fill="#3182F6" />
      <circle cx="100" cy="114" r="7" fill="#3182F6" />
      {/* faint neutral spark accents */}
      <line
        x1="150"
        y1="52"
        x2="162"
        y2="46"
        stroke="#8B95A1"
        strokeWidth="3"
        strokeLinecap="round"
        opacity="0.6"
      />
      <line
        x1="38"
        y1="52"
        x2="26"
        y2="46"
        stroke="#8B95A1"
        strokeWidth="3"
        strokeLinecap="round"
        opacity="0.6"
      />
    </svg>
  );
}
