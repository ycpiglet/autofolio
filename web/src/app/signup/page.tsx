"use client";

import Link from "next/link";
import { useState } from "react";
import {
  ApiError,
  postMembershipRequest,
  postMembershipRequestStatus,
  type MembershipRequestResponse,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type SubmitState =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "submitted"; request: MembershipRequestResponse }
  | { kind: "error"; message: string };

type LookupState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "found"; request: MembershipRequestResponse }
  | { kind: "error"; message: string };

function apiErrorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    if (typeof err.body === "object" && err.body && "detail" in err.body) {
      const detail = (err.body as { detail?: unknown }).detail;
      if (typeof detail === "string") return detail;
    }
    return err.message;
  }
  return "가입 승인 신청을 저장하지 못했습니다.";
}

function formatKrw(value: number): string {
  return `${new Intl.NumberFormat("ko-KR").format(value)}원`;
}

function statusLabel(status: MembershipRequestResponse["status"]): string {
  const labels: Record<MembershipRequestResponse["status"], string> = {
    requested: "신청 접수",
    verification_pending: "Owner 확인 중",
    deposit_pending: "입금 확인 대기",
    active: "승인 완료",
    rejected: "거절",
    expired: "만료",
  };
  return labels[status] ?? status;
}

function DepositInstruction({ request }: { request: MembershipRequestResponse }) {
  const instruction = request.deposit_instruction;
  if (!instruction) {
    return (
      <p className="text-sm leading-relaxed text-muted-foreground">
        Owner 확인 후 승인 대상에게 입금 안내가 표시됩니다.
      </p>
    );
  }
  return (
    <div className="space-y-3 rounded-lg border border-border bg-muted/30 p-4">
      <div className="grid gap-3 text-sm sm:grid-cols-2">
        <div>
          <div className="text-xs font-medium text-muted-foreground">입금 금액</div>
          <div className="mt-1 font-semibold text-foreground">
            {formatKrw(instruction.price_krw)}
          </div>
        </div>
        <div>
          <div className="text-xs font-medium text-muted-foreground">입금 코드</div>
          <div className="mt-1 font-mono font-semibold text-foreground">
            {instruction.deposit_code}
          </div>
        </div>
        <div>
          <div className="text-xs font-medium text-muted-foreground">은행</div>
          <div className="mt-1 font-semibold text-foreground">
            {instruction.bank_name ?? "Owner 안내 대기"}
          </div>
        </div>
        <div>
          <div className="text-xs font-medium text-muted-foreground">예금주</div>
          <div className="mt-1 font-semibold text-foreground">
            {instruction.account_holder ?? "Owner 안내 대기"}
          </div>
        </div>
      </div>
      <div>
        <div className="text-xs font-medium text-muted-foreground">계좌번호</div>
        <div className="mt-1 font-mono text-base font-semibold text-foreground">
          {instruction.account_number ?? "Owner 안내 대기"}
        </div>
      </div>
      {instruction.due_at && (
        <p className="text-xs text-muted-foreground">
          입금 확인 기한: {new Date(instruction.due_at).toLocaleString("ko-KR")}
        </p>
      )}
      {!instruction.account_configured && (
        <p className="text-xs text-muted-foreground">
          현재 런타임 계좌 설정이 없어 Owner가 별도로 안내해야 합니다.
        </p>
      )}
    </div>
  );
}

export default function SignupPage() {
  const [displayName, setDisplayName] = useState("");
  const [contact, setContact] = useState("");
  const [referralSource, setReferralSource] = useState("");
  const [note, setNote] = useState("");
  const [state, setState] = useState<SubmitState>({ kind: "idle" });
  const [lookupRequestId, setLookupRequestId] = useState("");
  const [lookupContact, setLookupContact] = useState("");
  const [lookupState, setLookupState] = useState<LookupState>({ kind: "idle" });

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setState({ kind: "submitting" });
    try {
      const request = await postMembershipRequest({
        display_name: displayName,
        contact,
        plan: "pilot_monthly",
        referral_source: referralSource || undefined,
        note: note || undefined,
      });
      setState({ kind: "submitted", request });
      setLookupRequestId(request.request_id);
      setLookupContact(request.contact);
      setLookupState({ kind: "found", request });
    } catch (err) {
      setState({ kind: "error", message: apiErrorMessage(err) });
    }
  }

  async function handleLookup(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLookupState({ kind: "loading" });
    try {
      const request = await postMembershipRequestStatus({
        request_id: lookupRequestId,
        contact: lookupContact,
      });
      setLookupState({ kind: "found", request });
    } catch (err) {
      setLookupState({ kind: "error", message: apiErrorMessage(err) });
    }
  }

  return (
    <main className="min-h-screen bg-page px-4 py-10 text-foreground">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-8">
        <header className="flex flex-col gap-3">
          <Link href="/login" className="text-sm font-medium text-brand hover:underline">
            Autofolio 로그인
          </Link>
          <div className="max-w-2xl">
            <h1 className="text-3xl font-bold leading-tight md:text-4xl">
              검증된 사용자 가입 승인
            </h1>
            <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
              Autofolio는 승인 기반 웹 서비스입니다. 신청 후 Owner가 사람을 확인하고,
              유료 파일럿은 무통장입금 확인 뒤 계정을 활성화합니다.
            </p>
          </div>
        </header>

        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_22rem]">
          <Card>
            <CardHeader>
              <CardTitle>가입 승인 신청</CardTitle>
              <CardDescription>
                신청은 계정 생성이 아니며, 승인 전에는 로그인할 수 없습니다.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {state.kind === "submitted" ? (
                <div className="space-y-5">
                  <div className="rounded-lg border border-border bg-muted/30 p-4">
                    <div className="text-xs font-medium text-muted-foreground">신청 ID</div>
                    <div className="mt-1 font-mono text-lg font-semibold">
                      {state.request.request_id}
                    </div>
                    <div className="mt-3 text-xs font-medium text-muted-foreground">상태</div>
                    <div className="mt-1 text-sm font-semibold">
                      {statusLabel(state.request.status)}
                    </div>
                    <p className="mt-3 text-sm text-muted-foreground">
                      {state.request.message}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button nativeButton={false} render={<Link href="/login" />}>
                      로그인으로 돌아가기
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setState({ kind: "idle" })}
                    >
                      다른 신청 작성
                    </Button>
                  </div>
                </div>
              ) : (
                <form className="space-y-4" onSubmit={handleSubmit}>
                  <div className="grid gap-4 sm:grid-cols-2">
                    <div className="flex flex-col gap-1.5">
                      <Label htmlFor="display-name">이름 또는 별칭</Label>
                      <Input
                        id="display-name"
                        value={displayName}
                        onChange={(event) => setDisplayName(event.target.value)}
                        required
                        maxLength={80}
                        autoComplete="name"
                      />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <Label htmlFor="contact">연락처</Label>
                      <Input
                        id="contact"
                        value={contact}
                        onChange={(event) => setContact(event.target.value)}
                        required
                        maxLength={160}
                        autoComplete="email"
                        placeholder="이메일 또는 연락 가능한 식별자"
                      />
                    </div>
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <div className="flex flex-col gap-1.5">
                      <Label htmlFor="plan">플랜</Label>
                      <select
                        id="plan"
                        className="h-8 rounded-lg border border-input bg-background px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                        value="pilot_monthly"
                        disabled
                      >
                        <option value="pilot_monthly">파일럿 월 20,000원</option>
                      </select>
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <Label htmlFor="referral-source">소개자 또는 확인 경로</Label>
                      <Input
                        id="referral-source"
                        value={referralSource}
                        onChange={(event) => setReferralSource(event.target.value)}
                        maxLength={120}
                        placeholder="예: Owner 지인, 테스트 그룹"
                      />
                    </div>
                  </div>

                  <div className="flex flex-col gap-1.5">
                    <Label htmlFor="note">메모</Label>
                    <textarea
                      id="note"
                      className="min-h-24 rounded-lg border border-input bg-background px-2.5 py-2 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                      value={note}
                      onChange={(event) => setNote(event.target.value)}
                      maxLength={500}
                      placeholder="사용 목적이나 Owner가 확인할 내용을 적어주세요."
                    />
                  </div>

                  {state.kind === "error" && (
                    <p role="alert" className="text-sm text-destructive">
                      {state.message}
                    </p>
                  )}

                  <Button type="submit" disabled={state.kind === "submitting"} aria-busy={state.kind === "submitting"}>
                    {state.kind === "submitting" ? "접수 중..." : "가입 승인 신청"}
                  </Button>
                </form>
              )}
            </CardContent>
          </Card>

          <aside className="space-y-4">
            <div className="rounded-lg border border-border bg-surface p-4">
              <h2 className="text-sm font-semibold">신청 상태 확인</h2>
              <form className="mt-3 space-y-3" onSubmit={handleLookup}>
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="lookup-request-id">신청 ID</Label>
                  <Input
                    id="lookup-request-id"
                    value={lookupRequestId}
                    onChange={(event) => setLookupRequestId(event.target.value)}
                    required
                    maxLength={80}
                    placeholder="mrq_..."
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="lookup-contact">연락처</Label>
                  <Input
                    id="lookup-contact"
                    value={lookupContact}
                    onChange={(event) => setLookupContact(event.target.value)}
                    required
                    maxLength={160}
                    placeholder="신청 때 입력한 연락처"
                  />
                </div>
                <Button type="submit" variant="outline" disabled={lookupState.kind === "loading"}>
                  {lookupState.kind === "loading" ? "확인 중..." : "상태 확인"}
                </Button>
              </form>

              {lookupState.kind === "error" && (
                <p role="alert" className="mt-3 text-sm text-destructive">
                  {lookupState.message}
                </p>
              )}
              {lookupState.kind === "found" && (
                <div className="mt-4 space-y-3">
                  <div className="rounded-lg border border-border bg-muted/20 p-3">
                    <div className="text-xs font-medium text-muted-foreground">현재 상태</div>
                    <div className="mt-1 text-sm font-semibold">
                      {statusLabel(lookupState.request.status)}
                    </div>
                    <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
                      {lookupState.request.message}
                    </p>
                  </div>
                  <DepositInstruction request={lookupState.request} />
                </div>
              )}
            </div>

            <div className="rounded-lg border border-border bg-surface p-4">
              <h2 className="text-sm font-semibold">승인 흐름</h2>
              <ol className="mt-3 space-y-2 text-sm text-muted-foreground">
                <li>1. 가입 승인 신청 접수</li>
                <li>2. Owner가 사람과 사용 범위 확인</li>
                <li>3. 승인 대상에게 입금 안내와 고유 코드 제공</li>
                <li>4. 입금 확인 후 계정 활성화</li>
              </ol>
            </div>
            <div className="rounded-lg border border-border bg-surface p-4">
              <h2 className="text-sm font-semibold">안전 경계</h2>
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                이 화면은 신청만 접수합니다. 계좌번호는 repository에 저장하지 않으며,
                운영 설정 또는 Owner 안내를 통해 승인 대상에게만 표시됩니다.
              </p>
            </div>
          </aside>
        </div>
      </div>
    </main>
  );
}
