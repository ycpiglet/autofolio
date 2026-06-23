"use client";

import Link from "next/link";
import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type MouseEvent as ReactMouseEvent,
  type PointerEvent,
} from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/AppShell";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  ApiError,
  getInvestorProfile,
  getInvestorSurvey,
  postInvestorSurvey,
  type InvestorProfileResponse,
  type SurveyCategory,
  type SurveyQuestion,
} from "@/lib/api";
import { cn } from "@/lib/utils";

type Answers = Record<string, unknown>;
type SignatureAnswer = {
  name: string;
  confirmation_text: string;
  signature_data_url: string;
  signed_at: string;
};
type SubmitStatus =
  | { kind: "idle" }
  | { kind: "saving" }
  | { kind: "saved"; profile: InvestorProfileResponse }
  | { kind: "error"; message: string };

/** A question annotated with its global running number (1..N across all categories). */
type NumberedQuestion = { question: SurveyQuestion; number: number };
const REQUIRED_CONFIRMATION_TEXT = "위 항목을 모두 이해했습니다.";

export default function InvestorProfileOnboardingPage() {
  const queryClient = useQueryClient();
  const [answers, setAnswers] = useState<Answers>({});
  const [status, setStatus] = useState<SubmitStatus>({ kind: "idle" });
  const [shakeId, setShakeId] = useState<string | null>(null);
  const [invalidIds, setInvalidIds] = useState<Set<string>>(new Set());
  const cardRefs = useRef<Map<string, HTMLElement>>(new Map());

  const surveyQuery = useQuery({
    queryKey: ["investor-survey"],
    queryFn: getInvestorSurvey,
    staleTime: 300_000,
  });

  const profileQuery = useQuery({
    queryKey: ["investor-profile"],
    queryFn: getInvestorProfile,
    staleTime: 60_000,
  });

  const questions = useMemo(
    () => surveyQuery.data?.questions ?? [],
    [surveyQuery.data?.questions],
  );
  const categories = useMemo(
    () => surveyQuery.data?.categories ?? [],
    [surveyQuery.data?.categories],
  );

  /**
   * Assign each question a GLOBAL running number (1..N) in category order, then
   * by the question order within `questions`. Questions whose category is not a
   * known category are appended at the end (defensive fallback) but still numbered.
   */
  const numberedByCategory = useMemo(() => {
    const result: Array<{ category: SurveyCategory; items: NumberedQuestion[] }> = [];
    let counter = 0;
    const seen = new Set<string>();

    for (const category of categories) {
      const items: NumberedQuestion[] = [];
      for (const question of questions) {
        if (question.category === category.key) {
          counter += 1;
          items.push({ question, number: counter });
          seen.add(question.id);
        }
      }
      result.push({ category, items });
    }

    // Defensive fallback: any question not matched by a known category.
    const orphans: NumberedQuestion[] = [];
    for (const question of questions) {
      if (!seen.has(question.id)) {
        counter += 1;
        orphans.push({ question, number: counter });
      }
    }

    return { groups: result, orphans };
  }, [categories, questions]);

  const completion = useMemo(() => {
    if (questions.length === 0) return 0;
    const answered = questions.filter((question) => hasAnswer(question, answers)).length;
    return Math.round((answered / questions.length) * 100);
  }, [answers, questions]);

  function registerCard(id: string) {
    return (element: HTMLElement | null) => {
      if (element) cardRefs.current.set(id, element);
      else cardRefs.current.delete(id);
    };
  }

  async function handleSubmit() {
    const missing = questions.filter((question) => !hasAnswer(question, answers));
    if (missing.length > 0) {
      const first = missing[0];
      const firstIssue = questionIssue(first, answers);
      setStatus({
        kind: "error",
        message:
          missing.length === 1
            ? firstIssue ?? `${first.title} 항목을 완료하세요.`
            : `${firstIssue ?? `${first.title} 항목을 완료하세요.`} 외 ${missing.length - 1}개 항목을 완료하세요.`,
      });
      setInvalidIds(new Set());
      window.requestAnimationFrame(() => {
        setInvalidIds(new Set(missing.map((question) => question.id)));
      });
      setShakeId(first.id);
      const ref = cardRefs.current.get(first.id);
      ref?.scrollIntoView({ behavior: "smooth", block: "center" });
      if (typeof navigator !== "undefined" && "vibrate" in navigator) {
        navigator.vibrate([60, 40, 60]);
      }
      window.setTimeout(() => setShakeId(null), 600);
      return;
    }
    setStatus({ kind: "saving" });
    try {
      const result = await postInvestorSurvey(answers);
      setStatus({ kind: "saved", profile: result.profile });
      await queryClient.invalidateQueries({ queryKey: ["investor-profile"] });
    } catch (err) {
      let message = "진단 결과를 저장하지 못했습니다.";
      if (err instanceof ApiError) {
        const detail = err.body as { detail?: string } | undefined;
        message = detail?.detail ?? err.message;
      } else if (err instanceof Error && err.message.startsWith("CSRF fetch failed: 401")) {
        message = "승인된 계정으로 로그인한 뒤 프로필을 저장할 수 있습니다.";
      }
      setStatus({ kind: "error", message });
    }
  }

  const activeProfile =
    status.kind === "saved" ? status.profile : profileQuery.data;

  function renderQuestion({ question, number }: NumberedQuestion) {
    return (
      <QuestionBlock
        key={question.id}
        index={number}
        question={question}
        value={answers[question.id]}
        shaking={shakeId === question.id}
        invalid={invalidIds.has(question.id)}
        registerRef={registerCard(question.id)}
        onAnimationEnd={() => {
          if (shakeId === question.id) setShakeId(null);
        }}
        onChange={(value) => {
          setStatus({ kind: "idle" });
          setInvalidIds((prev) => {
            if (!prev.has(question.id)) return prev;
            const next = new Set(prev);
            next.delete(question.id);
            return next;
          });
          setAnswers((prev) => ({ ...prev, [question.id]: value }));
        }}
      />
    );
  }

  return (
    <AppShell className="p-0">
      <div className="border-b border-border bg-surface px-6 py-5">
        <div className="mx-auto flex max-w-5xl flex-col gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-lg font-semibold text-foreground">투자자 성향 진단</h1>
            <Badge variant={activeProfile?.completed ? "default" : "secondary"}>
              {activeProfile?.completed ? activeProfile.risk_type : "미완료"}
            </Badge>
            {activeProfile?.needs_advanced_survey && (
              <Badge variant="outline">심화 설문 권장</Badge>
            )}
          </div>
          <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
            투자 목표·위험성향·투자지식·경험·자동화 선호를 차례로 진단하고, 마지막에 확인·동의를
            거쳐 제안과 경고를 개인화합니다.
          </p>
        </div>
      </div>

      <div className="mx-auto grid max-w-5xl gap-6 px-6 py-6 lg:grid-cols-[1fr_280px]">
        <div className="space-y-6">
          {/* Slim sticky progress strip for small screens (aside drops below the grid). */}
          <div className="sticky top-0 z-10 -mx-6 mb-2 border-b border-border bg-surface/95 px-6 py-2 backdrop-blur lg:hidden">
            <div className="flex items-center justify-between gap-3">
              <div className="h-1.5 flex-1 rounded-full bg-muted">
                <div
                  className="h-1.5 rounded-full bg-primary transition-all"
                  style={{ width: `${completion}%` }}
                />
              </div>
              <span className="shrink-0 text-xs font-medium text-muted-foreground">
                {completion}% 완료
              </span>
            </div>
          </div>

          {surveyQuery.isPending && (
            <div className="h-48 animate-pulse rounded-lg bg-muted" />
          )}
          {surveyQuery.error && (
            <p role="alert" className="rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
              설문을 불러오지 못했습니다.
            </p>
          )}

          {numberedByCategory.groups.map(({ category, items }) =>
            items.length === 0 ? null : (
              <section key={category.key} className="space-y-3">
                <div className="space-y-1">
                  <h2 className="text-base font-bold text-foreground">{category.title}</h2>
                  {category.description && (
                    <p className="text-sm text-muted-foreground">{category.description}</p>
                  )}
                </div>
                <div className="space-y-3 rounded-xl border border-border bg-surface/40 p-3">
                  {items.map(renderQuestion)}
                </div>
              </section>
            ),
          )}

          {numberedByCategory.orphans.length > 0 && (
            <section className="space-y-3">
              <div className="space-y-3 rounded-xl border border-border bg-surface/40 p-3">
                {numberedByCategory.orphans.map(renderQuestion)}
              </div>
            </section>
          )}

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Button
              onClick={() => void handleSubmit()}
              disabled={status.kind === "saving" || surveyQuery.isPending}
            >
              {status.kind === "saving" ? "저장 중…" : "진단 저장"}
            </Button>
            <Button variant="outline" nativeButton={false} render={<Link href="/home" />}>
              홈으로
            </Button>
            {status.kind === "error" && (
              <p role="alert" className="text-sm text-destructive">
                {status.message}
              </p>
            )}
          </div>
        </div>

        <aside className="space-y-4">
          <div className="sticky top-6 space-y-4">
            <Card size="sm">
              <CardHeader>
                <CardTitle>진행률</CardTitle>
                <CardDescription>{completion}% 완료</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-2 rounded-full bg-muted">
                  <div
                    className="h-2 rounded-full bg-primary transition-all"
                    style={{ width: `${completion}%` }}
                  />
                </div>
              </CardContent>
            </Card>

            {activeProfile && <ProfileSummary profile={activeProfile} />}
          </div>
        </aside>
      </div>
    </AppShell>
  );
}

function QuestionBlock({
  index,
  question,
  value,
  shaking,
  invalid,
  registerRef,
  onAnimationEnd,
  onChange,
}: {
  index: number;
  question: SurveyQuestion;
  value: unknown;
  shaking: boolean;
  invalid: boolean;
  registerRef: (element: HTMLElement | null) => void;
  onAnimationEnd: () => void;
  onChange: (value: unknown) => void;
}) {
  // Values of options flagged as exclusive — used to enforce "없음" type rules.
  const exclusiveValues = useMemo(
    () =>
      new Set(
        question.options.filter((option) => option.exclusive).map((option) => option.value),
      ),
    [question.options],
  );

  return (
    <div
      ref={registerRef}
      onAnimationEnd={onAnimationEnd}
      data-invalid={invalid ? "true" : undefined}
      className={cn((shaking || invalid) && "animate-shake", invalid && "animate-missing-answer rounded-xl")}
    >
      <Card className={cn(invalid && "border-destructive/70 bg-muted/80 shadow-[0_0_0_3px_rgb(240_68_82_/_0.12)]")}>
      <CardHeader>
        <CardTitle className="text-lg font-bold leading-snug">
          {index}. {question.title}
          {question.required && (
            <span className="ml-2 align-middle text-xs font-semibold text-destructive">
              필수
            </span>
          )}
        </CardTitle>
        {question.description && (
          <p className="text-sm text-muted-foreground">{question.description}</p>
        )}
      </CardHeader>
      <CardContent>
        {question.kind === "single" && (
          <div className="grid gap-2 sm:grid-cols-2">
            {question.options.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => onChange(option.value)}
                aria-pressed={value === option.value}
                className={cn(
                  "rounded-lg border px-3 py-2 text-left text-sm transition-colors",
                  value === option.value
                    ? "border-primary bg-primary/10 text-foreground"
                    : "border-border text-muted-foreground hover:bg-muted",
                )}
              >
                {option.label}
              </button>
            ))}
          </div>
        )}

        {question.kind === "multi" && (
          <div className="grid gap-2 sm:grid-cols-2">
            {question.options.map((option) => {
              const selected = Array.isArray(value) && value.includes(option.value);
              return (
                <label
                  key={option.value}
                  className={cn(
                    "flex min-h-10 items-center gap-2 rounded-lg border px-3 py-2 text-sm transition-colors",
                    selected
                      ? "border-primary bg-primary/10 text-foreground"
                      : "border-border text-muted-foreground hover:bg-muted",
                  )}
                >
                  <input
                    type="checkbox"
                    checked={selected}
                    onChange={(event) => {
                      const current = Array.isArray(value) ? [...value] : [];
                      if (event.target.checked) {
                        if (option.exclusive) {
                          // Checking an exclusive option clears everything else.
                          onChange([option.value]);
                        } else {
                          // Checking a normal option drops any selected exclusive value.
                          const next = current.filter(
                            (item) => !exclusiveValues.has(item as string),
                          );
                          onChange([...next, option.value]);
                        }
                      } else {
                        onChange(current.filter((item) => item !== option.value));
                      }
                    }}
                  />
                  {option.label}
                </label>
              );
            })}
          </div>
        )}

        {question.kind === "acknowledgement" && (
          <label className="flex items-start gap-2 rounded-lg border-2 border-border bg-surface px-3 py-3 text-sm text-foreground">
            <input
              type="checkbox"
              checked={value === true}
              onChange={(event) => onChange(event.target.checked)}
              className="mt-0.5"
            />
            <span className="font-medium">{question.options[0]?.label}</span>
          </label>
        )}

        {question.kind === "signature" && (
          <SignatureField
            title={question.title}
            description={question.description}
            value={signatureValue(value)}
            onChange={onChange}
          />
        )}
      </CardContent>
      </Card>
    </div>
  );
}

function SignatureField({
  title,
  description,
  value,
  onChange,
}: {
  title: string;
  description?: string | null;
  value: SignatureAnswer;
  onChange: (value: SignatureAnswer) => void;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const drawingRef = useRef(false);
  const [fallbackSignedAt] = useState(() => new Date().toISOString());
  const signedAtValue = value.signed_at || fallbackSignedAt;
  const hasInk = value.signature_data_url.length > 0;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext("2d");
    if (!context) return;
    resetCanvas(context, canvas);
    if (!value.signature_data_url) return;

    const image = new Image();
    image.onload = () => {
      resetCanvas(context, canvas);
      context.drawImage(image, 0, 0, canvas.width, canvas.height);
    };
    image.src = value.signature_data_url;
  }, [value.signature_data_url]);

  function update(partial: Partial<SignatureAnswer>) {
    onChange({ ...value, signed_at: signedAtValue, ...partial });
  }

  function pointerPosition(canvas: HTMLCanvasElement, clientX: number, clientY: number) {
    const rect = canvas.getBoundingClientRect();
    return {
      x: ((clientX - rect.left) / rect.width) * canvas.width,
      y: ((clientY - rect.top) / rect.height) * canvas.height,
    };
  }

  function beginAt(canvas: HTMLCanvasElement, clientX: number, clientY: number) {
    const context = canvas.getContext("2d");
    if (!context) return;
    drawingRef.current = true;
    const point = pointerPosition(canvas, clientX, clientY);
    context.beginPath();
    context.moveTo(point.x, point.y);
  }

  function drawAt(canvas: HTMLCanvasElement, clientX: number, clientY: number) {
    if (!drawingRef.current) return;
    const context = canvas.getContext("2d");
    if (!context) return;
    const point = pointerPosition(canvas, clientX, clientY);
    context.lineTo(point.x, point.y);
    context.strokeStyle = "#191F28";
    context.lineWidth = 3;
    context.lineCap = "round";
    context.lineJoin = "round";
    context.stroke();
  }

  function finishAt(canvas: HTMLCanvasElement) {
    if (!drawingRef.current) return;
    drawingRef.current = false;
    update({ signature_data_url: canvas.toDataURL("image/png") });
  }

  function beginSignature(event: PointerEvent<HTMLCanvasElement>) {
    event.preventDefault();
    const canvas = event.currentTarget;
    canvas.setPointerCapture(event.pointerId);
    beginAt(canvas, event.clientX, event.clientY);
  }

  function drawSignature(event: PointerEvent<HTMLCanvasElement>) {
    event.preventDefault();
    drawAt(event.currentTarget, event.clientX, event.clientY);
  }

  function endSignature(event: PointerEvent<HTMLCanvasElement>) {
    event.preventDefault();
    const canvas = event.currentTarget;
    if (canvas.hasPointerCapture(event.pointerId)) {
      canvas.releasePointerCapture(event.pointerId);
    }
    finishAt(canvas);
  }

  function beginMouseSignature(event: ReactMouseEvent<HTMLCanvasElement>) {
    event.preventDefault();
    beginAt(event.currentTarget, event.clientX, event.clientY);
  }

  function drawMouseSignature(event: ReactMouseEvent<HTMLCanvasElement>) {
    event.preventDefault();
    drawAt(event.currentTarget, event.clientX, event.clientY);
  }

  function endMouseSignature(event: ReactMouseEvent<HTMLCanvasElement>) {
    event.preventDefault();
    finishAt(event.currentTarget);
  }

  function clearSignature() {
    const canvas = canvasRef.current;
    const context = canvas?.getContext("2d");
    if (!canvas || !context) return;
    resetCanvas(context, canvas);
    update({ signature_data_url: "" });
  }

  const signedAtLabel = useMemo(
    () =>
      new Intl.DateTimeFormat("ko-KR", {
        dateStyle: "long",
        timeStyle: "short",
      }).format(new Date(signedAtValue)),
    [signedAtValue],
  );
  const confirmationText = value.confirmation_text.trim();
  const confirmationMismatch =
    confirmationText.length > 0 && confirmationText !== REQUIRED_CONFIRMATION_TEXT;
  const confirmationHelpId = "legal-signature-confirmation-guide";
  const confirmationErrorId = "legal-signature-confirmation-error";

  return (
    <div className="space-y-4">
      <label className="block space-y-1">
        <span className="text-sm font-medium text-foreground">성명 입력</span>
        <input
          type="text"
          aria-label={`${title} 성명`}
          placeholder="성명을 입력하세요"
          value={value.name}
          onChange={(event) => update({ name: event.target.value })}
          className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm font-medium text-foreground placeholder:text-muted-foreground focus-visible:border-ring focus-visible:outline-none"
        />
      </label>
      <label className="block space-y-1">
        <span className="text-sm font-medium text-foreground">확인 문구 입력</span>
        <div
          className={cn(
            "relative rounded-lg border bg-surface shadow-inner transition-colors focus-within:border-ring",
            confirmationMismatch ? "border-destructive" : "border-border",
          )}
        >
          <span
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 z-0 truncate px-3 py-2 text-sm font-semibold text-muted-foreground/45"
          >
            {REQUIRED_CONFIRMATION_TEXT}
          </span>
          <input
            type="text"
            aria-label="확인 문구 입력"
            aria-invalid={confirmationMismatch}
            aria-describedby={
              confirmationMismatch ? `${confirmationHelpId} ${confirmationErrorId}` : confirmationHelpId
            }
            value={value.confirmation_text}
            onChange={(event) => update({ confirmation_text: event.target.value })}
            className="relative z-10 w-full rounded-lg bg-transparent px-3 py-2 text-sm font-semibold text-foreground caret-foreground focus-visible:outline-none"
          />
        </div>
        <p id={confirmationHelpId} className="text-xs font-medium text-muted-foreground">
          회색 안내 문구와 동일하게 입력해야 저장됩니다.
        </p>
        {confirmationMismatch && (
          <p id={confirmationErrorId} role="alert" className="text-xs font-bold text-destructive">
            확인 문구가 정확하지 않습니다. 회색 문구를 그대로 입력하세요.
          </p>
        )}
      </label>
      <div className="space-y-2">
        <div className="flex items-center justify-between gap-3">
          <span className="text-sm font-medium text-foreground">직접 서명</span>
          <Button type="button" variant="outline" size="sm" onClick={clearSignature} disabled={!hasInk}>
            지우기
          </Button>
        </div>
        <canvas
          ref={canvasRef}
          width={760}
          height={180}
          aria-label={`${title} 서명 패드`}
          className="h-44 w-full touch-none rounded-lg border-2 border-dashed border-border bg-surface shadow-inner"
          onPointerDown={beginSignature}
          onPointerMove={drawSignature}
          onPointerUp={endSignature}
          onPointerCancel={endSignature}
          onPointerLeave={endSignature}
          onMouseDown={beginMouseSignature}
          onMouseMove={drawMouseSignature}
          onMouseUp={endMouseSignature}
          onMouseLeave={endMouseSignature}
        />
      </div>
      {description && <p className="text-sm leading-6 text-muted-foreground">{description}</p>}
      <p className="text-xs text-muted-foreground">
        서명 일시(저장 시 자동 기록): {signedAtLabel}
      </p>
    </div>
  );
}

function ProfileSummary({ profile }: { profile: InvestorProfileResponse }) {
  return (
    <Card size="sm">
      <CardHeader>
        <CardTitle>현재 프로필</CardTitle>
        <CardDescription>
          {profile.completed ? `${profile.risk_type} · ${profile.knowledge_level}` : "설문 전"}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <div className="grid grid-cols-2 gap-2">
          <Metric label="투자율 상한" value={`${profile.recommended_max_equity_pct}%`} />
          <Metric label="자동화" value={profile.recommended_autonomy_level} />
        </div>
        {profile.satisfaction_focus.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {profile.satisfaction_focus.map((item) => (
              <Badge key={item} variant="secondary">
                {item}
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border p-2">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="font-mono text-sm text-foreground">{value}</div>
    </div>
  );
}

function hasAnswer(question: SurveyQuestion, answers: Answers) {
  const value = answers[question.id];
  if (question.kind === "multi") return Array.isArray(value) && value.length > 0;
  if (question.kind === "acknowledgement") return value === true;
  if (question.kind === "signature") {
    const signature = signatureValue(value);
    return (
      signature.name.trim().length > 0 &&
      signature.confirmation_text.trim() === REQUIRED_CONFIRMATION_TEXT &&
      signature.signature_data_url.startsWith("data:image/png;base64,")
    );
  }
  return typeof value === "string" && value.length > 0;
}

function questionIssue(question: SurveyQuestion, answers: Answers): string | null {
  if (question.kind !== "signature") return null;
  const signature = signatureValue(answers[question.id]);
  if (signature.name.trim().length === 0) {
    return `${question.title}: 성명을 입력하세요.`;
  }
  if (signature.confirmation_text.trim().length === 0) {
    return `${question.title}: 회색 안내 문구를 그대로 입력하세요.`;
  }
  if (signature.confirmation_text.trim() !== REQUIRED_CONFIRMATION_TEXT) {
    return `${question.title}: 확인 문구가 정확하지 않습니다. 회색 안내 문구와 동일하게 입력하세요.`;
  }
  if (!signature.signature_data_url.startsWith("data:image/png;base64,")) {
    return `${question.title}: 서명 패드에 직접 서명하세요.`;
  }
  return null;
}

function signatureValue(value: unknown): SignatureAnswer {
  if (isSignatureAnswer(value)) return value;
  return {
    name: "",
    confirmation_text: "",
    signature_data_url: "",
    signed_at: new Date().toISOString(),
  };
}

function isSignatureAnswer(value: unknown): value is SignatureAnswer {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<SignatureAnswer>;
  return (
    typeof candidate.name === "string" &&
    typeof candidate.confirmation_text === "string" &&
    typeof candidate.signature_data_url === "string" &&
    typeof candidate.signed_at === "string"
  );
}

function resetCanvas(context: CanvasRenderingContext2D, canvas: HTMLCanvasElement) {
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "#FFFFFF";
  context.fillRect(0, 0, canvas.width, canvas.height);
}
