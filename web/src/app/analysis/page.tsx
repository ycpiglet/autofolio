"use client";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";
export default function AnalysisPage() {
  return (
    <AppShell>
      <EmptyState
        title="분석"
        description="분석 화면은 Phase 5에서 구현됩니다."
        phase="Phase 5 예정"
      />
    </AppShell>
  );
}
