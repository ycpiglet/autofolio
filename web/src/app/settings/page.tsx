// web/src/app/settings/page.tsx
"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { SecretField } from "@/components/safety/SecretField";
import { ConfirmModal } from "@/components/safety/ConfirmModal";
import { putRiskLimits, ApiError } from "@/lib/api";
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

function AccountTab() {
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");

  return (
    <div className="space-y-5 max-w-md">
      <p className="text-sm text-muted-foreground">
        KIS API 키 변경은 서버 설정 파일에서 직접 수정하세요. 여기서는 마스킹된 현재 상태만 표시됩니다.
      </p>
      <SecretField
        id="kis-api-key"
        label="KIS API Key"
        maskedPlaceholder="••••••••••••"
        value={apiKey}
        onChange={setApiKey}
      />
      <SecretField
        id="kis-api-secret"
        label="KIS API Secret"
        maskedPlaceholder="••••••••••••"
        value={apiSecret}
        onChange={setApiSecret}
      />
      <p className="text-xs text-muted-foreground">
        입력하더라도 서버로 전송되지 않습니다. 이 탭은 준비 중입니다.
      </p>
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
