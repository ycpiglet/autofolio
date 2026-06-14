"use client";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";
export default function SettingsPage() {
  return (
    <AppShell>
      <EmptyState
        title="설정"
        description="설정 화면은 Phase 3에서 구현됩니다."
        phase="Phase 3 예정"
      />
    </AppShell>
  );
}
