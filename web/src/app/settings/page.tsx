// web/src/app/settings/page.tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
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
  getIntegrations,
  getInvestorProfile,
  getMembershipReadiness,
  getMembershipRequests,
  getSsoProviders,
  deleteIntegrationCredential,
  postMembershipDepositRecognition,
  postMembershipTransition,
  postProfileCheckin,
  postPasswordChange,
  postLogout,
  putIntegrationCredential,
  ApiError,
  type AccountResponse,
  type IntegrationCredentialResponse,
  type IntegrationProviderInfo,
  type IntegrationSettingsResponse,
  type InvestorProfileResponse,
  type MembershipDepositMatchResponse,
  type MembershipReadinessResponse,
  type MembershipRequestResponse,
  type MembershipStatus,
  type ProfileCheckinPayload,
  type SsoProviderInfo,
} from "@/lib/api";
import { clearCsrfCache } from "@/lib/csrf";
import { cn } from "@/lib/utils";

type Tab = "risk" | "profile" | "membership" | "account" | "display" | "safety" | "about";

const TABS: { id: Tab; label: string }[] = [
  { id: "risk", label: "리스크 한도" },
  { id: "profile", label: "투자 프로필" },
  { id: "membership", label: "회원 승인" },
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

// ── Investor Profile Tab ─────────────────────────────────────────────────────

type ProfileState =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "ready"; profile: InvestorProfileResponse };

type CheckinStatus =
  | { kind: "idle" }
  | { kind: "saving" }
  | { kind: "saved" }
  | { kind: "error"; message: string };

function ProfileTab() {
  const [state, setState] = useState<ProfileState>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    getInvestorProfile()
      .then((profile) => {
        if (!cancelled) setState({ kind: "ready", profile });
      })
      .catch(() => {
        if (!cancelled) {
          setState({ kind: "error", message: "투자 프로필을 불러오지 못했습니다." });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (state.kind === "loading") {
    return <div className="h-28 max-w-md animate-pulse rounded-lg bg-muted" />;
  }

  if (state.kind === "error") {
    return (
      <p role="alert" className="max-w-md text-sm text-destructive">
        {state.message}
      </p>
    );
  }

  const { profile } = state;

  if (!profile.completed) {
    return (
      <div className="space-y-4 max-w-md">
        <p className="text-sm text-muted-foreground">
          투자 프로필을 완료하면 제안과 자동화 경고가 성향에 맞게 조정됩니다.
        </p>
        <Button nativeButton={false} render={<Link href="/onboarding/investor-profile" />}>
          투자 프로필 작성
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-xl">
      <div className="grid gap-3 sm:grid-cols-2">
        <ProfileMetric label="성향" value={profile.risk_type} />
        <ProfileMetric label="지식수준" value={profile.knowledge_level} />
        <ProfileMetric label="권장 투자율 상한" value={`${profile.recommended_max_equity_pct}%`} />
        <ProfileMetric label="권장 자동화" value={profile.recommended_autonomy_level} />
      </div>

      <div className="rounded-lg border border-border p-4">
        <h2 className="mb-3 text-sm font-semibold text-foreground">만족 기준</h2>
        <div className="flex flex-wrap gap-2">
          {profile.satisfaction_focus.length > 0 ? (
            profile.satisfaction_focus.map((item) => (
              <Badge key={item} variant="secondary">
                {item}
              </Badge>
            ))
          ) : (
            <span className="text-sm text-muted-foreground">기록 없음</span>
          )}
        </div>
      </div>

      <CheckinForm onSaved={(nextProfile) => setState({ kind: "ready", profile: nextProfile })} />

      <Button variant="outline" nativeButton={false} render={<Link href="/onboarding/investor-profile" />}>
        설문 다시 작성
      </Button>
    </div>
  );
}

function ProfileMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border p-3 text-sm">
      <div className="text-muted-foreground">{label}</div>
      <div className="mt-1 font-medium text-foreground">{value}</div>
    </div>
  );
}

function CheckinForm({
  onSaved,
}: {
  onSaved: (profile: InvestorProfileResponse) => void;
}) {
  const [satisfaction, setSatisfaction] = useState("4");
  const [confidence, setConfidence] = useState("3");
  const [stress, setStress] = useState("2");
  const [automation, setAutomation] = useState<ProfileCheckinPayload["automation_adjustment"]>("same");
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState<CheckinStatus>({ kind: "idle" });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus({ kind: "saving" });
    try {
      const result = await postProfileCheckin({
        trigger_type: "manual",
        satisfaction_score: parseInt(satisfaction, 10),
        confidence_score: parseInt(confidence, 10),
        stress_score: parseInt(stress, 10),
        automation_adjustment: automation,
        notes: notes.trim() || undefined,
      });
      onSaved(result.profile);
      setStatus({ kind: "saved" });
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "체크인을 저장하지 못했습니다.";
      setStatus({ kind: "error", message });
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border border-border p-4">
      <h2 className="text-sm font-semibold text-foreground">만족도 체크인</h2>
      <div className="grid gap-3 sm:grid-cols-3">
        <ScoreInput id="satisfaction" label="만족도" value={satisfaction} onChange={setSatisfaction} />
        <ScoreInput id="confidence" label="이해도" value={confidence} onChange={setConfidence} />
        <ScoreInput id="stress" label="불안도" value={stress} onChange={setStress} />
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="automation-adjustment">자동화 수준</Label>
        <select
          id="automation-adjustment"
          className="h-8 rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
          value={automation}
          onChange={(event) => setAutomation(event.target.value as ProfileCheckinPayload["automation_adjustment"])}
        >
          <option value="lower">낮추기</option>
          <option value="same">유지</option>
          <option value="raise">올리기 검토</option>
        </select>
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="checkin-notes">메모</Label>
        <Input
          id="checkin-notes"
          value={notes}
          onChange={(event) => setNotes((event.target as HTMLInputElement).value)}
          placeholder="예: 알림은 적당하지만 하락장 설명이 더 필요함"
        />
      </div>
      <Button type="submit" disabled={status.kind === "saving"}>
        {status.kind === "saving" ? "저장 중…" : "체크인 저장"}
      </Button>
      {status.kind === "saved" && (
        <p role="status" className="text-sm text-muted-foreground">저장되었습니다.</p>
      )}
      {status.kind === "error" && (
        <p role="alert" className="text-sm text-destructive">{status.message}</p>
      )}
    </form>
  );
}

function ScoreInput({
  id,
  label,
  value,
  onChange,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <Label htmlFor={id}>{label}</Label>
      <Input
        id={id}
        type="number"
        min={1}
        max={5}
        value={value}
        onChange={(event) => onChange((event.target as HTMLInputElement).value)}
      />
    </div>
  );
}

// ── Membership Tab ───────────────────────────────────────────────────────────

type MembershipState =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "ready"; requests: MembershipRequestResponse[]; busyId: string | null };

type DepositRecognitionState =
  | { kind: "idle" }
  | { kind: "checking" }
  | { kind: "ready"; matches: MembershipDepositMatchResponse[]; scannedLines: number; candidateRequests: number }
  | { kind: "error"; message: string };

type ReadinessState =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "ready"; data: MembershipReadinessResponse };

const MEMBERSHIP_STATUS_LABELS: Record<MembershipStatus, string> = {
  requested: "신청 접수",
  verification_pending: "검증 대기",
  deposit_pending: "입금 대기",
  active: "활성",
  rejected: "거절",
  expired: "만료",
};

function membershipErrorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    const detail = (err.body as { detail?: unknown } | undefined)?.detail;
    if (typeof detail === "string") return detail;
    if (err.status === 401) return "로그인이 필요합니다.";
    if (err.status === 403) return "회원 승인 관리는 Owner만 사용할 수 있습니다.";
  }
  return "회원 승인 목록을 불러오지 못했습니다.";
}

function MembershipTab() {
  const [state, setState] = useState<MembershipState>({ kind: "loading" });
  const [recognitionText, setRecognitionText] = useState("");
  const [recognitionState, setRecognitionState] = useState<DepositRecognitionState>({ kind: "idle" });

  async function load() {
    setState({ kind: "loading" });
    try {
      const result = await getMembershipRequests();
      setState({ kind: "ready", requests: result.requests, busyId: null });
    } catch (err) {
      setState({ kind: "error", message: membershipErrorMessage(err) });
    }
  }

  useEffect(() => {
    let cancelled = false;
    getMembershipRequests()
      .then((result) => {
        if (!cancelled) {
          setState({ kind: "ready", requests: result.requests, busyId: null });
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setState({ kind: "error", message: membershipErrorMessage(err) });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function transition(
    request: MembershipRequestResponse,
    status: MembershipStatus,
    evidenceType: string,
    grantDays?: number,
    loginUsername?: string,
    initialPassword?: string,
  ) {
    if (state.kind !== "ready") return;
    setState({ ...state, busyId: request.request_id });
    try {
      const updated = await postMembershipTransition(request.request_id, {
        status,
        evidence_type: evidenceType,
        grant_days: grantDays,
        login_username: loginUsername || undefined,
        initial_password: initialPassword || undefined,
      });
      setState((prev) =>
        prev.kind === "ready"
          ? {
              ...prev,
              busyId: null,
              requests: prev.requests.map((item) =>
                item.request_id === updated.request_id ? updated : item,
              ),
            }
          : prev,
      );
    } catch (err) {
      setState({ kind: "error", message: membershipErrorMessage(err) });
    }
  }

  async function recognizeDeposits() {
    const sourceText = recognitionText.trim();
    if (!sourceText) {
      setRecognitionState({ kind: "error", message: "은행 입금내역 텍스트를 붙여넣으세요." });
      return;
    }
    setRecognitionState({ kind: "checking" });
    try {
      const result = await postMembershipDepositRecognition({
        source_text: sourceText,
        min_confidence: 50,
      });
      setRecognitionState({
        kind: "ready",
        matches: result.matches,
        scannedLines: result.scanned_lines,
        candidateRequests: result.candidate_requests,
      });
    } catch (err) {
      setRecognitionState({ kind: "error", message: membershipErrorMessage(err) });
    }
  }

  if (state.kind === "loading") {
    return <div className="h-36 max-w-4xl animate-pulse rounded-lg bg-muted" />;
  }

  if (state.kind === "error") {
    return (
      <div className="max-w-2xl space-y-3">
        <p role="alert" className="text-sm text-destructive">{state.message}</p>
        <Button variant="outline" onClick={() => void load()}>다시 불러오기</Button>
      </div>
    );
  }

  const recognitionByRequest = new Map<string, MembershipDepositMatchResponse>();
  if (recognitionState.kind === "ready") {
    for (const match of recognitionState.matches) {
      recognitionByRequest.set(match.request_id, match);
    }
  }

  return (
    <div className="max-w-5xl space-y-5">
      <MembershipReadinessPanel />

      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-muted-foreground">
          `/signup`으로 접수된 신청을 검증하고, 입금대기 또는 활성 상태로 전환합니다.
        </p>
        <Button variant="outline" onClick={() => void load()} disabled={state.busyId !== null}>
          새로고침
        </Button>
      </div>

      <section className="rounded-lg border border-border p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-foreground">입금코드 인식</h2>
            <p className="mt-1 text-xs text-muted-foreground">
              은행앱/인터넷뱅킹 입금내역을 붙여넣으면 입금코드, 금액, 이름으로 대기 신청을 찾습니다.
            </p>
          </div>
          <Button
            variant="outline"
            onClick={() => void recognizeDeposits()}
            disabled={recognitionState.kind === "checking"}
          >
            {recognitionState.kind === "checking" ? "인식 중…" : "입금 인식"}
          </Button>
        </div>
        <textarea
          aria-label="은행 입금내역 붙여넣기"
          className="mt-3 min-h-24 w-full resize-y rounded-lg border border-input bg-transparent px-3 py-2 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
          value={recognitionText}
          onChange={(event) => setRecognitionText(event.target.value)}
          placeholder="예: 2026-06-19 홍길동 AF-1A2B3C 입금 20,000원"
        />
        {recognitionState.kind === "ready" && (
          <div className="mt-3 text-xs text-muted-foreground">
            {recognitionState.scannedLines}줄에서 {recognitionState.candidateRequests}건의 입금대기 신청을 비교했고,
            {recognitionState.matches.length}건을 찾았습니다.
          </div>
        )}
        {recognitionState.kind === "error" && (
          <p role="alert" className="mt-3 text-sm text-destructive">{recognitionState.message}</p>
        )}
      </section>

      {state.requests.length === 0 ? (
        <div className="rounded-lg border border-border p-4 text-sm text-muted-foreground">
          접수된 가입 승인 신청이 없습니다.
        </div>
      ) : (
        <div className="overflow-hidden rounded-lg border border-border">
          <div className="grid grid-cols-[1.2fr_1fr_1fr_1.4fr] gap-3 border-b border-border bg-muted/40 px-3 py-2 text-xs font-medium text-muted-foreground">
            <div>신청자</div>
            <div>상태</div>
            <div>입금</div>
            <div>액션</div>
          </div>
          <div className="divide-y divide-border">
            {state.requests.map((request) => (
              <MembershipRow
                key={request.request_id}
                request={request}
                busy={state.busyId === request.request_id}
                recognition={recognitionByRequest.get(request.request_id)}
                onTransition={transition}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function MembershipReadinessPanel() {
  const [state, setState] = useState<ReadinessState>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    getMembershipReadiness()
      .then((data) => {
        if (!cancelled) setState({ kind: "ready", data });
      })
      .catch((err) => {
        if (!cancelled) setState({ kind: "error", message: membershipErrorMessage(err) });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (state.kind === "loading") {
    return <div className="h-28 animate-pulse rounded-lg bg-muted" />;
  }

  if (state.kind === "error") {
    return (
      <div className="rounded-lg border border-border p-4">
        <p role="alert" className="text-sm text-destructive">{state.message}</p>
      </div>
    );
  }

  const { data } = state;
  const blocked = data.items.filter((item) => item.state === "block").length;
  const watched = data.items.filter((item) => item.state === "watch").length;

  return (
    <section className="rounded-lg border border-border p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-foreground">운영 전환 체크</h2>
          <p className="mt-1 text-xs text-muted-foreground">{data.summary}</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={data.can_launch ? "default" : "secondary"}>
            {data.can_launch ? "출시 가능" : "로컬 프로토타입"}
          </Badge>
          <span className="text-sm font-medium text-foreground">{data.score}/100</span>
        </div>
      </div>
      <div className="mt-3 grid gap-2 sm:grid-cols-2">
        {data.items.map((item) => (
          <div key={item.id} className="rounded-md border border-border bg-muted/30 p-3 text-xs">
            <div className="flex items-center justify-between gap-2">
              <div className="font-medium text-foreground">{item.label}</div>
              <Badge variant={item.state === "pass" ? "default" : "secondary"}>
                {item.state === "pass" ? "통과" : item.state === "watch" ? "확인" : "차단"}
              </Badge>
            </div>
            <p className="mt-1 text-muted-foreground">{item.detail}</p>
            <div className="mt-2 text-muted-foreground">{item.gate} · {item.evidence}</div>
          </div>
        ))}
      </div>
      <div className="mt-3 text-xs text-muted-foreground">
        차단 {blocked}건 · 확인 {watched}건
      </div>
    </section>
  );
}

function MembershipRow({
  request,
  busy,
  recognition,
  onTransition,
}: {
  request: MembershipRequestResponse;
  busy: boolean;
  recognition?: MembershipDepositMatchResponse;
  onTransition: (
    request: MembershipRequestResponse,
    status: MembershipStatus,
    evidenceType: string,
    grantDays?: number,
    loginUsername?: string,
    initialPassword?: string,
  ) => void;
}) {
  const instruction = request.deposit_instruction;
  const isTerminal = ["active", "rejected", "expired"].includes(request.status);
  const [loginUsername, setLoginUsername] = useState(request.contact);
  const [initialPassword, setInitialPassword] = useState("");
  const canActivateWithAccount = initialPassword.length >= 8;
  const recognitionEvidence =
    recognition && recognition.confidence >= 80
      ? "code_assisted_deposit_match"
      : "manual_bank_app_check";

  return (
    <div className="grid grid-cols-[1.2fr_1fr_1fr_1.4fr] gap-3 px-3 py-3 text-sm">
      <div className="min-w-0">
        <div className="truncate font-medium text-foreground">{request.display_name}</div>
        <div className="truncate text-xs text-muted-foreground">{request.contact}</div>
        <div className="mt-1 font-mono text-[11px] text-muted-foreground">{request.request_id}</div>
      </div>
      <div>
        <Badge variant={request.status === "active" ? "default" : "secondary"}>
          {MEMBERSHIP_STATUS_LABELS[request.status]}
        </Badge>
        <div className="mt-1 text-xs text-muted-foreground">{formatDateTime(request.updated_at)}</div>
      </div>
      <div className="text-xs text-muted-foreground">
        <div className="font-medium text-foreground">{request.price_krw.toLocaleString("ko-KR")}원</div>
        {instruction ? (
          <div className="mt-1 space-y-1">
            <div>코드 <span className="font-mono text-foreground">{instruction.deposit_code}</span></div>
            <div>{instruction.account_configured ? "계좌 설정됨" : "계좌 설정 필요"}</div>
            {recognition && (
              <div className="rounded-md border border-border bg-muted/40 p-2">
                <div className="font-medium text-foreground">인식 {recognition.confidence}%</div>
                <div>{recognition.reasons.join(", ")}</div>
                <div className="truncate">{recognition.matched_text_excerpt}</div>
              </div>
            )}
          </div>
        ) : (
          <div className="mt-1">검증 후 입금 안내</div>
        )}
      </div>
      <div className="flex flex-wrap gap-1.5">
        {request.status === "requested" && (
          <>
            <Button size="sm" variant="outline" disabled={busy} onClick={() => onTransition(request, "verification_pending", "owner_review")}>
              검증 대기
            </Button>
            <Button size="sm" variant="outline" disabled={busy} onClick={() => onTransition(request, "deposit_pending", "owner_verified_person")}>
              입금 안내
            </Button>
          </>
        )}
        {request.status === "verification_pending" && (
          <Button size="sm" variant="outline" disabled={busy} onClick={() => onTransition(request, "deposit_pending", "owner_verified_person")}>
            입금 안내
          </Button>
        )}
        {request.status === "deposit_pending" && (
          <div className="flex w-full flex-col gap-1.5">
            <Input
              aria-label={`${request.display_name} 로그인 ID`}
              value={loginUsername}
              onChange={(event) => setLoginUsername((event.target as HTMLInputElement).value)}
              placeholder="로그인 ID"
              className="h-8 text-xs"
            />
            <Input
              aria-label={`${request.display_name} 임시 비밀번호`}
              type="password"
              value={initialPassword}
              onChange={(event) => setInitialPassword((event.target as HTMLInputElement).value)}
              placeholder="임시 비밀번호 8자 이상"
              className="h-8 text-xs"
            />
            <Button
              size="sm"
              disabled={busy || !canActivateWithAccount}
              onClick={() =>
                onTransition(
                  request,
                  "active",
                  recognitionEvidence,
                  30,
                  loginUsername.trim(),
                  initialPassword,
                )
              }
            >
              {recognitionEvidence === "code_assisted_deposit_match"
                ? "인식 승인 + 계정 활성화"
                : "입금 확인 + 계정 활성화"}
            </Button>
          </div>
        )}
        {!isTerminal && (
          <>
            <Button size="sm" variant="destructive" disabled={busy} onClick={() => onTransition(request, "rejected", "owner_rejected")}>
              거절
            </Button>
            <Button size="sm" variant="ghost" disabled={busy} onClick={() => onTransition(request, "expired", "owner_expired")}>
              만료
            </Button>
          </>
        )}
        {isTerminal && (
          <span className="text-xs text-muted-foreground">
            {request.account_grant ? `${request.account_grant.username} 활성화됨` : "처리 완료"}
          </span>
        )}
      </div>
    </div>
  );
}

function formatDateTime(value: string | null): string {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("ko-KR", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// ── Account Tab ──────────────────────────────────────────────────────────────

const ROLE_LABELS: Record<string, string> = {
  owner: "오너",
  member: "회원",
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

function PasswordChangeForm({ canChangePassword }: { canChangePassword: boolean }) {
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
      {!canChangePassword && (
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
        disabled={!canChangePassword || status.kind === "saving"}
      />
      <SecretField
        id="pw-new"
        label="새 비밀번호 (최소 8자)"
        maskedPlaceholder="새 비밀번호"
        value={next}
        onChange={setNext}
        disabled={!canChangePassword || status.kind === "saving"}
      />
      <SecretField
        id="pw-confirm"
        label="새 비밀번호 확인"
        maskedPlaceholder="새 비밀번호 확인"
        value={confirm}
        onChange={setConfirm}
        disabled={!canChangePassword || status.kind === "saving"}
      />
      <Button type="submit" disabled={!canChangePassword || status.kind === "saving"}>
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
  const [providers, setProviders] = useState<SsoProviderInfo[]>([]);

  useEffect(() => {
    let cancelled = false;
    getSsoProviders()
      .then((data) => {
        if (!cancelled) setProviders(Array.isArray(data.providers) ? data.providers : []);
      })
      .catch(() => {
        if (!cancelled) setProviders([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const enabled = providers.filter((p) => p.enabled);

  return (
    <div className="rounded-lg border border-dashed border-border p-4 text-sm">
      <div className="font-medium text-foreground">SSO/SNS 로그인</div>
      {enabled.length > 0 ? (
        <div className="mt-2 flex flex-wrap gap-2">
          {enabled.map((provider) => (
            <Badge key={provider.id} variant="secondary">
              {provider.label}
            </Badge>
          ))}
        </div>
      ) : (
        <p className="mt-1 text-muted-foreground">
          활성 provider가 없습니다. 서버 환경변수 설정 후 로그인 화면에 표시됩니다.
        </p>
      )}
    </div>
  );
}

type IntegrationState =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "ready"; data: IntegrationSettingsResponse };

type IntegrationSaveStatus =
  | { kind: "idle" }
  | { kind: "saving" }
  | { kind: "saved" }
  | { kind: "error"; message: string };

function integrationErrorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    const detail = (err.body as { detail?: unknown } | undefined)?.detail;
    if (typeof detail === "string") return detail;
    if (err.status === 401) return "로그인이 필요합니다.";
    if (err.status === 403) return "승인된 계정만 연동을 관리할 수 있습니다.";
  }
  return "연동 정보를 불러오지 못했습니다.";
}

function IntegrationsSection() {
  const [state, setState] = useState<IntegrationState>({ kind: "loading" });
  const [providerId, setProviderId] = useState("openai");
  const [accountLabel, setAccountLabel] = useState("");
  const [secretValue, setSecretValue] = useState("");
  const [scopes, setScopes] = useState("");
  const [enabled, setEnabled] = useState(true);
  const [status, setStatus] = useState<IntegrationSaveStatus>({ kind: "idle" });

  async function load() {
    setState({ kind: "loading" });
    try {
      const data = await getIntegrations();
      setState({ kind: "ready", data });
      if (!data.providers.find((provider) => provider.id === providerId)) {
        setProviderId(data.providers[0]?.id ?? "openai");
      }
    } catch (err) {
      setState({ kind: "error", message: integrationErrorMessage(err) });
    }
  }

  useEffect(() => {
    let cancelled = false;
    getIntegrations()
      .then((data) => {
        if (cancelled) return;
        setState({ kind: "ready", data });
        setProviderId((current) =>
          data.providers.find((provider) => provider.id === current)
            ? current
            : data.providers[0]?.id ?? "openai",
        );
      })
      .catch((err) => {
        if (!cancelled) {
          setState({ kind: "error", message: integrationErrorMessage(err) });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSave(event: React.FormEvent) {
    event.preventDefault();
    setStatus({ kind: "saving" });
    try {
      await putIntegrationCredential(providerId, {
        secret_value: secretValue.trim() || undefined,
        account_label: accountLabel.trim() || undefined,
        scopes: scopes
          .split(",")
          .map((scope) => scope.trim())
          .filter(Boolean),
        enabled,
      });
      setSecretValue("");
      setStatus({ kind: "saved" });
      await load();
    } catch (err) {
      setStatus({ kind: "error", message: integrationErrorMessage(err) });
    }
  }

  async function handleDelete(provider: IntegrationCredentialResponse) {
    setStatus({ kind: "saving" });
    try {
      await deleteIntegrationCredential(provider.provider_id);
      if (provider.provider_id === providerId) {
        setSecretValue("");
      }
      setStatus({ kind: "saved" });
      await load();
    } catch (err) {
      setStatus({ kind: "error", message: integrationErrorMessage(err) });
    }
  }

  if (state.kind === "loading") {
    return <div className="h-32 animate-pulse rounded-lg bg-muted" />;
  }

  if (state.kind === "error") {
    return (
      <div className="space-y-3 rounded-lg border border-border p-4">
        <p role="alert" className="text-sm text-destructive">{state.message}</p>
        <Button variant="outline" onClick={() => void load()}>다시 불러오기</Button>
      </div>
    );
  }

  const selectedProvider = state.data.providers.find((provider) => provider.id === providerId)
    ?? state.data.providers[0];
  const selectedIntegration = state.data.integrations.find(
    (integration) => integration.provider_id === selectedProvider?.id,
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold text-foreground">사용자 연동</h2>
        <Button variant="outline" size="sm" onClick={() => void load()}>
          새로고침
        </Button>
      </div>

      <div className="grid gap-2 sm:grid-cols-2">
        {state.data.integrations.map((integration) => (
          <div key={integration.provider_id} className="rounded-lg border border-border p-3 text-sm">
            <div className="flex items-center justify-between gap-2">
              <div>
                <div className="font-medium text-foreground">{integration.label}</div>
                <div className="text-xs text-muted-foreground">{integration.kind.toUpperCase()}</div>
              </div>
              <Badge variant={integration.configured && integration.enabled ? "default" : "secondary"}>
                {integration.configured ? (integration.enabled ? "설정됨" : "비활성") : "미설정"}
              </Badge>
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              {integration.account_label ?? "계정 라벨 없음"}
              {integration.secret_hint ? ` · ${integration.secret_hint}` : ""}
            </div>
            {integration.configured && (
              <Button
                variant="ghost"
                size="sm"
                className="mt-2"
                onClick={() => void handleDelete(integration)}
                disabled={status.kind === "saving"}
              >
                삭제
              </Button>
            )}
          </div>
        ))}
      </div>

      {selectedProvider && (
        <form onSubmit={handleSave} className="space-y-3 rounded-lg border border-border p-4">
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="integration-provider">Provider</Label>
              <select
                id="integration-provider"
                className="h-8 rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                value={providerId}
                onChange={(event) => {
                  const nextProvider = event.target.value;
                  const next = state.data.integrations.find((item) => item.provider_id === nextProvider);
                  setProviderId(nextProvider);
                  setAccountLabel(next?.account_label ?? "");
                  setScopes(next?.scopes.join(", ") ?? "");
                  setEnabled(next?.enabled ?? true);
                }}
              >
                {state.data.providers.map((provider: IntegrationProviderInfo) => (
                  <option key={provider.id} value={provider.id}>
                    {provider.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="integration-account">계정 라벨</Label>
              <Input
                id="integration-account"
                value={accountLabel}
                onChange={(event) => setAccountLabel((event.target as HTMLInputElement).value)}
                placeholder={selectedProvider.account_label_hint}
              />
            </div>
          </div>
          <SecretField
            id="integration-secret"
            label={selectedProvider.secret_label}
            maskedPlaceholder={selectedIntegration?.secret_set ? "새 값 입력 시 교체" : selectedProvider.secret_label}
            value={secretValue}
            onChange={setSecretValue}
          />
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="integration-scopes">Scopes</Label>
            <Input
              id="integration-scopes"
              value={scopes}
              onChange={(event) => setScopes((event.target as HTMLInputElement).value)}
              placeholder="analysis, notification"
            />
          </div>
          <label className="flex items-center gap-2 text-sm text-foreground">
            <input
              type="checkbox"
              checked={enabled}
              onChange={(event) => setEnabled(event.target.checked)}
              className="size-4 rounded border-input"
            />
            활성화
          </label>
          <Button type="submit" disabled={status.kind === "saving"}>
            {status.kind === "saving" ? "저장 중…" : "연동 저장"}
          </Button>
          {status.kind === "saved" && (
            <p role="status" className="text-sm text-muted-foreground">저장되었습니다.</p>
          )}
          {status.kind === "error" && (
            <p role="alert" className="text-sm text-destructive">{status.message}</p>
          )}
        </form>
      )}
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
        <PasswordChangeForm canChangePassword={account.role !== "guest"} />
      </section>

      <section>
        <SessionSection />
      </section>

      <section>
        <KisKeysSection />
      </section>

      <section>
        <IntegrationsSection />
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
                {id === "profile" && <ProfileTab />}
                {id === "membership" && <MembershipTab />}
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
