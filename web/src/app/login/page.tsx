"use client";

import { useState } from "react";
import Link from "next/link";
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

/** Owner setup guidance per provider (source: docs/EXTERNAL_APP_API_OWNER_MANUAL.md). */
const SETUP_GUIDE: Record<
  string,
  { title: string; steps: string[]; env: string[]; manual: string }
> = {
  google: {
    title: "Google 로그인 연동 설정",
    steps: [
      "Google Cloud Console에서 프로젝트를 만듭니다.",
      "API 및 서비스 → OAuth 동의 화면 설정 (User type: 외부, 테스트 사용자에 본인 Google 이메일 추가).",
      "사용자 인증 정보 → OAuth 클라이언트 ID 만들기 → 유형: 웹 애플리케이션.",
      "승인된 리디렉션 URI에 아래 콜백 주소를 정확히 등록합니다.",
      "발급된 클라이언트 ID/비밀번호를 프로젝트 루트 .env에 입력하고 API 서버를 재시작합니다.",
    ],
    env: [
      "GOOGLE_CLIENT_ID=<client id>",
      "GOOGLE_CLIENT_SECRET=<client secret>",
      "AUTOFOLIO_SSO_ALLOWED_EMAILS=<본인 이메일>  # (선택) 허용 이메일 제한",
    ],
    manual: "docs/EXTERNAL_APP_API_OWNER_MANUAL.md §3.3 Google",
  },
  kakao: {
    title: "Kakao 로그인 연동 설정",
    steps: [
      "Kakao Developers에서 앱을 만들고 Kakao Login을 ON 합니다.",
      "Redirect URI에 아래 콜백 주소를 등록합니다.",
      "REST API key(필요 시 Client secret)를 .env에 입력하고 API 서버를 재시작합니다.",
    ],
    env: [
      "KAKAO_REST_API_KEY=<rest api key>",
      "KAKAO_CLIENT_SECRET=<client secret, 사용 시>",
    ],
    manual: "docs/EXTERNAL_APP_API_OWNER_MANUAL.md §3.4 Kakao",
  },
  naver: {
    title: "Naver 로그인 연동 설정",
    steps: [
      "Naver Developers에서 애플리케이션을 등록하고 네이버 로그인을 사용 설정합니다.",
      "서비스 URL과 Callback URL에 아래 콜백 주소를 등록합니다.",
      "Client ID/Secret을 .env에 입력하고 API 서버를 재시작합니다.",
    ],
    env: [
      "NAVER_CLIENT_ID=<client id>",
      "NAVER_CLIENT_SECRET=<client secret>",
    ],
    manual: "docs/EXTERNAL_APP_API_OWNER_MANUAL.md §3.5 Naver",
  },
};

function apiErrorDetail(err: unknown): string | null {
  if (!(err instanceof ApiError)) return null;
  if (typeof err.body === "object" && err.body && "detail" in err.body) {
    const detail = (err.body as { detail?: unknown }).detail;
    return typeof detail === "string" ? detail : null;
  }
  return null;
}

function callbackUrl(providerId: string): string {
  const origin =
    typeof window !== "undefined" ? window.location.origin : "http://127.0.0.1:3000";
  return `${origin}/api/auth/sso/${providerId}/callback`;
}

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [setupProvider, setSetupProvider] = useState<SsoProviderInfo | null>(null);

  const { data: ssoData } = useQuery({
    queryKey: ["sso-providers"],
    queryFn: getSsoProviders,
    retry: false,
    staleTime: 60_000,
  });

  // Show Google · Kakao · Naver always (as shells when not configured); mock only if enabled.
  const ORDER = ["google", "kakao", "naver"];
  const allProviders = ssoData?.providers ?? [];
  const socialProviders = ORDER.map((id) => allProviders.find((p) => p.id === id)).filter(
    (p): p is SsoProviderInfo => Boolean(p),
  );
  const mockProvider = allProviders.find((p) => p.id === "mock" && p.enabled);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await apiPost<SessionResponse>("/api/auth/login", { username, password });
      router.push("/home");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError(apiErrorDetail(err) ?? "아이디 또는 비밀번호가 올바르지 않습니다.");
      } else {
        setError("로그인 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
      }
    } finally {
      setLoading(false);
    }
  }

  function handleProviderClick(provider: SsoProviderInfo) {
    if (provider.enabled) {
      window.location.assign(`/api/auth/sso/${provider.id}/login`);
    } else {
      setSetupProvider(provider); // open setup guide
    }
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
              <CardDescription>승인된 Autofolio 계정으로 로그인하세요.</CardDescription>
            </CardHeader>
            <CardContent>
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

              {/* SSO / SNS — below the regular login (always shown; shells open setup guide) */}
              <div className="mt-5 flex flex-col gap-2" aria-label="SSO SNS 로그인">
                <div className="flex items-center gap-3 py-1" aria-hidden="true">
                  <span className="h-px flex-1 bg-border" />
                  <span className="text-xs text-muted-foreground">소셜 로그인</span>
                  <span className="h-px flex-1 bg-border" />
                </div>
                {socialProviders.map((provider) => (
                  <Button
                    key={provider.id}
                    type="button"
                    variant="outline"
                    className="w-full justify-center"
                    onClick={() => handleProviderClick(provider)}
                    title={provider.enabled ? undefined : "연동 설정이 필요합니다 — 클릭하면 안내가 표시됩니다"}
                  >
                    {provider.label}로 계속하기
                    {!provider.enabled && (
                      <span className="ml-2 rounded bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground">
                        설정 필요
                      </span>
                    )}
                  </Button>
                ))}
                {mockProvider && (
                  <Button
                    type="button"
                    variant="ghost"
                    className="w-full justify-center text-muted-foreground"
                    onClick={() => handleProviderClick(mockProvider)}
                  >
                    {mockProvider.label} (개발용)
                  </Button>
                )}
                <p className="mt-1 text-[11px] leading-relaxed text-muted-foreground">
                  소셜 로그인은 각 제공자 OAuth 앱 등록(클라이언트 ID/secret·리디렉션 URI)이 필요합니다.
                  버튼을 누르면 설정 방법을 안내합니다.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Signup request card */}
          <Card className="border-dashed">
            <CardContent className="pt-4 pb-4">
              <div className="flex flex-col items-center gap-3 text-center">
                <div className="text-sm font-medium text-foreground">승인 기반 가입</div>
                <p className="text-xs text-muted-foreground">
                  검증된 사용자만 계정이 활성화됩니다.
                </p>
                <Button nativeButton={false} render={<Link href="/signup" />} className="w-full">
                  가입 승인 신청
                </Button>
              </div>
            </CardContent>
          </Card>

          <p className="text-center text-xs leading-relaxed text-muted-foreground">
            계정은 Owner가 신청자와 입금 확인을 검증한 뒤 활성화합니다.
          </p>
        </div>
      </div>

      {/* Setup guide modal (shown when an unconfigured provider is clicked) */}
      {setupProvider && (() => {
        const guide = SETUP_GUIDE[setupProvider.id] ?? {
          title: `${setupProvider.label} 연동 설정`,
          steps: ["제공자 개발자 콘솔에서 OAuth 앱을 등록하고 콜백 URI를 등록하세요."],
          env: [],
          manual: "docs/EXTERNAL_APP_API_OWNER_MANUAL.md",
        };
        return (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
            role="dialog"
            aria-modal="true"
            aria-label={guide.title}
            onClick={() => setSetupProvider(null)}
          >
            <div
              className="max-h-[85vh] w-full max-w-lg overflow-auto rounded-xl bg-surface p-6 shadow-soft"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="mb-3 flex items-start justify-between gap-4">
                <h2 className="text-lg font-bold text-foreground" style={{ wordBreak: "keep-all" }}>
                  {guide.title}
                </h2>
                <button
                  type="button"
                  onClick={() => setSetupProvider(null)}
                  className="rounded px-2 py-1 text-sm text-muted-foreground hover:bg-muted"
                  aria-label="닫기"
                >
                  ✕
                </button>
              </div>
              <p className="mb-4 text-sm text-muted-foreground leading-relaxed">
                계정 생성·콘솔 등록·secret 발급은 <strong>Owner가 직접</strong> 수행합니다.
                아래 값을 준비해 <code className="rounded bg-muted px-1">.env</code>에 넣고 API 서버를
                재시작하면 버튼이 활성화됩니다.
              </p>

              <ol className="mb-4 list-decimal space-y-1.5 pl-5 text-sm text-foreground">
                {guide.steps.map((s, i) => (
                  <li key={i} style={{ wordBreak: "keep-all" }}>{s}</li>
                ))}
              </ol>

              <div className="mb-4">
                <div className="mb-1 text-xs font-medium text-muted-foreground">승인된 리디렉션 URI</div>
                <code className="block break-all rounded-lg bg-page p-2 text-xs text-foreground">
                  {callbackUrl(setupProvider.id)}
                </code>
              </div>

              {guide.env.length > 0 && (
                <div className="mb-4">
                  <div className="mb-1 text-xs font-medium text-muted-foreground">.env 변수</div>
                  <pre className="overflow-auto rounded-lg bg-page p-2 text-xs text-foreground">
{guide.env.join("\n")}
                  </pre>
                </div>
              )}

              <p className="text-xs text-muted-foreground">
                상세 절차·주의사항: <code className="rounded bg-muted px-1">{guide.manual}</code>
              </p>
            </div>
          </div>
        );
      })()}
    </main>
  );
}
