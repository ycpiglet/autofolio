import type React from "react";
import { cn } from "@/lib/utils";
import type { EmptyIllustration } from "@/lib/empty-illustration";
import { NoData } from "@/components/ui/illustrations/NoData";
import { NoResults } from "@/components/ui/illustrations/NoResults";
import { ErrorState as ErrorIllustration } from "@/components/ui/illustrations/ErrorState";

const ILLUSTRATIONS = {
  "no-data": NoData,
  "no-results": NoResults,
  error: ErrorIllustration,
} as const satisfies Record<EmptyIllustration, React.ComponentType<{ size?: number }>>;

interface EmptyStateProps {
  /** Which built-in illustration to show. Default "no-data". */
  illustration?: EmptyIllustration;
  title?: string;
  description?: string;
  phase?: string;
  className?: string;
  /** Illustration size in px. Default 120. */
  size?: number;
}

export function EmptyState({
  illustration = "no-data",
  title = "준비 중",
  description,
  phase,
  className,
  size = 120,
}: EmptyStateProps) {
  const Illustration = ILLUSTRATIONS[illustration];
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-border p-12 text-center",
        className
      )}
      role="status"
      aria-label={title}
    >
      <Illustration size={size} />
      <h2 className="text-base font-medium text-foreground">{title}</h2>
      {description && (
        <p className="max-w-sm text-sm text-muted-foreground">{description}</p>
      )}
      {phase && (
        <span className="mt-1 rounded-full bg-muted px-3 py-1 text-xs text-muted-foreground">
          {phase}
        </span>
      )}
    </div>
  );
}
