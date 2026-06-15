// web/src/app/agents/page.tsx
"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";
import { AgentMessage, type AgentMessageData } from "@/components/domain/AgentMessage";
import { IcTranscript } from "@/components/domain/IcTranscript";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  apiAgentsList,
  apiAgentAsk,
  apiIcRun,
  apiIcDecisions,
  type AgentsListResponse,
  type IcDecision,
} from "@/lib/api";

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
        <CardTitle>IC 회의 실행</CardTitle>
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

  // Agents unavailable
  if (!data?.available) {
    return (
      <AppShell>
        <EmptyState
          title="에이전트 사용 불가"
          description={data?.message ?? "에이전트 팀이 현재 비활성 상태입니다."}
          phase="에이전트 비활성"
        />
      </AppShell>
    );
  }

  const agentNames = (data.agents ?? []).map((a) => a.name).filter(Boolean);

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-base font-semibold text-foreground">에이전트</h1>
          <p className="mt-0.5 text-sm text-muted-foreground">
            에이전트 팀 {agentNames.length}명 활성
          </p>
        </div>

        {/* Team roster */}
        {agentNames.length > 0 && (
          <section aria-label="에이전트 팀">
            <h2 className="mb-2 text-sm font-medium text-muted-foreground">팀 목록</h2>
            <div
              className="flex flex-wrap gap-2"
              data-testid="agent-team"
              aria-label="에이전트 팀 목록"
            >
              {data.agents.map((agent) => (
                <div
                  key={agent.name}
                  className="flex flex-col rounded-lg border border-border bg-card px-3 py-2 text-sm"
                >
                  <span className="font-medium text-foreground">{agent.name}</span>
                  {agent.role && (
                    <span className="text-xs text-muted-foreground">{agent.role}</span>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Ask panel */}
        {agentNames.length > 0 && (
          <section aria-label="에이전트에게 묻기">
            <AskPanel agents={agentNames} />
          </section>
        )}

        {/* IC run panel */}
        <section aria-label="IC 회의">
          <IcPanel />
        </section>

        {/* Past decisions */}
        <section aria-label="과거 결정">
          <PastDecisions />
        </section>
      </div>
    </AppShell>
  );
}
