// web/src/app/agents/page.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";
import { AgentMessage, type AgentMessageData } from "@/components/domain/AgentMessage";
import { IcTranscript } from "@/components/domain/IcTranscript";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useSymbols } from "@/hooks/useSymbols";
import { fmtWon } from "@/lib/format";
import {
  apiGet,
  apiAgentsList,
  apiAgentAsk,
  apiAgentResearch,
  apiPremarketSummary,
  apiIcRun,
  apiIcDecisions,
  type AgentInfo,
  type AgentsListResponse,
  type AgentResearchResponse,
  type IcDecision,
  type PremarketSummaryResponse,
} from "@/lib/api";

// ── Honest gap banner (shown above the briefing) ────────────────────────────

function HonestGapBanner() {
  return (
    <div
      role="note"
      data-testid="honest-gap-banner"
      className="rounded-lg border border-amber-400/40 bg-amber-50 p-3 text-xs leading-relaxed text-amber-800 dark:bg-amber-900/20 dark:text-amber-300"
    >
      <p className="font-medium">제공 범위 안내 (솔직한 한계)</p>
      <ul className="mt-1 list-disc space-y-0.5 pl-4">
        <li>실시간 뉴스 연동은 미구현입니다 — 브리핑은 공시(disclosures) 기반입니다.</li>
        <li>자동 트리거는 미가동입니다 — 리서치는 수동(&ldquo;리서치 실행&rdquo;)으로만 실행됩니다.</li>
        <li>제안은 규칙 기반 예시이며, 조건/주문을 자동 저장하지 않습니다.</li>
      </ul>
    </div>
  );
}

// ── Expert agent roster ────────────────────────────────────────────────────

function ExpertAgentsPanel({ agents }: { agents: AgentInfo[] }) {
  const expertAgents = agents.filter((agent) => agent.expert);
  const grouped = expertAgents.reduce<Record<string, AgentInfo[]>>((acc, agent) => {
    const category = agent.category || "기타";
    acc[category] = [...(acc[category] ?? []), agent];
    return acc;
  }, {});

  return (
    <Card data-testid="expert-agents-panel">
      <CardHeader>
        <CardTitle>리서치·금융 전문가 에이전트</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {expertAgents.length === 0 ? (
          <p className="text-sm text-muted-foreground">표시할 전문가 에이전트가 없습니다.</p>
        ) : (
          Object.entries(grouped).map(([category, items]) => (
            <section key={category} aria-label={`${category} 에이전트`} className="space-y-2">
              <h3 className="text-sm font-medium text-muted-foreground">{category}</h3>
              <div className="divide-y divide-border rounded-lg border border-border">
                {items.map((agent) => (
                  <div
                    key={agent.name}
                    className="grid gap-1 px-3 py-2 text-sm sm:grid-cols-[180px_140px_1fr] sm:items-center"
                  >
                    <span className="font-medium text-foreground">{agent.name}</span>
                    <span className="text-muted-foreground">{agent.role}</span>
                    <span className="line-clamp-2 text-xs text-muted-foreground">
                      {agent.description || "설명 없음"}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          ))
        )}
      </CardContent>
    </Card>
  );
}

// ── Saved pre-market summary ───────────────────────────────────────────────

function PremarketSummaryPanel() {
  const { data, isPending, error } = useQuery<PremarketSummaryResponse>({
    queryKey: ["premarket-summary"],
    queryFn: () => apiPremarketSummary(),
    retry: false,
    staleTime: 30_000,
  });

  return (
    <Card data-testid="premarket-summary-panel">
      <CardHeader>
        <CardTitle>프리마켓 핵심 요약</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {isPending && (
          <div className="h-24 animate-pulse rounded-xl bg-muted" role="status" aria-label="요약 로딩 중" />
        )}
        {error && (
          <div className="rounded-lg border border-dashed border-border p-3 text-sm text-muted-foreground">
            저장된 프리마켓 요약이 없습니다. CLI에서{" "}
            <code className="rounded bg-muted px-1 py-0.5">python scripts/run_premarket_summary.py</code>
            를 실행하면 여기에 표시됩니다.
          </div>
        )}
        {data && (
          <>
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
              <span>{data.date}</span>
              <span>{data.file}</span>
              <span>{data.market_open_reference}</span>
            </div>
            <ul className="list-disc space-y-1 pl-4 text-sm" data-testid="premarket-highlights">
              {data.highlights.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
            <details className="rounded-lg border border-border p-3 text-sm">
              <summary className="cursor-pointer font-medium text-foreground">저장 파일 원문</summary>
              <pre className="mt-3 max-h-96 overflow-auto whitespace-pre-wrap text-xs leading-relaxed text-muted-foreground">
                {data.content}
              </pre>
            </details>
          </>
        )}
      </CardContent>
    </Card>
  );
}

// ── Owner detection (for owner-only AI insight) ─────────────────────────────

interface SessionResponse {
  role: string;
  username: string | null;
  data_source: string;
}

function useIsOwner(): boolean {
  const { data } = useQuery<SessionResponse>({
    queryKey: ["auth-me"],
    queryFn: () => apiGet<SessionResponse>("/api/auth/me"),
    retry: false,
    staleTime: 60_000,
  });
  return data?.role === "owner";
}

// ── Fundamental key labels (Korean) ─────────────────────────────────────────

const FUNDAMENTAL_LABELS: Record<string, string> = {
  per: "PER",
  pbr: "PBR",
  eps: "EPS",
  bps: "BPS",
  market_cap: "시가총액",
  dividend_yield: "배당수익률",
};

function fundamentalEntries(f: Record<string, unknown>): Array<[string, string]> {
  return Object.entries(f)
    .filter(([, v]) => v !== null && v !== undefined && v !== "")
    .map(([k, v]) => [FUNDAMENTAL_LABELS[k] ?? k, String(v)] as [string, string]);
}

// ── AI insight (owner-only) ─────────────────────────────────────────────────

type InsightState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "answer"; message: AgentMessageData }
  | { kind: "error"; message: string };

function AiInsightButton({
  agent,
  symbol,
  name,
  llmAvailable,
}: {
  agent: string;
  symbol: string;
  name: string;
  llmAvailable: boolean;
}) {
  const [state, setState] = useState<InsightState>({ kind: "idle" });

  async function handleAsk() {
    setState({ kind: "loading" });
    try {
      const context = `종목 ${name} (${symbol}) 에 대한 공시·펀더멘털 기반 브리핑을 검토 중입니다.`;
      const question = `${name}(${symbol}) 종목의 현재 투자 매력도와 리스크를 간단히 평가해 주세요.`;
      const res = await apiAgentAsk(agent, question, context);
      setState({
        kind: "answer",
        message: { agent, content: res.answer, kind: "agent" },
      });
    } catch (err) {
      setState({
        kind: "error",
        message: err instanceof Error ? err.message : "알 수 없는 오류",
      });
    }
  }

  return (
    <div className="space-y-2" data-testid="ai-insight">
      <Button
        type="button"
        size="sm"
        variant="outline"
        onClick={() => void handleAsk()}
        disabled={state.kind === "loading" || !llmAvailable}
        title={llmAvailable ? undefined : "LLM 키가 없어 AI 인사이트를 사용할 수 없습니다."}
      >
        {state.kind === "loading" ? "분석 중…" : "AI 인사이트 요청"}
      </Button>
      {!llmAvailable && (
        <p className="text-xs text-muted-foreground">
          LLM API 키가 설정되지 않아 AI 인사이트는 비활성화되어 있습니다.
        </p>
      )}
      {state.kind === "answer" && <AgentMessage message={state.message} />}
      {state.kind === "error" && (
        <div role="alert" className="rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
          AI 인사이트 오류: {state.message}
        </div>
      )}
    </div>
  );
}

// ── Briefing card ────────────────────────────────────────────────────────────

function BriefingCard({
  data,
  agentNames,
  isOwner,
  llmAvailable,
}: {
  data: AgentResearchResponse;
  agentNames: string[];
  isOwner: boolean;
  llmAvailable: boolean;
}) {
  const router = useRouter();
  const f = fundamentalEntries(data.fundamental ?? {});
  const proposal = data.proposal;
  const disclosureRows = data.disclosures?.rows ?? [];
  const gate = data.disclosure_gate;

  function handleMakeCondition() {
    const q = new URLSearchParams({
      symbol: proposal.symbol,
      side: proposal.side,
      price: String(Math.round(proposal.target_price)),
      qty: String(proposal.quantity),
    });
    // Pre-fills the trade form only — does NOT submit / save a condition.
    router.push(`/trade?${q}`);
  }

  return (
    <Card data-testid="briefing-card">
      <CardHeader>
        <CardTitle>
          {data.name ? `${data.name} (${data.symbol})` : data.symbol} 브리핑
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        {/* Current price */}
        <div className="flex items-baseline gap-2">
          <span className="text-sm text-muted-foreground">현재가</span>
          <span className="text-lg font-semibold text-foreground" data-testid="briefing-price">
            {fmtWon(data.price)}
          </span>
        </div>

        {/* Fundamental */}
        <section aria-label="펀더멘털 주요지표">
          <h3 className="mb-1.5 text-sm font-medium text-muted-foreground">펀더멘털 주요지표</h3>
          {f.length === 0 ? (
            <p className="text-sm text-muted-foreground" data-testid="fundamental-empty">
              펀더멘털 지표 없음 (mock 환경이거나 데이터 미제공).
            </p>
          ) : (
            <dl className="grid grid-cols-2 gap-2 sm:grid-cols-3" data-testid="fundamental-grid">
              {f.map(([label, value]) => (
                <div key={label} className="rounded-lg border border-border bg-card px-3 py-2">
                  <dt className="text-xs text-muted-foreground">{label}</dt>
                  <dd className="text-sm font-medium text-foreground">{value}</dd>
                </div>
              ))}
            </dl>
          )}
        </section>

        {/* Disclosures + gate */}
        <section aria-label="최근 공시">
          <div className="mb-1.5 flex items-center justify-between">
            <h3 className="text-sm font-medium text-muted-foreground">최근 공시 (뉴스 아님 · 공시 기반)</h3>
            {gate.blocked ? (
              <span
                role="status"
                data-testid="disclosure-gate-blocked"
                className="rounded-full bg-destructive/10 px-2 py-0.5 text-xs font-semibold text-destructive"
              >
                공시 게이트: 차단
              </span>
            ) : (
              <span
                role="status"
                data-testid="disclosure-gate-clear"
                className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground"
              >
                공시 게이트: 정상
              </span>
            )}
          </div>
          {gate.blocked && gate.reason && (
            <p className="mb-2 text-xs text-destructive">차단 사유: {gate.reason}</p>
          )}
          {disclosureRows.length === 0 ? (
            <p className="text-sm text-muted-foreground" data-testid="disclosures-empty">
              최근 공시 없음.
            </p>
          ) : (
            <ul className="flex flex-col gap-1.5" data-testid="disclosures-list">
              {disclosureRows.map((row, i) => (
                <li
                  key={i}
                  className="rounded-lg border border-border bg-card px-3 py-2 text-sm"
                >
                  <span className="font-medium text-foreground">
                    {String(row.title ?? "(제목 없음)")}
                  </span>
                  <span className="ml-2 text-xs text-muted-foreground">
                    {String(row.date ?? "")} {String(row.category ?? "")}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Proposal */}
        <section aria-label="제안" data-testid="proposal">
          <h3 className="mb-1.5 text-sm font-medium text-muted-foreground">제안 (규칙 기반 · 자동 저장 안 함)</h3>
          <div className="rounded-xl border border-border bg-muted/40 p-3 text-sm">
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
              <span>
                방향:{" "}
                <span className="font-semibold text-foreground" data-testid="proposal-side">
                  {proposal.side === "BUY" ? "매수" : "매도"}
                </span>
              </span>
              <span>
                목표가:{" "}
                <span className="font-semibold text-foreground" data-testid="proposal-target">
                  {fmtWon(proposal.target_price)}
                </span>
              </span>
              <span>
                수량: <span className="font-semibold text-foreground">{proposal.quantity}주</span>
              </span>
            </div>
            <p className="mt-2 text-muted-foreground">근거: {proposal.rationale}</p>
            <p className="mt-1 text-xs text-amber-700 dark:text-amber-400">리스크: {proposal.risk_note}</p>
          </div>
          <Button
            type="button"
            size="sm"
            className="mt-3"
            onClick={handleMakeCondition}
            data-testid="make-condition-btn"
          >
            이 제안으로 조건 만들기
          </Button>
          <p className="mt-1 text-xs text-muted-foreground">
            매매 화면의 조건 양식을 미리 채웁니다. 저장은 자동으로 이루어지지 않으며, 안전 게이트를 거칩니다.
          </p>
        </section>

        {/* Owner-only AI insight */}
        {isOwner && agentNames.length > 0 && (
          <section aria-label="AI 인사이트" className="border-t border-border pt-4">
            <h3 className="mb-2 text-sm font-medium text-muted-foreground">AI 인사이트 (소유자 전용)</h3>
            <AiInsightButton
              agent={agentNames[0]}
              symbol={data.symbol}
              name={data.name || data.symbol}
              llmAvailable={llmAvailable}
            />
          </section>
        )}
      </CardContent>
    </Card>
  );
}

// ── Briefing section (symbol picker + run) ──────────────────────────────────

type BriefingState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "ready"; data: AgentResearchResponse }
  | { kind: "error"; message: string };

function BriefingSection({
  agentNames,
  isOwner,
  llmAvailable,
}: {
  agentNames: string[];
  isOwner: boolean;
  llmAvailable: boolean;
}) {
  const symbolMap = useSymbols();
  const symbolCodes = Object.keys(symbolMap);
  const [symbol, setSymbol] = useState("");
  const [state, setState] = useState<BriefingState>({ kind: "idle" });

  // Default the picker to the first whitelist symbol once it loads.
  const selected = symbol || symbolCodes[0] || "";

  async function handleRun() {
    if (!selected) return;
    setState({ kind: "loading" });
    try {
      const data = await apiAgentResearch(selected);
      setState({ kind: "ready", data });
    } catch (err) {
      setState({
        kind: "error",
        message: err instanceof Error ? err.message : "알 수 없는 오류",
      });
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>종목 전문가 브리핑</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <HonestGapBanner />

        <div className="flex flex-wrap items-end gap-3">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="briefing-symbol">종목 선택</Label>
            <select
              id="briefing-symbol"
              className="h-8 rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
              value={selected}
              onChange={(e) => setSymbol(e.target.value)}
              aria-label="종목 선택"
            >
              {symbolCodes.length === 0 && <option value="">종목 없음</option>}
              {symbolCodes.map((code) => (
                <option key={code} value={code}>
                  {symbolMap[code]} ({code})
                </option>
              ))}
            </select>
          </div>
          <Button
            type="button"
            size="sm"
            onClick={() => void handleRun()}
            disabled={state.kind === "loading" || !selected}
            data-testid="run-research-btn"
          >
            {state.kind === "loading" ? "리서치 중…" : "리서치 실행"}
          </Button>
        </div>

        {state.kind === "loading" && (
          <div className="h-40 animate-pulse rounded-xl bg-muted" role="status" aria-label="리서치 중" />
        )}
        {state.kind === "error" && (
          <div role="alert" className="rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
            리서치 오류: {state.message}
          </div>
        )}
        {state.kind === "ready" && (
          <BriefingCard
            data={state.data}
            agentNames={agentNames}
            isOwner={isOwner}
            llmAvailable={llmAvailable}
          />
        )}
        {state.kind === "idle" && (
          <p className="text-sm text-muted-foreground">
            종목을 선택하고 &ldquo;리서치 실행&rdquo;을 눌러 공시·펀더멘털 기반 브리핑을 받아보세요.
          </p>
        )}
      </CardContent>
    </Card>
  );
}

// ── Ask panel ──────────────────────────────────────────────────────────────

type AskState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "answer"; message: AgentMessageData }
  | { kind: "error"; message: string };

function AskPanel({ agents }: { agents: string[] }) {
  const [selectedAgent, setSelectedAgent] = useState(agents[0] ?? "");
  const [question, setQuestion] = useState("");
  const [state, setState] = useState<AskState>({ kind: "idle" });

  async function handleAsk(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedAgent || !question.trim()) return;
    setState({ kind: "loading" });
    try {
      const res = await apiAgentAsk(selectedAgent, question.trim());
      setState({
        kind: "answer",
        message: { agent: selectedAgent, content: res.answer, kind: "agent" },
      });
    } catch (err) {
      setState({
        kind: "error",
        message: err instanceof Error ? err.message : "알 수 없는 오류",
      });
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>에이전트에게 묻기</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={(e) => { void handleAsk(e); }} className="space-y-3">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="ask-agent">에이전트 선택</Label>
            <select
              id="ask-agent"
              className="h-8 rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value)}
              aria-label="에이전트 선택"
            >
              {agents.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="ask-question">질문</Label>
            <Input
              id="ask-question"
              placeholder="에이전트에게 질문을 입력하세요"
              value={question}
              onChange={(e) => setQuestion((e.target as HTMLInputElement).value)}
              disabled={state.kind === "loading"}
            />
          </div>
          <Button
            type="submit"
            disabled={state.kind === "loading" || !question.trim()}
            size="sm"
          >
            {state.kind === "loading" ? "대기 중…" : "질문하기"}
          </Button>
        </form>

        {state.kind === "answer" && (
          <AgentMessage message={state.message} />
        )}
        {state.kind === "error" && (
          <div role="alert" className="rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
            오류: {state.message}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ── IC run panel ───────────────────────────────────────────────────────────

type IcState =
  | { kind: "idle" }
  | { kind: "starting" }
  | { kind: "streaming"; jobId: string }
  | { kind: "error"; message: string };

function IcPanel() {
  const [topic, setTopic] = useState("");
  const [state, setState] = useState<IcState>({ kind: "idle" });

  async function handleRun(e: React.FormEvent) {
    e.preventDefault();
    if (!topic.trim()) return;
    setState({ kind: "starting" });
    try {
      const res = await apiIcRun(topic.trim());
      setState({ kind: "streaming", jobId: res.job_id });
    } catch (err) {
      setState({
        kind: "error",
        message: err instanceof Error ? err.message : "알 수 없는 오류",
      });
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>투자위원회(IC) 회의 실행</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={(e) => { void handleRun(e); }} className="flex gap-2">
          <Input
            placeholder="토픽 입력 (예: 삼성전자 매수 여부)"
            value={topic}
            onChange={(e) => setTopic((e.target as HTMLInputElement).value)}
            disabled={state.kind === "starting" || state.kind === "streaming"}
            aria-label="IC 토픽"
          />
          <Button
            type="submit"
            size="sm"
            disabled={
              state.kind === "starting" ||
              state.kind === "streaming" ||
              !topic.trim()
            }
          >
            {state.kind === "starting" ? "시작 중…" : "실행"}
          </Button>
        </form>

        {state.kind === "error" && (
          <div role="alert" className="rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
            오류: {state.message}
          </div>
        )}

        <IcTranscript
          jobId={state.kind === "streaming" ? state.jobId : null}
        />
      </CardContent>
    </Card>
  );
}

// ── Past decisions list ────────────────────────────────────────────────────

function PastDecisions() {
  const { data, isPending, error } = useQuery<IcDecision[]>({
    queryKey: ["ic-decisions"],
    queryFn: () => apiIcDecisions(10),
    staleTime: 60_000,
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>과거 IC 결정</CardTitle>
      </CardHeader>
      <CardContent>
        {isPending && (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-8 animate-pulse rounded-lg bg-muted" />
            ))}
          </div>
        )}
        {error && (
          <div role="alert" className="rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
            결정 내역을 불러오지 못했습니다: {(error as Error).message}
          </div>
        )}
        {data && data.length === 0 && (
          <p className="text-sm text-muted-foreground">과거 IC 결정이 없습니다.</p>
        )}
        {data && data.length > 0 && (
          <ul className="flex flex-col gap-2" aria-label="과거 IC 결정 목록" data-testid="past-decisions">
            {data.map((d, i) => (
              <li
                key={d.id ?? i}
                className="rounded-lg border border-border bg-card p-3 text-sm"
              >
                <p className="font-medium text-foreground">{d.topic}</p>
                {(d.decision ?? d.summary) && (
                  <p className="mt-1 text-muted-foreground">{d.decision ?? d.summary}</p>
                )}
                {d.created_at && (
                  <time
                    dateTime={d.created_at}
                    className="mt-1 block text-xs text-muted-foreground"
                  >
                    {new Date(d.created_at).toLocaleString("ko-KR")}
                  </time>
                )}
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}

// ── Main page ──────────────────────────────────────────────────────────────

export default function AgentsPage() {
  const isOwner = useIsOwner();
  const { data, isPending, error } = useQuery<AgentsListResponse>({
    queryKey: ["agents-list"],
    queryFn: apiAgentsList,
    staleTime: 60_000,
    retry: 1,
  });

  // Loading skeleton
  if (isPending) {
    return (
      <AppShell>
        <div className="space-y-4">
          <div className="h-6 w-32 animate-pulse rounded bg-muted" />
          <div className="h-32 animate-pulse rounded-xl bg-muted" />
        </div>
      </AppShell>
    );
  }

  // Fetch error
  if (error) {
    return (
      <AppShell>
        <div role="alert" className="rounded-lg border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive">
          에이전트 목록을 불러오지 못했습니다: {(error as Error).message}
        </div>
      </AppShell>
    );
  }

  const agents = data?.agents ?? [];
  const agentNames = agents.map((a) => a.name).filter(Boolean);
  const llmAvailable = Boolean(data?.available);

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-base font-semibold text-foreground">에이전트</h1>
          <p className="mt-0.5 text-sm text-muted-foreground">
            종목 전문가가 공시·펀더멘털을 모아 요약하고 제안합니다 (읽기 전용 리서치).
          </p>
        </div>

        <section aria-label="리서치 금융 전문가 에이전트">
          <ExpertAgentsPanel agents={agents} />
        </section>

        <section aria-label="프리마켓 핵심 요약">
          <PremarketSummaryPanel />
        </section>

        {/* ── 1. 종목 전문가 브리핑 (manual primary) ── */}
        <section aria-label="종목 전문가 브리핑">
          <BriefingSection
            agentNames={agentNames}
            isOwner={isOwner}
            llmAvailable={llmAvailable}
          />
        </section>

        {/* ── 2. 투자위원회(IC) (secondary) ── */}
        <section aria-label="투자위원회">
          <IcPanel />
        </section>

        <section aria-label="과거 결정">
          <PastDecisions />
        </section>

        {/* ── 3. 에이전트에게 질문(Ask) (secondary) ── */}
        {agentNames.length > 0 ? (
          <section aria-label="에이전트에게 질문">
            <AskPanel agents={agentNames} />
          </section>
        ) : (
          <section aria-label="에이전트에게 질문">
            <EmptyState
              title="질문 불가"
              description={data?.message ?? "에이전트 팀이 현재 비활성 상태입니다."}
              phase="에이전트 비활성"
            />
          </section>
        )}
      </div>
    </AppShell>
  );
}
