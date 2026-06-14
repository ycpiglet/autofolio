import { cn } from "@/lib/utils";

export type ModeLevel = "L0" | "L1" | "L2" | "L3" | "L4";

const MODE_LABELS: Record<ModeLevel, string> = {
  L0: "L0 모의",
  L1: "L1 보수",
  L2: "L2 균형",
  L3: "L3 적극",
  L4: "L4 공격",
};

const MODE_COLORS: Record<ModeLevel, string> = {
  L0: "bg-muted text-muted-foreground",
  L1: "bg-blue-50 text-blue-700",
  L2: "bg-green-50 text-green-700",
  L3: "bg-orange-50 text-orange-700",
  L4: "bg-red-50 text-red-700",
};

interface ModeBadgeProps {
  mode: ModeLevel;
  className?: string;
}

export function ModeBadge({ mode, className }: ModeBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        MODE_COLORS[mode],
        className
      )}
      aria-label={`운용 모드: ${MODE_LABELS[mode]}`}
    >
      {MODE_LABELS[mode]}
    </span>
  );
}
