"use client";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";
export default function AgentsPage() {
  return (
    <AppShell>
      <EmptyState
        title="에이전트"
        description="에이전트 화면은 Phase 4에서 구현됩니다."
        phase="Phase 4 예정"
      />
    </AppShell>
  );
}
