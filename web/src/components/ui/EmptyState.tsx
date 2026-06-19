import * as React from "react";

import { cn } from "@/lib/utils";
import type { EmptyIllustration } from "@/lib/empty-illustration";

import { ErrorState } from "./illustrations/ErrorState";
import { NoData } from "./illustrations/NoData";
import { NoResults } from "./illustrations/NoResults";

interface EmptyStateProps {
  /** Which built-in illustration to show. Default "no-data". */
  illustration?: EmptyIllustration;
  /** Bold headline, e.g. "보유 종목이 없어요". Required. */
  title: string;
  /** Optional muted supporting line under the title. */
  description?: string;
  /** Optional call-to-action slot (e.g. a <Button>) rendered below the text. */
  action?: React.ReactNode;
  /** Illustration size in px. Default 160. */
  size?: number;
  className?: string;
}

/** name → illustration component (kept here so the key module stays React-free). */
const ILLUSTRATIONS = {
  "no-data": NoData,
  "no-results": NoResults,
  error: ErrorState,
} as const satisfies Record<
  EmptyIllustration,
  React.ComponentType<{ size?: number }>
>;

/**
 * EmptyState — a friendly, on-brand placeholder for empty lists and error
 * states (holdings / orders / results, load failures, etc.).
 *
 * Renders a centered column: a brand-colored flat illustration, a bold title,
 * an optional muted description, and an optional action slot. Purely
 * presentational and asset-agnostic — the illustration set lives in
 * `./illustrations/` and can be swapped for real unDraw/Open Doodles SVGs later.
 *
 * Server-renderable (no "use client"): no state, props, or browser APIs.
 */
export function EmptyState({
  illustration = "no-data",
  title,
  description,
  action,
  size = 160,
  className,
}: EmptyStateProps) {
  const Illustration = ILLUSTRATIONS[illustration];
  return (
    <div
      data-slot="empty-state"
      className={cn(
        "flex flex-col items-center justify-center px-6 py-12 text-center",
        className,
      )}
    >
      <Illustration size={size} />
      <p className="mt-6 text-base font-semibold text-foreground">{title}</p>
      {description ? (
        <p className="mt-1.5 max-w-sm text-sm text-muted-foreground">
          {description}
        </p>
      ) : null}
      {action ? <div className="mt-5">{action}</div> : null}
    </div>
  );
}
