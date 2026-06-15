// web/src/components/domain/IcTranscript.tsx
"use client";

import { useEffect, useRef, useState } from "react";
import { AgentMessage, type AgentMessageData } from "./AgentMessage";
import { cn } from "@/lib/utils";

interface IcStep {
  agent?: string;
  content?: string;
  message?: string;
  role?: string;
  kind?: string;
  [key: string]: unknown;
}

interface IcDonePayload {
  decision?: string;
  summary?: string;
  result?: string;
  [key: string]: unknown;
}

type StreamState =
  | { kind: "idle" }
  | { kind: "connecting" }
  | { kind: "streaming"; steps: AgentMessageData[] }
  | { kind: "done"; steps: AgentMessageData[]; decision: string }
  | { kind: "error"; message: string }
  | { kind: "disconnected" };

interface IcTranscriptProps {
  /** When non-null, opens the SSE stream for this job */
  jobId: string | null;
  className?: string;
}

/**
 * IcTranscript — streams an IC run via EventSource.
 *
 * SSE protocol (per backend spec):
 *   - event: step  data: {"agent": "...", "content": "...", "kind": "agent"|"system"}
 *   - event: done  data: {"decision": "...", "summary": "..."}
 *   - event: error data: {"message": "..."}
 *
 * Cleanup: EventSource is closed when jobId changes or component unmounts.
 */
export function IcTranscript({ jobId, className }: IcTranscriptProps) {
  const [state, setState] = useState<StreamState>({ kind: "idle" });
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    // Close any previous connection
    if (esRef.current) {
      esRef.current.close();
      esRef.current = null;
    }

    if (!jobId) {
      queueMicrotask(() => setState({ kind: "idle" }));
      return;
    }

    queueMicrotask(() => setState({ kind: "connecting" }));

    const es = new EventSource(`/api/agents/ic/stream/${jobId}`);
    esRef.current = es;

    es.addEventListener("step", (e: MessageEvent) => {
      try {
        const step = JSON.parse(e.data as string) as IcStep;
        const msg: AgentMessageData = {
          agent: step.agent ?? step.role ?? "Agent",
          content: step.content ?? step.message ?? "",
          kind:
            step.kind === "user"
              ? "user"
              : step.kind === "system"
                ? "system"
                : "agent",
        };
        setState((prev) => {
          const prevSteps =
            prev.kind === "streaming" || prev.kind === "done"
              ? prev.steps
              : [];
          return { kind: "streaming", steps: [...prevSteps, msg] };
        });
      } catch {
        // malformed step — ignore
      }
    });

    es.addEventListener("done", (e: MessageEvent) => {
      try {
        const payload = JSON.parse(e.data as string) as IcDonePayload;
        const decision =
          payload.decision ?? payload.summary ?? payload.result ?? "결정 없음";
        setState((prev) => ({
          kind: "done",
          steps: prev.kind === "streaming" || prev.kind === "done" ? prev.steps : [],
          decision,
        }));
      } catch {
        setState((prev) => ({
          kind: "done",
          steps: prev.kind === "streaming" || prev.kind === "done" ? prev.steps : [],
          decision: "결정 없음 (파싱 실패)",
        }));
      }
      es.close();
      esRef.current = null;
    });

    es.addEventListener("error", (e: MessageEvent) => {
      try {
        const payload = JSON.parse(e.data as string) as { message?: string };
        setState({ kind: "error", message: payload.message ?? "스트림 오류" });
      } catch {
        setState({ kind: "error", message: "스트림 오류" });
      }
      es.close();
      esRef.current = null;
    });

    // Native onerror fires on connection failures (network, 4xx/5xx)
    es.onerror = () => {
      // Only transition to disconnected if we haven't already finished
      setState((prev) => {
        if (prev.kind === "done" || prev.kind === "error") return prev;
        return { kind: "disconnected" };
      });
      es.close();
      esRef.current = null;
    };

    return () => {
      es.close();
      esRef.current = null;
    };
  }, [jobId]);

  if (state.kind === "idle") return null;

  return (
    <div
      className={cn(
        "flex flex-col gap-2 rounded-xl border border-border p-4",
        className,
      )}
      aria-label="IC 실행 트랜스크립트"
      data-testid="ic-transcript"
    >
      {(state.kind === "connecting") && (
        <p className="text-sm text-muted-foreground" role="status">
          연결 중…
        </p>
      )}

      {(state.kind === "streaming" || state.kind === "done") &&
        state.steps.map((msg, i) => (
          <AgentMessage key={i} message={msg} />
        ))}

      {state.kind === "streaming" && (
        <div className="flex items-center gap-2 text-xs text-muted-foreground" role="status">
          <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-brand" />
          스트리밍 중…
        </div>
      )}

      {state.kind === "done" && (
        <div
          className="mt-2 rounded-xl bg-muted p-3 text-sm"
          role="region"
          aria-label="IC 최종 결정"
          data-testid="ic-decision"
        >
          <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            최종 결정
          </p>
          <p className="text-foreground">{state.decision}</p>
        </div>
      )}

      {state.kind === "error" && (
        <div role="alert" className="rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
          오류: {state.message}
        </div>
      )}

      {state.kind === "disconnected" && (
        <div role="alert" className="rounded-lg border border-amber-400/40 bg-amber-50 p-3 text-sm text-amber-800 dark:bg-amber-900/20 dark:text-amber-300">
          연결 끊김. 페이지를 새로고침하거나 다시 시도해 주세요.
        </div>
      )}
    </div>
  );
}
