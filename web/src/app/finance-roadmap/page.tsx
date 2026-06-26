// web/src/app/finance-roadmap/page.tsx
// TASK-174 — read-only finance roadmap planning preview.
// No recommendation wording, no actionable buttons, no order/risk/prod/deploy.
"use client";

import { AppShell } from "@/components/layout/AppShell";
import { FinanceRoadmapPanel } from "@/components/domain/FinanceRoadmapPanel";
import { ROADMAP_LABELS } from "@/lib/finance-roadmap-labels";

export default function FinanceRoadmapPage() {
  return (
    <AppShell>
      <div className="space-y-4">
        <h1 className="text-lg font-semibold">{ROADMAP_LABELS.pageTitle}</h1>
        <FinanceRoadmapPanel />
      </div>
    </AppShell>
  );
}
