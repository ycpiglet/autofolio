import { cn } from "@/lib/utils";

interface EmptyStateProps {
  title?: string;
  description?: string;
  phase?: string;
  className?: string;
}

export function EmptyState({
  title = "준비 중",
  description,
  phase,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-border p-12 text-center",
        className
      )}
      role="status"
      aria-label={title}
    >
      <div className="text-4xl" aria-hidden>
        🏗️
      </div>
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
