"use client";

import { useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/AppShell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  ApiError,
  getAcknowledgementStatus,
  getManual,
  getManuals,
  postAcknowledgement,
  type AcknowledgementStatusResponse,
  type ManualDetail,
  type ManualSummary,
} from "@/lib/api";
import { cn } from "@/lib/utils";

const ACK_TEXT = "실전 거래의 손실 가능성과 자동화 오류 가능성을 이해하며 최종 책임이 계좌 소유자에게 있음을 확인합니다.";

type AckState =
  | { kind: "idle" }
  | { kind: "saving" }
  | { kind: "saved" }
  | { kind: "error"; message: string };

function MarkdownView({ content }: { content: string }) {
  const lines = content.split(/\r?\n/);
  return (
    <div className="space-y-3 text-sm leading-6 text-foreground">
      {lines.map((line, index) => {
        const key = `${index}-${line.slice(0, 12)}`;
        if (!line.trim()) return <div key={key} className="h-1" />;
        if (line.startsWith("# ")) {
          return <h2 key={key} className="text-lg font-semibold text-foreground">{line.slice(2)}</h2>;
        }
        if (line.startsWith("## ")) {
          return <h3 key={key} className="pt-2 text-base font-semibold text-foreground">{line.slice(3)}</h3>;
        }
        if (line.startsWith("- ")) {
          return <p key={key} className="pl-4 before:mr-2 before:content-['•']">{line.slice(2)}</p>;
        }
        if (/^\d+\.\s/.test(line)) {
          return <p key={key} className="pl-4">{line}</p>;
        }
        return <p key={key}>{line}</p>;
      })}
    </div>
  );
}

function ManualSelector({
  manuals,
  activeSlug,
  onSelect,
}: {
  manuals: ManualSummary[];
  activeSlug: string;
  onSelect: (slug: string) => void;
}) {
  const sections = useMemo(() => {
    const grouped = new Map<string, ManualSummary[]>();
    for (const manual of manuals) {
      const key = manual.ui_section || "manuals";
      grouped.set(key, [...(grouped.get(key) ?? []), manual]);
    }
    return Array.from(grouped.entries());
  }, [manuals]);

  return (
    <aside className="space-y-4 lg:w-72">
      {sections.map(([section, items]) => (
        <div key={section} className="space-y-1">
          <div className="px-1 text-xs font-medium uppercase text-muted-foreground">{section}</div>
          {items.map((manual) => (
            <button
              key={manual.slug}
              type="button"
              onClick={() => onSelect(manual.slug)}
              className={cn(
                "w-full rounded-lg border px-3 py-2 text-left text-sm transition-colors",
                activeSlug === manual.slug
                  ? "border-primary bg-primary/10 text-foreground"
                  : "border-border text-muted-foreground hover:bg-muted",
              )}
            >
              <div className="font-medium">{manual.title}</div>
              <div className="mt-1 flex gap-1">
                <Badge variant={manual.visibility === "private" ? "secondary" : "outline"}>
                  {manual.visibility}
                </Badge>
                <Badge variant={manual.risk_level === "critical" ? "destructive" : "outline"}>
                  {manual.risk_level}
                </Badge>
              </div>
            </button>
          ))}
        </div>
      ))}
    </aside>
  );
}

function AcknowledgementPanel({
  manual,
  status,
}: {
  manual: ManualDetail;
  status?: AcknowledgementStatusResponse;
}) {
  const queryClient = useQueryClient();
  const [text, setText] = useState(ACK_TEXT);
  const [currentPassword, setCurrentPassword] = useState("");
  const [state, setState] = useState<AckState>({ kind: "idle" });
  const alreadyDone =
    manual.ack_kind === "live_trading_risk_v1" && status?.live_trading_acknowledged;

  async function handleSubmit() {
    if (!manual.ack_kind) return;
    setState({ kind: "saving" });
    try {
      await postAcknowledgement({
        kind: manual.ack_kind,
        document_slug: manual.slug,
        document_version: manual.version,
        acknowledgement_text: text,
        current_password: currentPassword || undefined,
      });
      setState({ kind: "saved" });
      setCurrentPassword("");
      void queryClient.invalidateQueries({ queryKey: ["ack-status"] });
    } catch (err) {
      const message =
        err instanceof ApiError
          ? JSON.stringify(err.body)
          : "동의를 기록하지 못했습니다.";
      setState({ kind: "error", message });
    }
  }

  if (!manual.requires_ack) return null;

  return (
    <section className="space-y-3 rounded-lg border border-amber-400/40 bg-amber-50 p-4 text-sm text-amber-950 dark:bg-amber-900/20 dark:text-amber-200">
      <div className="flex items-center justify-between gap-3">
        <h3 className="font-semibold">실전 거래 확인</h3>
        <Badge variant={alreadyDone ? "default" : "secondary"}>
          {alreadyDone ? "기록됨" : "필요"}
        </Badge>
      </div>
      <p>{status?.message ?? "실전 거래 전 위험 고지 확인이 필요합니다."}</p>
      <p>
        Authenticator 사용을 권장합니다. 현재 TOTP 강제는 준비 중이며, 비밀번호 재확인을 입력하면
        동의 기록에 재인증으로 남습니다.
      </p>
      <textarea
        value={text}
        onChange={(event) => setText(event.target.value)}
        className="min-h-24 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/50"
        aria-label="위험 고지 확인 문구"
      />
      <input
        type="password"
        value={currentPassword}
        onChange={(event) => setCurrentPassword(event.target.value)}
        className="h-9 w-full rounded-lg border border-input bg-background px-3 text-sm text-foreground outline-none focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/50"
        placeholder="현재 비밀번호 (선택, 입력 시 재인증 기록)"
        aria-label="현재 비밀번호"
      />
      <Button onClick={() => void handleSubmit()} disabled={state.kind === "saving"}>
        {state.kind === "saving" ? "기록 중..." : "위험 고지 확인 기록"}
      </Button>
      {state.kind === "saved" && <p role="status">기록되었습니다.</p>}
      {state.kind === "error" && <p role="alert" className="text-destructive">{state.message}</p>}
    </section>
  );
}

export default function ManualsPage() {
  const manualsQuery = useQuery({
    queryKey: ["manuals"],
    queryFn: getManuals,
    staleTime: 60_000,
  });
  const ackQuery = useQuery({
    queryKey: ["ack-status"],
    queryFn: getAcknowledgementStatus,
    staleTime: 30_000,
  });
  const manuals = manualsQuery.data?.manuals ?? [];
  const [activeSlug, setActiveSlug] = useState("");
  const selectedSlug = activeSlug || manuals[0]?.slug || "";

  const manualQuery = useQuery({
    queryKey: ["manual", selectedSlug],
    queryFn: () => getManual(selectedSlug),
    enabled: Boolean(selectedSlug),
    staleTime: 60_000,
  });

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-base font-semibold text-foreground">매뉴얼</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              화면에서 읽고 확인하는 제품 안내와 운영 절차입니다.
            </p>
          </div>
          {ackQuery.data && (
            <Badge variant={ackQuery.data.live_trading_acknowledged ? "default" : "secondary"}>
              실전 고지 {ackQuery.data.live_trading_acknowledged ? "완료" : "필요"}
            </Badge>
          )}
        </div>

        <div className="grid gap-6 lg:grid-cols-[288px_1fr]">
          <ManualSelector
            manuals={manuals}
            activeSlug={selectedSlug}
            onSelect={setActiveSlug}
          />
          <article className="min-h-[520px] rounded-lg border border-border bg-surface p-5">
            {manualsQuery.isPending || manualQuery.isPending ? (
              <div className="h-64 animate-pulse rounded-lg bg-muted" />
            ) : manualQuery.error ? (
              <p role="alert" className="text-sm text-destructive">문서를 불러오지 못했습니다.</p>
            ) : manualQuery.data ? (
              <div className="space-y-5">
                <div className="flex flex-wrap gap-2">
                  <Badge variant={manualQuery.data.visibility === "private" ? "secondary" : "outline"}>
                    {manualQuery.data.visibility}
                  </Badge>
                  <Badge variant={manualQuery.data.risk_level === "critical" ? "destructive" : "outline"}>
                    {manualQuery.data.risk_level}
                  </Badge>
                  <Badge variant="outline">v {manualQuery.data.version}</Badge>
                </div>
                <MarkdownView content={manualQuery.data.content} />
                <AcknowledgementPanel manual={manualQuery.data} status={ackQuery.data} />
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">표시할 문서가 없습니다.</p>
            )}
          </article>
        </div>
      </div>
    </AppShell>
  );
}
