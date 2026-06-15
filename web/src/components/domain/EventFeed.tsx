// web/src/components/domain/EventFeed.tsx
"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { cn } from "@/lib/utils";

export interface FeedEvent {
  id: string;
  kind: string;
  ts?: string;
  message?: string;
  symbol?: string;
  price?: number;
  [key: string]: unknown;
}

type FeedState =
  | { kind: "connecting" }
  | { kind: "live"; events: FeedEvent[] }
  | { kind: "disconnected"; events: FeedEvent[] }
  | { kind: "empty" };

const KIND_LABELS: Record<string, string> = {
  price: "가격",
  engine: "엔진",
  order: "주문",
  alert: "알림",
  tick: "틱",
};

function kindLabel(kind: string): string {
  return KIND_LABELS[kind] ?? kind;
}

function kindBadgeClass(kind: string): string {
  switch (kind) {
    case "price":
      return "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300";
    case "engine":
      return "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300";
    case "order":
      return "bg-brand/10 text-brand";
    case "alert":
      return "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300";
    default:
      return "bg-muted text-muted-foreground";
  }
}

interface EventFeedProps {
  /** Maximum events to display (oldest are dropped when exceeded) */
  maxEvents?: number;
  className?: string;
}

/**
 * EventFeed — live notifications feed via EventSource on /api/stream/events.
 *
 * Newest event is always on top. Shows connecting/disconnected states.
 * Cleans up EventSource on unmount.
 */
export function EventFeed({ maxEvents = 100, className }: EventFeedProps) {
  const [state, setState] = useState<FeedState>({ kind: "connecting" });
  const esRef = useRef<EventSource | null>(null);
  const retryRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (esRef.current) {
      esRef.current.close();
      esRef.current = null;
    }

    setState((prev) => {
      // preserve existing events while reconnecting
      const existingEvents =
        prev.kind === "live" || prev.kind === "disconnected"
          ? prev.events
          : [];
      return existingEvents.length > 0
        ? { kind: "disconnected", events: existingEvents }
        : { kind: "connecting" };
    });

    const es = new EventSource("/api/stream/events");
    esRef.current = es;

    es.onmessage = (e: MessageEvent) => {
      try {
        const raw = JSON.parse(e.data as string) as Record<string, unknown>;
        const event: FeedEvent = {
          id: String(raw.id ?? Date.now()),
          kind: String(raw.kind ?? raw.type ?? "unknown"),
          ts: (raw.ts as string | undefined) ?? new Date().toISOString(),
          message: raw.message as string | undefined,
          symbol: raw.symbol as string | undefined,
          price: raw.price as number | undefined,
          ...raw,
        };
        setState((prev) => {
          const existing =
            prev.kind === "live" || prev.kind === "disconnected"
              ? prev.events
              : [];
          const updated = [event, ...existing].slice(0, maxEvents);
          return { kind: "live", events: updated };
        });
      } catch {
        // ignore malformed messages
      }
    };

    // Handle named events too (price, engine, etc.)
    ["price", "engine", "order", "alert", "tick"].forEach((eventName) => {
      es.addEventListener(eventName, (e: MessageEvent) => {
        try {
          const raw = JSON.parse(e.data as string) as Record<string, unknown>;
          const event: FeedEvent = {
            id: String(raw.id ?? Date.now()),
            kind: eventName,
            ts: (raw.ts as string | undefined) ?? new Date().toISOString(),
            message: raw.message as string | undefined,
            symbol: raw.symbol as string | undefined,
            price: raw.price as number | undefined,
            ...raw,
          };
          setState((prev) => {
            const existing =
              prev.kind === "live" || prev.kind === "disconnected"
                ? prev.events
                : [];
            const updated = [event, ...existing].slice(0, maxEvents);
            return { kind: "live", events: updated };
          });
        } catch {
          // ignore
        }
      });
    });

    es.onerror = () => {
      setState((prev) => {
        const existingEvents =
          prev.kind === "live" || prev.kind === "disconnected"
            ? prev.events
            : [];
        return { kind: "disconnected", events: existingEvents };
      });
      es.close();
      esRef.current = null;
    };
  }, [maxEvents]);

  useEffect(() => {
    connect();
    return () => {
      if (retryRef.current) clearTimeout(retryRef.current);
      if (esRef.current) {
        esRef.current.close();
        esRef.current = null;
      }
    };
  }, [connect]);

  function handleRetry() {
    connect();
  }

  const events =
    state.kind === "live" || state.kind === "disconnected" ? state.events : [];

  return (
    <div
      className={cn("flex flex-col gap-3", className)}
      aria-label="알림 피드"
      data-testid="event-feed"
    >
      {/* Connection status bar */}
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-medium text-foreground">라이브 알림</h2>
        <div className="flex items-center gap-2">
          {state.kind === "connecting" && (
            <span className="text-xs text-muted-foreground" role="status">
              연결 중…
            </span>
          )}
          {state.kind === "live" && (
            <span className="flex items-center gap-1 text-xs text-muted-foreground" role="status">
              <span className="inline-block h-1.5 w-1.5 rounded-full bg-green-500" aria-hidden />
              연결됨
            </span>
          )}
          {state.kind === "disconnected" && (
            <>
              <span className="text-xs text-amber-600" role="alert">
                연결 끊김
              </span>
              <button
                className="rounded px-2 py-0.5 text-xs text-brand underline-offset-2 hover:underline"
                onClick={handleRetry}
                aria-label="다시 연결"
              >
                다시 연결
              </button>
            </>
          )}
        </div>
      </div>

      {/* Feed list */}
      {state.kind === "connecting" && events.length === 0 && (
        <div
          className="rounded-xl border border-dashed border-border p-8 text-center text-sm text-muted-foreground"
          role="status"
          aria-label="이벤트 피드 연결 중"
          data-testid="feed-connecting"
        >
          이벤트를 기다리는 중…
        </div>
      )}

      {events.length === 0 && state.kind !== "connecting" && (
        <div
          className="rounded-xl border border-dashed border-border p-8 text-center text-sm text-muted-foreground"
          role="status"
          aria-label="이벤트 없음"
        >
          아직 이벤트가 없습니다.
        </div>
      )}

      {events.length > 0 && (
        <ul className="flex flex-col gap-1.5" role="list" aria-label="이벤트 목록" data-testid="feed-list">
          {events.map((ev) => (
            <li
              key={ev.id}
              className="flex items-start gap-2 rounded-lg border border-border bg-card px-3 py-2 text-sm"
              role="listitem"
            >
              <span
                className={cn(
                  "mt-0.5 shrink-0 rounded-full px-1.5 py-0.5 text-xs font-semibold",
                  kindBadgeClass(ev.kind),
                )}
                aria-label={`종류: ${kindLabel(ev.kind)}`}
              >
                {kindLabel(ev.kind)}
              </span>
              <div className="flex-1 min-w-0">
                {ev.message && (
                  <p className="text-foreground">{ev.message}</p>
                )}
                {ev.symbol && (
                  <p className="font-mono text-xs text-muted-foreground">
                    {ev.symbol}
                    {ev.price !== undefined ? ` ₩${Number(ev.price).toLocaleString("ko-KR")}` : ""}
                  </p>
                )}
                {!ev.message && !ev.symbol && (
                  <p className="font-mono text-xs text-muted-foreground">
                    {JSON.stringify(ev)}
                  </p>
                )}
              </div>
              {ev.ts && (
                <time
                  dateTime={ev.ts}
                  className="shrink-0 text-xs text-muted-foreground"
                  aria-label={`시각: ${ev.ts}`}
                >
                  {new Date(ev.ts).toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                </time>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
