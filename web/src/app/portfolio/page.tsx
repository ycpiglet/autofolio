// web/src/app/portfolio/page.tsx
"use client";

import { AppShell } from "@/components/layout/AppShell";
import { PortfolioDashboard } from "@/components/domain/PortfolioDashboard";

export default function PortfolioPage() {
  return (
    <AppShell>
      <PortfolioDashboard />
    </AppShell>
  );
}
