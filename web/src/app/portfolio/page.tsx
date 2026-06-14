"use client";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";
export default function PortfolioPage() {
  return (
    <AppShell>
      <EmptyState
        title="포트폴리오"
        description="포트폴리오 화면은 Phase 2에서 구현됩니다."
        phase="Phase 2 예정"
      />
    </AppShell>
  );
}
