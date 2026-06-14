/**
 * /home — 홈 대시보드 플레이스홀더 (TASK-045 Unit 2)
 *
 * Phase 2에서 KpiCard, EquityChart, HoldingsTable 등으로 채워질 예정.
 * 이 셸은 npm run build 통과를 위한 최소 구현.
 */
export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8">
      <h1 className="text-2xl font-bold" style={{ wordBreak: "keep-all" }}>
        홈 (빈 셸)
      </h1>
      <p className="text-muted-foreground text-sm">
        Phase 2에서 대시보드 컴포넌트가 여기에 추가됩니다.
      </p>
    </main>
  );
}
