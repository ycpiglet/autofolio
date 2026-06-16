// web/src/app/settings/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { SecretField } from "@/components/safety/SecretField";
import { ConfirmModal } from "@/components/safety/ConfirmModal";
import {
  putRiskLimits,
  getAccount,
  postPasswordChange,
  postLogout,
  ApiError,
  type AccountResponse,
} from "@/lib/api";
import { clearCsrfCache } from "@/lib/csrf";
import { cn } from "@/lib/utils";

type Tab = "risk" | "account" | "display" | "safety" | "about";

const TABS: { id: Tab; label: string }[] = [
  { id: "risk", label: "리스크 한도" },
  { id: "account", label: "계정/연결" },
  { id: "display", label: "표시" },
  { id: "safety", label: "안전" },
  { id: "about", label: "정보" },
];

// ── Risk Limits Tab ──────────────────────────────────────────────────────────

type SaveStatus =
  | { kind: "idle" }
  | { kind: "saving" }
  | { kind: "saved" }
  | { kind: "error"; message: string };

function RiskTab() {
  const [maxPositionPct, setMaxPositionPct] = useState("");
  const [maxDailyLossPct, setMaxDailyLossPct] = useState("");
  const [maxDrawdownPct, setMaxDrawdownPct] = useState("");
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>({ kind: "idle" });

  async function handleSave() {
    setSaveStatus({ kind: "saving" });
    try {
      const payload: Record<string, number> = {};
      if (maxPositionPct) payload.max_position_pct = parseFloat(maxPositionPct);
      if (maxDailyLossPct) payload.max_daily_loss_pct = parseFloat(maxDailyLossPct);
      if (maxDrawdownPct) payload.max_drawdown_pct = parseFloat(maxDrawdownPct);
      await putRiskLimits(payload);
      setSaveStatus({ kind: "saved" });
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "저장 실패";
      setSaveStatus({ kind: "error", message: msg });
    }
  }

  return (
    <div className="space-y-5 max-w-md">
      <p className="text-sm text-muted-foreground">
        리스크 한도를 초과하면 킬스위치가 자동으로 활성화됩니다. 빈 칸은 현재 값을 유지합니다.
      </p>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="max-position-pct">최대 포지션 비중 (%)</Label>
        <Input
          id="max-position-pct"
          type="number"
          min={0}
          max={100}
          step={0.1}
          placeholder="예: 20"
          value={maxPositionPct}
          onChange={(e) => setMaxPositionPct((e.target as HTMLInputElement).value)}
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="max-daily-loss-pct">일간 최대 손실 (%)</Label>
        <Input
          id="max-daily-loss-pct"
          type="number"
          min={0}
          max={100}
          step={0.1}
          placeholder="예: 5"
          value={maxDailyLossPct}
          onChange={(e) => setMaxDailyLossPct((e.target as HTMLInputElement).value)}
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="max-drawdown-pct">최대 드로우다운 (%)</Label>
        <Input
          id="max-drawdown-pct"
          type="number"
          min={0}
          max={100}
          step={0.1}
          placeholder="예: 10"
          value={maxDrawdownPct}
          onChange={(e) => setMaxDrawdownPct((e.target as HTMLInputElement).value)}
        />
      </div>

      <Button
        onClick={() => setConfirmOpen(true)}
        disabled={saveStatus.kind === "saving"}
      >
        {saveStatus.kind === "saving" ? "저장 중…" : "리스크 한도 저장"}
      </Button>

      {saveStatus.kind === "saved" && (
        <p role="status" className="text-sm text-muted-foreground">저장되었습니다.</p>
      )}
      {saveStatus.kind === "error" && (
        <p role="alert" className="text-sm text-destructive">{saveStatus.message}</p>
      )}

      <ConfirmModal
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        title="리스크 한도를 변경합니까?"
        description="리스크 한도 변경은 즉시 적용됩니다."
        confirmLabel="저장"
        onConfirm={() => { void handleSave(); }}
        dangerous
      />
    </div>
  );
}

// ── Account Tab ──────────────────────────────────────────────────────────────

const ROLE_LABELS: Record<string, string> = {
  owner: "오너",
  guest: "게스트",
};

function AccountInfo({ account }: { account: AccountResponse }) {
  return (
    <div className="space-y-2 text-sm">
      <div className="flex items-center justify-between border-b border-border py-2">
        <span className="text-muted-foreground">아이디</span>
        <span className="text-foreground">{account.username ?? "—"}</span>
      </div>
      <div className="flex items-center justify-between border-b border-border py-2">
        <span className="text-muted-foreground">권한</span>
        <Badge variant={account.is_owner ? "default" : "secondary"}>
          {ROLE_LABELS[account.role] ?? account.role}
        </Badge>
      </div>
      <div className="flex items-center justify-between py-2">
        <span className="text-muted-foreground">데이터 소스</span>
        <span className="text-foreground">{account.data_source}</span>
      </div>
    </div>
  );
}

type PwStatus =
  | { kind: "idle" }
  | { kind: "saving" }
  | { kind: "saved" }
  | { kind: "error"; message: string };

function PasswordChangeForm({ isOwner }: { isOwner: boolean }) {
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [status, setStatus] = useState<PwStatus>({ kind: "idle" });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus({ kind: "idle" });

    if (!current || !next) {
      setStatus({ kind: "error", message: "모든 항목을 입력하세요." });
      return;
    }
    if (next.length < 8) {
      setStatus({ kind: "error", message: "새 비밀번호는 최소 8자 이상이어야 합니다." });
      return;
    }
    if (next !== confirm) {
      setStatus({ kind: "error", message: "새 비밀번호가 일치하지 않습니다." });
      return;
    }
    if (next === current) {
      setStatus({ kind: "error", message: "새 비밀번호는 현재 비밀번호와 달라야 합니다." });
      return;
    }

    setStatus({ kind: "saving" });
    try {
      await postPasswordChange(current, next);
      setStatus({ kind: "saved" });
      setCurrent("");
      setNext("");
      setConfirm("");
    } catch (err) {
      let message = "비밀번호 변경에 실패했습니다.";
      if (err instanceof ApiError) {
        const detail = (err.body as { detail?: string } | undefined)?.detail;
        if (err.status === 401) {
          message = detail ?? "현재 비밀번호가 일치하지 않습니다.";
        } else if (err.status === 400) {
          message = detail ?? "새 비밀번호가 유효하지 않습니다.";
        } else if (err.status === 403) {
          message = "비밀번호를 변경할 권한이 없습니다.";
        } else if (detail) {
          message = detail;
        }
      }
      setStatus({ kind: "error", message });
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-sm font-semibold text-foreground">비밀번호 변경</h2>
      {!isOwner && (
        <p className="text-xs text-muted-foreground">
          게스트 계정은 비밀번호를 변경할 수 없습니다. 로그인 후 이용하세요.
        </p>
      )}
      <SecretField
        id="pw-current"
        label="현재 비밀번호"
        maskedPlaceholder="현재 비밀번호"
        value={current}
        onChange={setCurrent}
        disabled={!isOwner || status.kind === "saving"}
      />
      <SecretField
        id="pw-new"
        label="새 비밀번호 (최소 8자)"
        maskedPlaceholder="새 비밀번호"
        value={next}
        onChange={setNext}
        disabled={!isOwner || status.kind === "saving"}
      />
      <SecretField
        id="pw-confirm"
        label="새 비밀번호 확인"
        maskedPlaceholder="새 비밀번호 확인"
        value={confirm}
        onChange={setConfirm}
        disabled={!isOwner || status.kind === "saving"}
      />
      <Button type="submit" disabled={!isOwner || status.kind === "saving"}>
        {status.kind === "saving" ? "변경 중…" : "비밀번호 변경"}
      </Button>
      {status.kind === "saved" && (
        <p role="status" className="text-sm text-muted-foreground">
          비밀번호가 변경되었습니다.
        </p>
      )}
      {status.kind === "error" && (
        <p role="alert" className="text-sm text-destructive">
          {status.message}
        </p>
      )}
    </form>
  );
}

function SessionSection() {
  const router = useRouter();
  const [loggingOut, setLoggingOut] = useState(false);

  async function handleLogout() {
    setLoggingOut(true);
    try {
      await postLogout();
    } catch {
      // Even if the request fails, clear local state and send the user to /login.
    } finally {
      clearCsrfCache();
      router.replace("/login");
    }
  }

  return (
    <div className="space-y-3">
      <h2 className="text-sm font-semibold text-foreground">세션</h2>
      <Button variant="outline" onClick={handleLogout} disabled={loggingOut}>
        {loggingOut ? "로그아웃 중…" : "로그아웃"}
      </Button>
    </div>
  );
}

function KisKeysSection() {
  // Display-only — server secrets are NEVER fetched or echoed here.
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-semibold text-foreground">KIS API 키</h2>
      <p className="text-sm text-muted-foreground">
        KIS API 키 변경은 서버 설정 파일에서 직접 수정하세요. 여기서는 마스킹된 표시만 제공되며,
        입력하더라도 서버로 전송되지 않습니다.
      </p>
      <SecretField
        id="kis-api-key"
        label="KIS API Key"
        maskedPlaceholder="••••••••••••"
        value=""
        onChange={() => {}}
        disabled
      />
      <SecretField
        id="kis-api-secret"
        label="KIS API Secret"
        maskedPlaceholder="••••••••••••"
        value=""
        onChange={() => {}}
        disabled
      />
    </div>
  );
}

function SsoNote() {
  return (
    <div className="rounded-lg border border-dashed border-border p-4 text-sm text-muted-foreground">
      Google · Kakao · Naver SSO·SNS 연동은 추후 지원 예정입니다.
    </div>
  );
}

type AccountState =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "ready"; account: AccountResponse };

function AccountTab() {
  const [state, setState] = useState<AccountState>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    getAccount()
      .then((account) => {
        if (!cancelled) setState({ kind: "ready", account });
      })
      .catch((err) => {
        if (cancelled) return;
        const message =
          err instanceof ApiError && err.status === 401
            ? "로그인이 필요합니다."
            : "계정 정보를 불러오지 못했습니다.";
        setState({ kind: "error", message });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (state.kind === "loading") {
    return (
      <div className="space-y-5 max-w-md">
        <div className="h-24 animate-pulse rounded-lg bg-muted" />
      </div>
    );
  }

  if (state.kind === "error") {
    return (
      <div className="space-y-5 max-w-md">
        <p role="alert" className="text-sm text-destructive">
          {state.message}
        </p>
      </div>
    );
  }

  const { account } = state;

  return (
    <div className="space-y-8 max-w-md">
      <section className="space-y-3">
        <h2 className="text-sm font-semibold text-foreground">계정 정보</h2>
        <AccountInfo account={account} />
      </section>

      <section>
        <PasswordChangeForm isOwner={account.is_owner} />
      </section>

      <section>
        <SessionSection />
      </section>

      <section>
        <KisKeysSection />
      </section>

      <SsoNote />
    </div>
  );
}

// ── Display Tab ──────────────────────────────────────────────────────────────

function DisplayTab() {
  return (
    <div className="space-y-4 max-w-md">
      <p className="text-sm text-muted-foreground">
        테마 및 손익 컬러 컨벤션 설정 (준비 중)
      </p>
      <div className="rounded-lg border border-border p-4 text-sm text-muted-foreground">
        손익 표시 방식 변경은 향후 업데이트에서 지원됩니다.
      </div>
    </div>
  );
}

// ── Safety Tab ───────────────────────────────────────────────────────────────

function SafetyTab() {
  return (
    <div className="space-y-4 max-w-md">
      <p className="text-sm text-muted-foreground">
        킬스위치 및 서킷브레이커 설정. 리스크 한도는 [리스크 한도] 탭에서 변경하세요.
      </p>
      <div className="rounded-lg border border-border p-4 text-sm text-muted-foreground">
        서킷브레이커 설정은 준비 중입니다.
      </div>
    </div>
  );
}

// ── About Tab ────────────────────────────────────────────────────────────────

function AboutTab() {
  return (
    <div className="space-y-2 max-w-md text-sm">
      <div className="flex justify-between border-b border-border py-2">
        <span className="text-muted-foreground">앱</span>
        <span className="text-foreground">Autofolio</span>
      </div>
      <div className="flex justify-between border-b border-border py-2">
        <span className="text-muted-foreground">프론트엔드</span>
        <span className="text-foreground">Next.js 16 / React 19</span>
      </div>
      <div className="flex justify-between py-2">
        <span className="text-muted-foreground">백엔드</span>
        <span className="text-foreground">FastAPI / Python</span>
      </div>
    </div>
  );
}

// ── Settings page ────────────────────────────────────────────────────────────

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<Tab>("risk");

  return (
    <AppShell>
      <div className="space-y-6">
        <h1 className="text-base font-semibold text-foreground">설정</h1>

        {/* Tab bar */}
        <div
          role="tablist"
          aria-label="설정 탭"
          className="flex gap-1 border-b border-border"
        >
          {TABS.map(({ id, label }) => (
            <button
              key={id}
              role="tab"
              aria-selected={activeTab === id}
              aria-controls={`settings-panel-${id}`}
              id={`settings-tab-${id}`}
              onClick={() => setActiveTab(id)}
              className={cn(
                "px-4 py-2 text-sm font-medium transition-colors",
                activeTab === id
                  ? "border-b-2 border-primary text-foreground"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Tab panels */}
        {TABS.map(({ id }) => (
          <div
            key={id}
            role="tabpanel"
            id={`settings-panel-${id}`}
            aria-labelledby={`settings-tab-${id}`}
            hidden={activeTab !== id}
          >
            {activeTab === id && (
              <>
                {id === "risk" && <RiskTab />}
                {id === "account" && <AccountTab />}
                {id === "display" && <DisplayTab />}
                {id === "safety" && <SafetyTab />}
                {id === "about" && <AboutTab />}
              </>
            )}
          </div>
        ))}
      </div>
    </AppShell>
  );
}
