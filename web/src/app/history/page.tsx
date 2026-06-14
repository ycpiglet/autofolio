"use client";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";
export default function HistoryPage() {
  return (
    <AppShell>
      <EmptyState
        title="내역"
        description="거래 내역 화면은 Phase 2에서 구현됩니다."
        phase="Phase 2 예정"
      />
    </AppShell>
  );
}
