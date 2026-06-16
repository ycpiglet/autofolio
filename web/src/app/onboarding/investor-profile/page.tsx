"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
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
  type SurveyQuestion,
} from "@/lib/api";
import { cn } from "@/lib/utils";

type Answers = Record<string, unknown>;
type SubmitStatus =
  | { kind: "idle" }
  | { kind: "saving" }
  | { kind: "saved"; profile: InvestorProfileResponse }
  | { kind: "error"; message: string };

export default function InvestorProfileOnboardingPage() {
  const queryClient = useQueryClient();
  const [answers, setAnswers] = useState<Answers>({});
  const [status, setStatus] = useState<SubmitStatus>({ kind: "idle" });

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
  const completion = useMemo(() => {
    if (questions.length === 0) return 0;
    const answered = questions.filter((question) => hasAnswer(question, answers)).length;
    return Math.round((answered / questions.length) * 100);
  }, [answers, questions]);

  async function handleSubmit() {
    const missing = questions.filter((question) => !hasAnswer(question, answers));
    if (missing.length > 0) {
      setStatus({ kind: "error", message: `${missing[0].title} 항목을 완료하세요.` });
      return;
    }
    setStatus({ kind: "saving" });
    try {
      const result = await postInvestorSurvey(answers);
      setStatus({ kind: "saved", profile: result.profile });
      await queryClient.invalidateQueries({ queryKey: ["investor-profile"] });
    } catch (err) {
      let message = "투자 프로필을 저장하지 못했습니다.";
      if (err instanceof ApiError) {
        const detail = err.body as { detail?: string } | undefined;
        message = detail?.detail ?? err.message;
      }
      setStatus({ kind: "error", message });
    }
  }

  const activeProfile =
    status.kind === "saved" ? status.profile : profileQuery.data;

  return (
    <AppShell className="p-0">
      <div className="border-b border-border bg-surface px-6 py-5">
        <div className="mx-auto flex max-w-5xl flex-col gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-lg font-semibold text-foreground">투자 프로필</h1>
            <Badge variant={activeProfile?.completed ? "default" : "secondary"}>
              {activeProfile?.completed ? activeProfile.risk_type : "미완료"}
            </Badge>
            {activeProfile?.needs_advanced_survey && (
              <Badge variant="outline">심화 설문 권장</Badge>
            )}
          </div>
          <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
            성향, 지식수준, 만족 기준, 자동화 선호를 기록해 제안과 경고를 개인화합니다.
          </p>
        </div>
      </div>

      <div className="mx-auto grid max-w-5xl gap-6 px-6 py-6 lg:grid-cols-[1fr_280px]">
        <div className="space-y-4">
          {surveyQuery.isPending && (
            <div className="h-48 animate-pulse rounded-lg bg-muted" />
          )}
          {surveyQuery.error && (
            <p role="alert" className="rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
              설문을 불러오지 못했습니다.
            </p>
          )}
          {questions.map((question, index) => (
            <QuestionBlock
              key={question.id}
              index={index + 1}
              question={question}
              value={answers[question.id]}
              onChange={(value) => {
                setStatus({ kind: "idle" });
                setAnswers((prev) => ({ ...prev, [question.id]: value }));
              }}
            />
          ))}

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Button
              onClick={() => void handleSubmit()}
              disabled={status.kind === "saving" || surveyQuery.isPending}
            >
              {status.kind === "saving" ? "저장 중…" : "프로필 저장"}
            </Button>
            <Button variant="outline" render={<Link href="/home" />}>
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
        </aside>
      </div>
    </AppShell>
  );
}

function QuestionBlock({
  index,
  question,
  value,
  onChange,
}: {
  index: number;
  question: SurveyQuestion;
  value: unknown;
  onChange: (value: unknown) => void;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">
          {index}. {question.title}
        </CardTitle>
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
                        onChange([...current, option.value]);
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
          <label className="flex items-start gap-2 rounded-lg border border-border px-3 py-3 text-sm text-muted-foreground">
            <input
              type="checkbox"
              checked={value === true}
              onChange={(event) => onChange(event.target.checked)}
              className="mt-0.5"
            />
            <span>{question.options[0]?.label}</span>
          </label>
        )}
      </CardContent>
    </Card>
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
  return typeof value === "string" && value.length > 0;
}
