// web/src/app/alerts/page.tsx
"use client";

import { AppShell } from "@/components/layout/AppShell";
import { EventFeed } from "@/components/domain/EventFeed";

/**
 * /alerts — live event notifications feed.
 * Renders EventFeed which opens an EventSource on /api/stream/events.
 * No alert-rule creation here — that lives in the Streamlit TASK-038 layer.
 */
export default function AlertsPage() {
  return (
    <AppShell>
      <div className="space-y-4">
        <div>
          <h1 className="text-base font-semibold text-foreground">알림</h1>
          <p className="mt-0.5 text-sm text-muted-foreground">
            실시간 이벤트 피드 — 가격·엔진·주문 알림
          </p>
        </div>
        <EventFeed maxEvents={200} />
      </div>
    </AppShell>
  );
}
