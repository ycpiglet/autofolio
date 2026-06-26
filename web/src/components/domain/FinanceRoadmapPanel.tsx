"use client";

/**
 * FinanceRoadmapPanel — read-only finance roadmap planning preview.
 *
 * GATE (TASK-174):
 * - Read-only display only. No actionable buttons.
 * - No recommendation, advice, order, or action wording.
 * - Auth-gated: data query enabled only after isAuthenticated.
 * - as_of="fixture_static" is rendered as a synthetic-preview label, not a date.
 */

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useAuthSession, isUnauthorized } from "@/hooks/useAuthSession";
import {
  getFinanceRoadmap,
  type FinanceRoadmapResponse,
} from "@/lib/api";
import { fmtPct } from "@/lib/format";
import { EmptyState } from "@/components/safety/EmptyState";
import { ROADMAP_LABELS } from "@/lib/finance-roadmap-labels";

export function FinanceRoadmapPanel() {
  const router = useRouter();
  const {
    isAuthenticated,
    isPending: isAuthPending,
    isAuthError,
    authError,
  } = useAuthSession();

  useEffect(() => {
    if (isAuthError && isUnauthorized(authError)) {
      router.replace("/login");
    }
  }, [isAuthError, authError, router]);

  const roadmapQuery = useQuery<FinanceRoadmapResponse>({
    queryKey: ["finance-roadmap-goal-gap"],
    queryFn: getFinanceRoadmap,
    staleTime: 5 * 60_000,
    enabled: isAuthenticated,
  });

  if (isAuthPending) {
    return (
      <div className="flex min-h-[200px] items-center justify-center">
        <div
          className="h-6 w-6 animate-pulse rounded-full bg-muted"
          aria-label={ROADMAP_LABELS.authPendingText}
        />
      </div>
    );
  }

  if (isAuthError && !isUnauthorized(authError)) {
    return (
      <EmptyState
        illustration="error"
        title={ROADMAP_LABELS.errorTitle}
        description={(authError as Error)?.message ?? ROADMAP_LABELS.errorTitle}
      />
    );
  }

  if (roadmapQuery.isPending) {
    return (
      <div
        className="flex min-h-[200px] items-center justify-center text-sm text-muted-foreground"
        aria-label={ROADMAP_LABELS.loadingText}
      >
        {ROADMAP_LABELS.loadingText}
      </div>
    );
  }

  if (roadmapQuery.isError) {
    return (
      <EmptyState
        illustration="error"
        title={ROADMAP_LABELS.errorTitle}
        description={(roadmapQuery.error as Error)?.message ?? ROADMAP_LABELS.errorTitle}
      />
    );
  }

  const data = roadmapQuery.data;
  if (!data) return null;

  return (
    <div className="space-y-6" data-testid="finance-roadmap-panel">
      {/* ── Preview badge ──────────────────────────────────────────────── */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <span
          className="inline-flex w-fit items-center rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800 dark:bg-amber-900/30 dark:text-amber-200"
          data-testid="preview-badge"
        >
          {data.as_of === "fixture_static" ? ROADMAP_LABELS.previewBadge : data.as_of}
        </span>
        <p className="max-w-prose text-xs text-muted-foreground">
          {ROADMAP_LABELS.previewNote}
        </p>
      </div>

      {/* ── Plan vs Expected ───────────────────────────────────────────── */}
      <section
        aria-label={ROADMAP_LABELS.sectionPlanVsExpected}
        data-testid="plan-vs-expected"
        className="rounded-xl border border-border bg-surface p-4 sm:p-5"
      >
        <h2 className="mb-3 text-sm font-medium text-muted-foreground">
          {ROADMAP_LABELS.sectionPlanVsExpected}
        </h2>
        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="flex flex-col gap-0.5">
            <dt className="text-xs text-muted-foreground">
              {ROADMAP_LABELS.labelPlanned}
            </dt>
            <dd
              className="text-lg font-semibold text-foreground"
              data-testid="planned-return"
            >
              {fmtPct(data.planned.planned_return_pct)}
            </dd>
          </div>
          <div className="flex flex-col gap-0.5">
            <dt className="text-xs text-muted-foreground">
              {ROADMAP_LABELS.labelExpectedRange}
            </dt>
            <dd
              className="text-lg font-semibold text-foreground"
              data-testid="expected-range"
            >
              {fmtPct(data.expected.low_pct)} ~ {fmtPct(data.expected.high_pct)}
            </dd>
          </div>
          <div className="flex flex-col gap-0.5">
            <dt className="text-xs text-muted-foreground">
              {ROADMAP_LABELS.labelConfidence}
            </dt>
            <dd className="text-base text-foreground">
              {data.expected.confidence}
            </dd>
          </div>
          <div className="flex flex-col gap-0.5">
            <dt className="text-xs text-muted-foreground">
              {ROADMAP_LABELS.labelHorizon}
            </dt>
            <dd className="text-base text-foreground">
              {data.planned.planning_horizon}
            </dd>
          </div>
        </dl>
        <p className="mt-3 text-xs text-muted-foreground">
          {ROADMAP_LABELS.notGuaranteedNote}
        </p>
      </section>

      {/* ── Gap Matrix ─────────────────────────────────────────────────── */}
      <section
        aria-label={ROADMAP_LABELS.sectionGap}
        data-testid="gap-matrix"
        className="rounded-xl border border-border bg-surface p-4 sm:p-5"
      >
        <h2 className="mb-3 text-sm font-medium text-muted-foreground">
          {ROADMAP_LABELS.sectionGap}
        </h2>
        <dl className="grid grid-cols-2 gap-4">
          <div className="flex flex-col gap-0.5">
            <dt className="text-xs text-muted-foreground">
              {ROADMAP_LABELS.labelGapLow}
            </dt>
            <dd
              className="text-lg font-semibold text-foreground"
              data-testid="gap-low"
            >
              {fmtPct(data.gap.low_pct_points)}
            </dd>
          </div>
          <div className="flex flex-col gap-0.5">
            <dt className="text-xs text-muted-foreground">
              {ROADMAP_LABELS.labelGapHigh}
            </dt>
            <dd
              className="text-lg font-semibold text-foreground"
              data-testid="gap-high"
            >
              {fmtPct(data.gap.high_pct_points)}
            </dd>
          </div>
        </dl>
        <p className="mt-2 text-xs text-muted-foreground">
          {ROADMAP_LABELS.sectionAllocationDrift}:{" "}
          <span className="font-medium">{data.allocation_drift}</span>
        </p>
      </section>

      {/* ── Timeline Candidates ────────────────────────────────────────── */}
      {data.timeline_candidates.length > 0 && (
        <section
          aria-label={ROADMAP_LABELS.sectionTimeline}
          data-testid="timeline-candidates"
          className="rounded-xl border border-border bg-surface p-4 sm:p-5"
        >
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">
            {ROADMAP_LABELS.sectionTimeline}
          </h2>
          <ul className="flex flex-col gap-4" role="list">
            {data.timeline_candidates.map((tc) => (
              <li
                key={tc.id}
                className="flex flex-col gap-2 rounded-lg border border-border p-3"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs text-foreground">
                    {tc.id}
                  </span>
                  <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                    {ROADMAP_LABELS.tagCandidateOnly}
                  </span>
                  <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-700 dark:bg-amber-900/20 dark:text-amber-300">
                    {ROADMAP_LABELS.tagBlockedAction}
                  </span>
                </div>
                <dl className="grid grid-cols-1 gap-2 text-sm sm:grid-cols-2">
                  <div>
                    <dt className="text-xs text-muted-foreground">
                      {ROADMAP_LABELS.labelHorizonItem}
                    </dt>
                    <dd>{tc.horizon}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-muted-foreground">
                      {ROADMAP_LABELS.labelTrigger}
                    </dt>
                    <dd>{tc.trigger}</dd>
                  </div>
                </dl>
                {tc.required_evidence.length > 0 && (
                  <div>
                    <p className="text-xs text-muted-foreground">
                      {ROADMAP_LABELS.labelRequiredEvidence}
                    </p>
                    <ul className="mt-1 flex flex-wrap gap-1" role="list">
                      {tc.required_evidence.map((ev, i) => (
                        <li
                          key={i}
                          className="rounded-md bg-muted px-2 py-0.5 text-xs text-muted-foreground"
                        >
                          {ev}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* ── Review Candidates ──────────────────────────────────────────── */}
      {data.review_candidates.length > 0 && (
        <section
          aria-label={ROADMAP_LABELS.sectionReview}
          data-testid="review-candidates"
          className="rounded-xl border border-border bg-surface p-4 sm:p-5"
        >
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">
            {ROADMAP_LABELS.sectionReview}
          </h2>
          <ul className="flex flex-col gap-4" role="list">
            {data.review_candidates.map((rc) => (
              <li
                key={rc.id}
                className="flex flex-col gap-2 rounded-lg border border-border p-3"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs text-foreground">
                    {rc.id}
                  </span>
                  <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                    {ROADMAP_LABELS.tagCandidateOnly}
                  </span>
                  <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                    {ROADMAP_LABELS.tagNoTradeInstruction}
                  </span>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">
                    {ROADMAP_LABELS.labelWhyFlagged}
                  </p>
                  <p className="mt-0.5 text-sm text-foreground">
                    {rc.why_flagged}
                  </p>
                </div>
                {rc.missing_evidence.length > 0 && (
                  <div>
                    <p className="text-xs text-muted-foreground">
                      {ROADMAP_LABELS.labelMissingEvidence}
                    </p>
                    <ul className="mt-1 flex flex-wrap gap-1" role="list">
                      {rc.missing_evidence.map((ev, i) => (
                        <li
                          key={i}
                          className="rounded-md bg-muted px-2 py-0.5 text-xs text-muted-foreground"
                        >
                          {ev}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* ── Operations Support Gaps ────────────────────────────────────── */}
      {data.data_quality_flags.length > 0 && (
        <section
          aria-label={ROADMAP_LABELS.sectionDataQuality}
          data-testid="data-quality-flags"
          className="rounded-xl border border-border bg-surface p-4 sm:p-5"
        >
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">
            {ROADMAP_LABELS.sectionDataQuality}
          </h2>
          <ul className="flex flex-col gap-2" role="list">
            {data.data_quality_flags.map((flag) => (
              <li
                key={flag.id}
                className="flex flex-wrap items-center gap-2 rounded-lg border border-border p-3"
              >
                <span className="text-sm text-foreground">{flag.id}</span>
                {flag.owner_decision_required && (
                  <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-700 dark:bg-amber-900/20 dark:text-amber-300">
                    {ROADMAP_LABELS.tagOwnerDecision}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* ── Boundary note ──────────────────────────────────────────────── */}
      <p className="rounded-lg border border-border bg-muted/40 p-3 text-xs text-muted-foreground">
        {ROADMAP_LABELS.boundaryNote}
      </p>
    </div>
  );
}
