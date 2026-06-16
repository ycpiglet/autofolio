"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { apiPost, ApiError, getSsoProviders, type SsoProviderInfo } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";

interface SessionResponse {
  role: string;
  username: string | null;
  data_source: string;
}

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [guestLoading, setGuestLoading] = useState(false);
  const { data: ssoData } = useQuery({
    queryKey: ["sso-providers"],
    queryFn: getSsoProviders,
    retry: false,
    staleTime: 60_000,
  });
  const enabledProviders = (ssoData?.providers ?? []).filter((p) => p.enabled);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await apiPost<SessionResponse>("/api/auth/login", { username, password });
      router.push("/home");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError("아이디 또는 비밀번호가 올바르지 않습니다.");
      } else {
        setError("로그인 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleGuest() {
    setError(null);
    setGuestLoading(true);
    try {
      await apiPost<SessionResponse>("/api/auth/login", { guest: true });
      router.push("/home");
    } catch {
      setError("게스트 로그인 중 오류가 발생했습니다.");
    } finally {
      setGuestLoading(false);
    }
  }

  function handleSso(provider: SsoProviderInfo) {
    window.location.assign(`/api/auth/sso/${provider.id}/login`);
  }

  return (
    <main className="flex min-h-screen bg-page">
      {/* Left brand zone — 55% */}
      <div className="animate-fade-rise hidden lg:flex lg:w-[55%] flex-col justify-center gap-8 bg-brand/5 px-12 py-16">
        <div className="flex flex-col gap-4 max-w-md">
          <div className="text-3xl font-bold text-foreground leading-tight" style={{ wordBreak: "keep-all" }}>
            투자는 에이전트 팀에게,<br />결정은 나에게.
          </div>
          <p className="text-muted-foreground text-sm leading-relaxed">
            AI 에이전트가 시장을 분석하고 조건을 제안합니다.<br />
            실제 주문은 당신의 확인 후 실행됩니다.
          </p>
        </div>

        {/* Static demo preview card */}
        <div className="max-w-md rounded-xl bg-surface shadow-soft p-5 flex flex-col gap-4">
          <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            포트폴리오 미리보기 (데모)
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col gap-1 rounded-lg bg-page p-3">
              <span className="text-xs text-muted-foreground">총 평가금액</span>
              <span className="kpi text-foreground">₩12,543,000</span>
            </div>
            <div className="flex flex-col gap-1 rounded-lg bg-page p-3">
              <span className="text-xs text-muted-foreground">오늘 손익</span>
              <span className="kpi text-pnl-up">+₩123,400</span>
            </div>
            <div className="flex flex-col gap-1 rounded-lg bg-page p-3">
              <span className="text-xs text-muted-foreground">수익률</span>
              <span className="kpi text-pnl-up">+0.99%</span>
            </div>
            <div className="flex flex-col gap-1 rounded-lg bg-page p-3">
              <span className="text-xs text-muted-foreground">보유 종목</span>
              <span className="kpi text-foreground">4</span>
            </div>
          </div>
          <div className="flex flex-col gap-1.5">
            {[
              { name: "삼성전자", pct: "+1.2%", up: true },
              { name: "SK하이닉스", pct: "+2.8%", up: true },
              { name: "NAVER", pct: "-0.4%", up: false },
            ].map((row) => (
              <div
                key={row.name}
                className="flex items-center justify-between rounded-md px-2 py-1.5 text-sm hover:bg-muted"
              >
                <span className="text-foreground">{row.name}</span>
                <span className={row.up ? "text-pnl-up" : "text-pnl-down"}>
                  {row.pct}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Safety strip */}
        <div className="max-w-md rounded-xl border border-border bg-surface px-4 py-3">
          <p className="text-sm text-muted-foreground">
            🛡️ 모의투자 기본 &middot; 자동매매 기본 OFF &middot; 킬스위치 상시
          </p>
        </div>
      </div>

      {/* Right auth zone — 45% */}
      <div className="animate-fade-rise flex w-full lg:w-[45%] flex-col items-center justify-center px-6 py-12 lg:px-12"
           style={{ animationDelay: "60ms" }}>
        <div className="w-full max-w-sm flex flex-col gap-6">
          {/* Mobile headline */}
          <div className="lg:hidden text-center">
            <div className="text-xl font-bold text-foreground" style={{ wordBreak: "keep-all" }}>
              투자는 에이전트 팀에게,<br />결정은 나에게.
            </div>
          </div>

          {/* ID/PW form */}
          <Card>
            <CardHeader>
              <CardTitle>로그인</CardTitle>
              <CardDescription>Autofolio 계정으로 로그인하세요.</CardDescription>
            </CardHeader>
            <CardContent>
              {enabledProviders.length > 0 && (
                <div className="mb-4 flex flex-col gap-2" aria-label="SSO SNS 로그인">
                  {enabledProviders.map((provider) => (
                    <Button
                      key={provider.id}
                      type="button"
                      variant="outline"
                      className="w-full"
                      onClick={() => handleSso(provider)}
                    >
                      {provider.label}로 계속하기
                    </Button>
                  ))}
                  <div className="flex items-center gap-3 py-1" aria-hidden="true">
                    <span className="h-px flex-1 bg-border" />
                    <span className="text-xs text-muted-foreground">또는</span>
                    <span className="h-px flex-1 bg-border" />
                  </div>
                </div>
              )}

              <form onSubmit={handleLogin} noValidate className="flex flex-col gap-4">
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="username">아이디</Label>
                  <Input
                    id="username"
                    type="text"
                    autoComplete="username"
                    placeholder="아이디 입력"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    aria-required="true"
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="password">비밀번호</Label>
                  <Input
                    id="password"
                    type="password"
                    autoComplete="current-password"
                    placeholder="비밀번호 입력"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    aria-required="true"
                  />
                </div>
                {error && (
                  <p role="alert" className="text-sm text-destructive">
                    {error}
                  </p>
                )}
                <Button
                  type="submit"
                  className="w-full"
                  disabled={loading}
                  aria-busy={loading}
                >
                  {loading ? "로그인 중…" : "로그인"}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Guest card */}
          <Card className="border-dashed">
            <CardContent className="pt-4 pb-4">
              <div className="flex flex-col items-center gap-3 text-center">
                <div className="text-sm font-medium text-foreground">
                  로그인 없이 둘러보기
                </div>
                <p className="text-xs text-muted-foreground">
                  데모 데이터로 Autofolio를 체험해보세요.
                </p>
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={handleGuest}
                  disabled={guestLoading}
                  aria-busy={guestLoading}
                >
                  {guestLoading ? "연결 중…" : "게스트 데모 시작"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}
