/**
 * /login — 로그인 플레이스홀더 (TASK-045 Unit 2)
 *
 * Phase 1 Unit 3에서 §4.4 스펙(55:45 레이아웃, Google CTA 등)으로 대체 예정.
 * 이 셸은 npm run build 통과를 위한 최소 구현.
 */
import Link from "next/link";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-8">
      <h1 className="text-2xl font-bold" style={{ wordBreak: "keep-all" }}>
        Autofolio 로그인
      </h1>
      <p className="text-muted-foreground text-sm">
        투자는 에이전트 팀에게, 결정은 나에게.
      </p>
      <Link
        href="/home"
        className="rounded-lg bg-primary px-6 py-2 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
      >
        게스트로 둘러보기
      </Link>
    </main>
  );
}
