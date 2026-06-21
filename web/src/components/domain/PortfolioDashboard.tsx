"use client";

import { useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import dynamic from "next/dynamic";
import {
  Activity,
  AlertTriangle,
  ArrowDownWideNarrow,
  BarChart3,
  ChevronDown,
  ChevronUp,
  HelpCircle,
  Layers,
  PieChart,
  Plus,
  RefreshCcw,
  Save,
  Table2,
  Target,
  Trash2,
  Wallet,
} from "lucide-react";
import {
  deletePortfolioGroup,
  apiTable,
  getPortfolioOverview,
  postPortfolioGroup,
  putPortfolioGroup,
  type PortfolioGroup,
  type PortfolioHoldingRow,
  type PortfolioOverviewResponse,
} from "@/lib/api";
import { fmtPct, fmtWon } from "@/lib/format";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { HoldingsTable } from "@/components/domain/HoldingsTable";

const EquityChart = dynamic(
  () => import("@/components/domain/EquityChart").then((m) => m.EquityChart),
  { ssr: false, loading: () => <div className="h-60 animate-pulse rounded-lg bg-muted" /> },
);

const AllocationChart = dynamic(
  () => import("@/components/domain/AllocationChart").then((m) => m.AllocationChart),
  { ssr: false, loading: () => <div className="h-60 animate-pulse rounded-lg bg-muted" /> },
);

type TabId = "overview" | "diagnosis" | "holdings" | "groups" | "performance";
type KpiId = "total" | "unrealized" | "daily" | "holdings" | "monthly";
type ValueMode = "pct" | "won" | "raw";
type Tone = "neutral" | "pnl";
type MoverSortKey = "pnl" | "return" | "weight" | "name";
type SortDirection = "asc" | "desc";

interface KpiDetailItem {
  label: string;
  value: string;
  tone?: Tone;
}

interface PortfolioKpiCardModel {
  id: KpiId;
  label: string;
  value: unknown;
  valueMode: ValueMode;
  valueSigned?: boolean;
  delta?: unknown;
  deltaMode?: ValueMode;
  deltaSigned?: boolean;
  deltaTone?: Tone;
  help: string;
  detail: string;
  tone?: Tone;
  items: KpiDetailItem[];
}

const TABS: Array<{ id: TabId; label: string; icon: typeof AlertTriangle }> = [
  { id: "overview", label: "요약", icon: PieChart },
  { id: "diagnosis", label: "진단", icon: AlertTriangle },
  { id: "holdings", label: "보유", icon: Table2 },
  { id: "groups", label: "그룹", icon: Layers },
  { id: "performance", label: "성과", icon: BarChart3 },
];

const KPI_TAB_TARGET: Record<KpiId, TabId> = {
  total: "overview",
  unrealized: "performance",
  daily: "performance",
  holdings: "holdings",
  monthly: "performance",
};

const NUMBER_TEXT_CLASS = "font-semibold tabular-nums";
const STRONG_NUMBER_TEXT_CLASS = "font-bold tabular-nums";
const EMPHASIS_PATTERN =
  /([+-]?₩?\d+(?:,\d{3})*(?:\.\d+)?%?|보유 목적|손실 허용 범위|손실 허용|투자 목적|단일 종목 집중|상위 1종목|상위 3종목|상위 5종목|데이터 품질|집중도|SK하이닉스|삼성전자|ETF|현금|채권|주식|자산군|섹터|전략|위험|비중|총자산|평가금액|평가손익|일간손익|월간수익률|누적손익률|보유종목|목표 배분)/g;
const EMPHASIS_EXACT_PATTERN =
  /^([+-]?₩?\d+(?:,\d{3})*(?:\.\d+)?%?|보유 목적|손실 허용 범위|손실 허용|투자 목적|단일 종목 집중|상위 1종목|상위 3종목|상위 5종목|데이터 품질|집중도|SK하이닉스|삼성전자|ETF|현금|채권|주식|자산군|섹터|전략|위험|비중|총자산|평가금액|평가손익|일간손익|월간수익률|누적손익률|보유종목|목표 배분)$/;

export function PortfolioDashboard() {
  const [activeTab, setActiveTab] = useState<TabId>("overview");
  const [activeKpi, setActiveKpi] = useState<KpiId>("total");
  const overviewQuery = useQuery<PortfolioOverviewResponse>({
    queryKey: ["portfolio-overview"],
    queryFn: getPortfolioOverview,
    staleTime: 30_000,
  });

  const overview = overviewQuery.data;
  const kpiCards = useMemo(() => buildKpiCards(overview?.kpis), [overview?.kpis]);

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-normal text-foreground">포트폴리오</h1>
          <p className="mt-1 text-sm font-medium text-muted-foreground">
            {overview?.kpis?.as_of ? `마지막 갱신 ${String(overview.kpis.as_of).slice(0, 19)}` : "계좌 자산 진단"}
          </p>
        </div>
        <Button
          type="button"
          variant="outline"
          onClick={() => overviewQuery.refetch()}
          disabled={overviewQuery.isFetching}
        >
          <RefreshCcw aria-hidden />
          새로고침
        </Button>
      </header>

      {overviewQuery.error && (
        <div role="alert" className="rounded-lg border border-destructive/40 bg-destructive/10 p-4 text-sm font-semibold text-destructive">
          포트폴리오를 불러오지 못했습니다: {(overviewQuery.error as Error).message}
        </div>
      )}

      <KpiGrid
        cards={kpiCards}
        activeKpi={activeKpi}
        isLoading={overviewQuery.isPending}
        onSelect={(id) => {
          setActiveKpi(id);
          setActiveTab(KPI_TAB_TARGET[id]);
        }}
      />

      <nav className="flex min-h-10 flex-wrap gap-2" aria-label="포트폴리오 보기">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const active = activeTab === tab.id;
          return (
            <Button
              key={tab.id}
              type="button"
              variant={active ? "default" : "outline"}
              size="sm"
              onClick={() => setActiveTab(tab.id)}
              aria-pressed={active}
            >
              <Icon aria-hidden />
              {tab.label}
            </Button>
          );
        })}
      </nav>

      {activeTab === "overview" && <OverviewPanel overview={overview} activeKpi={activeKpi} cards={kpiCards} />}
      {activeTab === "diagnosis" && <DiagnosisPanel overview={overview} />}
      {activeTab === "holdings" && <HoldingsPanel overview={overview} isLoading={overviewQuery.isPending} />}
      {activeTab === "groups" && <GroupsPanel overview={overview} />}
      {activeTab === "performance" && <PerformancePanel overview={overview} />}
    </div>
  );
}

function KpiGrid({
  cards,
  activeKpi,
  isLoading,
  onSelect,
}: {
  cards: PortfolioKpiCardModel[];
  activeKpi: KpiId;
  isLoading: boolean;
  onSelect: (id: KpiId) => void;
}) {
  return (
    <section aria-label="포트폴리오 핵심 지표" className="grid grid-cols-2 gap-3 lg:grid-cols-5">
      {cards.map((card) => (
        <PortfolioKpiButton
          key={card.id}
          card={card}
          active={activeKpi === card.id}
          isLoading={isLoading}
          onClick={() => onSelect(card.id)}
        />
      ))}
    </section>
  );
}

function PortfolioKpiButton({
  card,
  active,
  isLoading,
  onClick,
}: {
  card: PortfolioKpiCardModel;
  active: boolean;
  isLoading: boolean;
  onClick: () => void;
}) {
  const valueNumber = toNumber(card.value);
  const valueClass = card.tone === "pnl" ? portfolioPnlColorClass(valueNumber) : "text-foreground";
  const deltaNumber = toNumber(card.delta);
  const deltaClass = card.deltaTone === "pnl" ? portfolioPnlColorClass(deltaNumber) : "text-muted-foreground";

  return (
    <button
      type="button"
      data-kpi-id={card.id}
      className={cn(
        "rounded-lg border border-border bg-card p-4 text-left shadow-soft transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        "hover:border-primary/60 hover:bg-accent/40",
        active && "border-primary bg-accent/50 ring-2 ring-primary/15",
      )}
      aria-pressed={active}
      onClick={onClick}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="inline-flex items-center gap-1.5 text-sm font-bold text-foreground">
          {card.label}
          <InfoHint label={card.help} />
        </span>
        <Badge variant={active ? "default" : "outline"}>상세</Badge>
      </div>
      <div
        className={cn("mt-3 text-2xl", STRONG_NUMBER_TEXT_CLASS, valueClass)}
        aria-label={`${card.label}: ${isLoading ? "로딩 중" : formatKpiValue(card.value, card.valueMode, card.valueSigned)}`}
      >
        {isLoading ? "..." : formatKpiValue(card.value, card.valueMode, card.valueSigned)}
      </div>
      {card.delta !== undefined && (
        <div className={cn("mt-1 text-sm", NUMBER_TEXT_CLASS, deltaClass)}>
          {formatKpiValue(card.delta, card.deltaMode ?? "pct", card.deltaSigned)}
        </div>
      )}
    </button>
  );
}

function KpiDetailPanel({ cards, activeKpi }: { cards: PortfolioKpiCardModel[]; activeKpi: KpiId }) {
  const card = cards.find((item) => item.id === activeKpi);
  if (!card) return null;

  return (
    <section className="rounded-lg border border-primary/20 bg-accent/40 p-4" aria-label={`${card.label} 상세`}>
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <h2 className="text-base font-bold text-foreground">{card.label}</h2>
          <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
            <EmphasizedText text={card.detail} />
          </p>
        </div>
        <div className="grid min-w-0 gap-2 sm:grid-cols-3 lg:min-w-[520px]">
          {card.items.map((item) => (
            <div key={item.label} className="rounded-lg border border-border bg-card px-3 py-2">
              <div className="text-xs font-semibold text-muted-foreground">{item.label}</div>
              <div className={cn("mt-1 text-sm", STRONG_NUMBER_TEXT_CLASS, item.tone === "pnl" && portfolioPnlColorClass(parseDisplayNumber(item.value)))}>
                {item.value}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function OverviewPanel({
  overview,
  activeKpi,
  cards,
}: {
  overview?: PortfolioOverviewResponse;
  activeKpi: KpiId;
  cards: PortfolioKpiCardModel[];
}) {
  const allRows = overview?.holdings?.rows ?? [];
  const assetGroup = findAutomaticGroup(overview, "asset-class");
  const exposureGroup =
    findAutomaticGroup(overview, "sector") ??
    findAutomaticGroup(overview, "region") ??
    findAutomaticGroup(overview, "strategy");

  return (
    <section className="space-y-5" aria-label="포트폴리오 시각 요약">
      <KpiDetailPanel cards={cards} activeKpi={activeKpi} />

      <div className="grid gap-5 xl:grid-cols-[1.35fr_1fr]">
        <AssetTrendCard />
        <AllocationSummaryCard overview={overview} />
      </div>

      <div className="grid gap-5 xl:grid-cols-3">
        <ExposureCard
          title="자산군 노출"
          help="현금, 주식, ETF, 채권처럼 큰 자산군이 현재 평가금액에서 차지하는 비중입니다."
          group={assetGroup}
          icon="wallet"
        />
        <ExposureCard
          title={exposureGroup?.title ?? "섹터/지역 노출"}
          help="포트폴리오가 특정 산업, 지역, 전략에 몰려 있는지 확인하는 노출 분석입니다."
          group={exposureGroup}
          icon="activity"
        />
        <ConcentrationVisualCard overview={overview} />
      </div>

      <div className="grid gap-5 xl:grid-cols-2">
        <TopMovers
          title="성과 기여"
          help="평가손익 기준으로 현재 포트폴리오 수익을 가장 많이 만든 종목입니다."
          rows={overview?.top_movers?.contributors ?? []}
          allRows={allRows}
          defaultDirection="desc"
        />
        <TopMovers
          title="손실 기여"
          help="평가손익 기준으로 현재 포트폴리오 손실을 가장 많이 만든 종목입니다."
          rows={overview?.top_movers?.detractors ?? []}
          allRows={allRows}
          defaultDirection="asc"
        />
      </div>
    </section>
  );
}

function AssetTrendCard() {
  const curveQuery = useQuery({
    queryKey: ["asset-curve"],
    queryFn: () => apiTable("/api/portfolio/asset-curve?days=180"),
    staleTime: 60_000,
  });
  const stats = useMemo(() => buildCurveStats(curveQuery.data), [curveQuery.data]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base font-bold">
          <BarChart3 className="size-4 text-brand" aria-hidden />
          <span>자산 추이</span>
          <InfoHint label="기간 시작점 대비 현재 총자산이 얼마나 변했는지, 고점과 저점이 어디였는지 함께 보여줍니다." />
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4 p-4 pt-0">
        <div className="grid gap-2 sm:grid-cols-3">
          <TrendStat label="현재" value={stats ? fmtWon(stats.current) : "-"} />
          <TrendStat
            label="기간 변화"
            value={stats ? formatSignedWon(stats.change) : "-"}
            className={stats ? portfolioPnlColorClass(stats.change) : undefined}
          />
          <TrendStat label="변화율" value={stats ? fmtPct(stats.changePct) : "-"} className={stats ? portfolioPnlColorClass(stats.changePct) : undefined} />
        </div>
        <EquityChart data={curveQuery.data} isLoading={curveQuery.isPending} error={curveQuery.error as Error | null} />
        {stats && (
          <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs font-medium text-muted-foreground">
            <span>
              고점 <strong className={cn(STRONG_NUMBER_TEXT_CLASS, "text-foreground")}>{fmtWon(stats.high)}</strong>
            </span>
            <span>
              저점 <strong className={cn(STRONG_NUMBER_TEXT_CLASS, "text-foreground")}>{fmtWon(stats.low)}</strong>
            </span>
            <span>{stats.points.toLocaleString("ko-KR")}개 관측값</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function TrendStat({ label, value, className }: { label: string; value: string; className?: string }) {
  return (
    <div className="rounded-md bg-muted/45 px-3 py-2">
      <div className="text-xs font-semibold text-muted-foreground">{label}</div>
      <div className={cn("mt-1 text-base", STRONG_NUMBER_TEXT_CLASS, className ?? "text-foreground")}>{value}</div>
    </div>
  );
}

function AllocationSummaryCard({ overview }: { overview?: PortfolioOverviewResponse }) {
  const rows = overview?.allocation_gap?.rows ?? [];
  const columns = overview?.allocation_gap?.columns ?? [];
  const nameCol = columns[0] ?? "자산군";
  const currentCol = columns.find((col) => col.includes("현재")) ?? columns.find((col) => col.includes("비중")) ?? columns[1];
  const targetCol = columns.find((col) => col.includes("목표"));
  const gapCol = columns.find((col) => col.includes("갭"));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base font-bold">
          <PieChart className="size-4 text-brand" aria-hidden />
          <span>목표 배분</span>
          <InfoHint label="현재 자산군 비중을 목표 비중과 비교해 리밸런싱 후보를 찾는 도넛/갭 분석입니다." />
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4 p-4 pt-0">
        <AllocationChart data={overview?.allocation_gap} />
        <div className="space-y-2">
          {rows.slice(0, 5).map((row, index) => {
            const name = String(row[nameCol] ?? "미분류");
            const current = toNumber(currentCol ? row[currentCol] : 0);
            const target = targetCol ? toNumber(row[targetCol]) : 0;
            const gap = gapCol ? toNumber(row[gapCol]) : current - target;
            return (
              <div key={`${name}-${index}`} className="space-y-1.5">
                <div className="flex items-center justify-between gap-3 text-sm">
                  <strong className="text-foreground">{name}</strong>
                  <span className={cn(NUMBER_TEXT_CLASS, portfolioPnlColorClass(gap))}>
                    {targetCol ? `${fmtNumber(current, "%")} / 목표 ${fmtNumber(target, "%")}` : fmtNumber(current, "%")}
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <div className="h-full rounded-full bg-brand" style={{ width: `${clampPct(current)}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

function ExposureCard({
  title,
  help,
  group,
  icon,
}: {
  title: string;
  help: string;
  group?: { rows: Record<string, unknown>[] };
  icon: "wallet" | "activity";
}) {
  const rows = group?.rows ?? [];
  const Icon = icon === "wallet" ? Wallet : Activity;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base font-bold">
          <Icon className="size-4 text-brand" aria-hidden />
          <span>{title}</span>
          <InfoHint label={help} />
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 p-4 pt-0">
        {rows.length === 0 ? (
          <p className="text-sm font-medium text-muted-foreground">분석할 그룹 데이터가 없습니다.</p>
        ) : (
          rows.slice(0, 6).map((row) => {
            const name = String(row.name ?? "미분류");
            const weight = toNumber(row.weight_pct);
            const pnl = toNumber(row.pnl);
            return (
              <div key={name} className="space-y-1.5">
                <div className="flex items-center justify-between gap-3 text-sm">
                  <strong className="truncate text-foreground">{name}</strong>
                  <span className={cn(STRONG_NUMBER_TEXT_CLASS, portfolioPnlColorClass(pnl))}>
                    {fmtNumber(weight, "%")}
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <div className="h-full rounded-full bg-brand/80" style={{ width: `${clampPct(weight)}%` }} />
                </div>
              </div>
            );
          })
        )}
      </CardContent>
    </Card>
  );
}

function ConcentrationVisualCard({ overview }: { overview?: PortfolioOverviewResponse }) {
  const concentration = overview?.concentration ?? {};
  const holdings = [...(overview?.holdings?.rows ?? [])]
    .sort((a, b) => holdingNumber(b, "비중") - holdingNumber(a, "비중"))
    .slice(0, 5);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base font-bold">
          <Target className="size-4 text-brand" aria-hidden />
          <span>집중도</span>
          <InfoHint label="상위 종목이 전체 평가금액에서 차지하는 비중입니다. 특정 종목 쏠림을 빠르게 확인합니다." />
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 p-4 pt-0">
        <div className="grid grid-cols-2 gap-2">
          <TrendStat label="상위 1종목" value={fmtNumber(concentration.top1_weight_pct, "%")} />
          <TrendStat label="상위 3종목" value={fmtNumber(concentration.top3_weight_pct, "%")} />
        </div>
        <div className="space-y-2">
          {holdings.length === 0 ? (
            <p className="text-sm font-medium text-muted-foreground">보유 종목 없음</p>
          ) : (
            holdings.map((row) => {
              const name = holdingText(row, "종목") || holdingText(row, "티커") || "미분류";
              const weight = holdingNumber(row, "비중");
              return (
                <div key={`${name}-${holdingText(row, "티커")}`} className="space-y-1">
                  <div className="flex items-center justify-between gap-3 text-sm">
                    <strong className="truncate text-foreground">{name}</strong>
                    <span className={cn(NUMBER_TEXT_CLASS, "text-foreground")}>{fmtNumber(weight, "%")}</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-muted">
                    <div className="h-full rounded-full bg-destructive/75" style={{ width: `${clampPct(weight)}%` }} />
                  </div>
                </div>
              );
            })
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function DiagnosisPanel({ overview }: { overview?: PortfolioOverviewResponse }) {
  const diagnostics = overview?.diagnostics ?? [];
  const concentration = overview?.concentration ?? {};
  const dataQuality = overview?.data_quality ?? {};

  return (
    <section className="grid gap-4 lg:grid-cols-[1.4fr_1fr]" aria-label="포트폴리오 진단">
      <div className="space-y-3">
        <SectionHeading
          title="진단"
          help="보유 구조에서 바로 확인해야 할 집중도, 데이터 누락, 손익 위험 신호를 요약합니다."
        />
        {diagnostics.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border p-5 text-sm font-medium text-muted-foreground">
            확인할 진단 항목이 없습니다.
          </div>
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            {diagnostics.map((item, index) => (
              <DiagnosticCard key={index} item={item} />
            ))}
          </div>
        )}
      </div>

      <div className="space-y-4">
        <div className="space-y-3">
          <SectionHeading
            title="집중도"
            help="상위 종목이 전체 평가금액에서 차지하는 비중입니다. 특정 종목 쏠림을 빠르게 봅니다."
          />
          <Card>
            <CardContent className="grid gap-3 p-4">
              <MetricRow label="상위 1종목" value={fmtNumber(concentration.top1_weight_pct, "%")} />
              <MetricRow label="상위 3종목" value={fmtNumber(concentration.top3_weight_pct, "%")} />
              <MetricRow label="상위 5종목" value={fmtNumber(concentration.top5_weight_pct, "%")} />
              <MetricRow label="보유 종목" value={`${Number(concentration.held_symbols ?? 0).toLocaleString("ko-KR")}개`} />
            </CardContent>
          </Card>
        </div>

        <div className="space-y-3">
          <SectionHeading
            title="데이터 품질"
            help="종목명, 섹터, 전략 메타데이터가 부족한 항목을 보여줍니다. 분석 신뢰도를 판단하는 기준입니다."
          />
          <Card>
            <CardContent className="space-y-2 p-4 text-sm">
              <MetricRow label="경고" value={`${Number(dataQuality.warnings ?? 0).toLocaleString("ko-KR")}건`} />
              <MetricRow label="종목명 보강 필요" value={`${asArray(dataQuality.fallback_ticker_name_symbols).length}개`} />
              <MetricRow label="섹터 미분류" value={`${asArray(dataQuality.missing_sector_symbols).length}개`} />
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
}

function DiagnosticCard({ item }: { item: Record<string, unknown> }) {
  const level = String(item.level ?? "info");
  return (
    <Card className={cn(level === "watch" && "border-amber-300/70")}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between gap-2 text-base font-bold">
          <span>{String(item.title ?? "진단")}</span>
          <Badge variant={level === "watch" ? "outline" : "secondary"}>{level}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <p className="leading-relaxed text-foreground">
          <EmphasizedText text={String(item.message ?? "")} />
        </p>
        <p className="font-medium leading-relaxed text-muted-foreground">
          <EmphasizedText text={String(item.action ?? "")} />
        </p>
        <div className="flex flex-wrap gap-1">
          {asArray(item.symbols).map((symbol) => (
            <Badge key={String(symbol)} variant="secondary" className="font-bold tabular-nums">
              {String(symbol)}
            </Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function HoldingsPanel({
  overview,
  isLoading,
}: {
  overview?: PortfolioOverviewResponse;
  isLoading: boolean;
}) {
  const table = overview?.holdings;
  return (
    <section className="space-y-3" aria-label="보유 종목">
      <SectionHeading
        title="보유 종목"
        help="현재 보유 중인 종목별 수량, 평가금액, 평가손익, 비중입니다. 숫자 컬럼은 같은 고정폭 글꼴로 표시합니다."
      />
      <HoldingsTable
        data={table}
        isLoading={isLoading}
        pnlClassName={portfolioPnlColorClass}
        emphasizeValues
      />
    </section>
  );
}

function GroupsPanel({ overview }: { overview?: PortfolioOverviewResponse }) {
  const groups = overview?.groups;
  return (
    <section className="space-y-5" aria-label="포트폴리오 그룹">
      <ManualGroupEditor saved={groups?.saved ?? []} holdings={overview?.holdings?.rows ?? []} />
      <div className="grid gap-4 xl:grid-cols-2">
        {(groups?.automatic ?? []).map((group) => (
          <GroupSummary key={group.id} title={group.title} rows={group.rows} />
        ))}
      </div>
    </section>
  );
}

function ManualGroupEditor({
  saved,
  holdings,
}: {
  saved: PortfolioGroup[];
  holdings: PortfolioHoldingRow[];
}) {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [symbolsText, setSymbolsText] = useState("");
  const symbols = useMemo(
    () => symbolsText.split(/[,\s]+/).map((s) => s.trim().toUpperCase()).filter(Boolean),
    [symbolsText],
  );
  const createMutation = useMutation({
    mutationFn: () => postPortfolioGroup({ name, symbols }),
    onSuccess: () => {
      setName("");
      setSymbolsText("");
      queryClient.invalidateQueries({ queryKey: ["portfolio-overview"] });
    },
  });
  const deleteMutation = useMutation({
    mutationFn: (groupId: string) => deletePortfolioGroup(groupId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["portfolio-overview"] }),
  });
  const quickSaveMutation = useMutation({
    mutationFn: (group: PortfolioGroup) =>
      putPortfolioGroup(group.group_id, {
        name: group.name,
        description: group.description,
        color: group.color,
        sort_order: group.sort_order,
        symbols: group.symbols,
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["portfolio-overview"] }),
  });

  return (
    <div className="space-y-3">
      <SectionHeading
        title="수동 그룹"
        help="사용자가 직접 묶어 보고 싶은 종목 그룹입니다. 예: 장기보유, 단기실험, 배당, 리스크 관찰."
      />
      <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
        <Card>
          <CardContent className="space-y-3 p-4">
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="그룹명" />
            <Input value={symbolsText} onChange={(e) => setSymbolsText(e.target.value)} placeholder="005930, 069500" />
            <Button
              type="button"
              onClick={() => createMutation.mutate()}
              disabled={!name.trim() || symbols.length === 0 || createMutation.isPending}
            >
              <Plus aria-hidden />
              생성
            </Button>
            {createMutation.error && (
              <p className="text-sm font-semibold text-destructive">{(createMutation.error as Error).message}</p>
            )}
          </CardContent>
        </Card>

        <div className="grid gap-3 md:grid-cols-2">
          {saved.length === 0 ? (
            <div className="rounded-lg border border-dashed border-border p-5 text-sm font-medium text-muted-foreground">
              저장된 수동 그룹 없음
            </div>
          ) : (
            saved.map((group) => (
              <Card key={group.group_id}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between gap-2 text-base font-bold">
                    <span>{group.name}</span>
                    <Badge variant="secondary">{group.symbols.length}종목</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 p-4 pt-0">
                  <div className="flex flex-wrap gap-1">
                    {group.symbols.map((symbol) => (
                      <Badge key={symbol} variant="outline" className="font-semibold">
                        {symbolName(symbol, holdings)}
                      </Badge>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <Button type="button" size="sm" variant="outline" onClick={() => quickSaveMutation.mutate(group)}>
                      <Save aria-hidden />
                      저장
                    </Button>
                    <Button type="button" size="sm" variant="destructive" onClick={() => deleteMutation.mutate(group.group_id)}>
                      <Trash2 aria-hidden />
                      삭제
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function GroupSummary({ title, rows }: { title: string; rows: Record<string, unknown>[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-bold">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 p-4 pt-0">
        {rows.length === 0 ? (
          <p className="text-sm font-medium text-muted-foreground">데이터 없음</p>
        ) : (
          rows.map((row) => (
            <div key={String(row.name)} className="grid grid-cols-[minmax(0,1fr)_90px_100px] items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-muted/40">
              <span className="truncate font-bold text-foreground">{String(row.name)}</span>
              <span className={cn("text-right", NUMBER_TEXT_CLASS)}>{fmtNumber(row.weight_pct, "%")}</span>
              <span className={cn("text-right", STRONG_NUMBER_TEXT_CLASS, portfolioPnlColorClass(Number(row.pnl ?? 0)))}>
                {formatSignedWon(Number(row.pnl ?? 0))}
              </span>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}

function PerformancePanel({ overview }: { overview?: PortfolioOverviewResponse }) {
  const allRows = overview?.holdings?.rows ?? [];

  return (
    <section className="grid gap-5 xl:grid-cols-[1.3fr_1fr]" aria-label="성과">
      <AssetTrendCard />
      <AllocationSummaryCard overview={overview} />
      <TopMovers
        title="기여 상위"
        help="평가손익 기준으로 포트폴리오 수익에 가장 크게 기여한 종목입니다."
        rows={overview?.top_movers?.contributors ?? []}
        allRows={allRows}
        defaultDirection="desc"
      />
      <TopMovers
        title="손실 기여"
        help="평가손익 기준으로 포트폴리오 손실에 가장 크게 영향을 준 종목입니다."
        rows={overview?.top_movers?.detractors ?? []}
        allRows={allRows}
        defaultDirection="asc"
      />
    </section>
  );
}

function TopMovers({
  title,
  help,
  rows,
  allRows,
  defaultDirection,
}: {
  title: string;
  help: string;
  rows: PortfolioHoldingRow[];
  allRows: PortfolioHoldingRow[];
  defaultDirection: SortDirection;
}) {
  const [sortKey, setSortKey] = useState<MoverSortKey>("pnl");
  const [direction, setDirection] = useState<SortDirection>(defaultDirection);
  const [expanded, setExpanded] = useState(false);
  const baseRows = expanded ? allRows : rows.length > 0 ? rows : allRows;
  const sortedRows = useMemo(
    () => sortMoverRows(baseRows, sortKey, direction),
    [baseRows, sortKey, direction],
  );
  const visibleRows = expanded ? sortedRows.slice(0, 20) : sortedRows.slice(0, 5);
  const canExpand = allRows.length > rows.length || sortedRows.length > visibleRows.length;

  function changeSort(nextKey: MoverSortKey) {
    if (sortKey === nextKey) {
      setDirection((current) => (current === "desc" ? "asc" : "desc"));
      return;
    }
    setSortKey(nextKey);
    setDirection(nextKey === "name" ? "asc" : defaultDirection);
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <SectionHeading title={title} help={help} />
        <div className="flex flex-wrap gap-1.5">
          {[
            ["pnl", "손익"],
            ["return", "수익률"],
            ["weight", "비중"],
            ["name", "종목"],
          ].map(([key, label]) => (
            <Button
              key={key}
              type="button"
              size="sm"
              variant={sortKey === key ? "default" : "outline"}
              onClick={() => changeSort(key as MoverSortKey)}
            >
              <ArrowDownWideNarrow aria-hidden />
              {label}
            </Button>
          ))}
        </div>
      </div>

      <div className="rounded-lg border border-border bg-card">
        {visibleRows.length === 0 ? (
          <p className="p-4 text-sm font-medium text-muted-foreground">데이터 없음</p>
        ) : (
          visibleRows.map((row, index) => {
            const pnl = holdingNumber(row, "평가손익");
            const returnPct = holdingNumber(row, "손익률");
            const weightPct = holdingNumber(row, "비중");
            const name = holdingText(row, "종목") || "미분류";
            const ticker = holdingText(row, "티커");
            return (
              <div
                key={`${ticker || name}-${index}`}
                className="grid grid-cols-[minmax(0,1fr)_auto] gap-3 border-b border-border p-3 text-sm last:border-0 hover:bg-muted/40"
              >
                <div className="min-w-0">
                  <div className="flex min-w-0 flex-wrap items-center gap-2">
                    <strong className="truncate text-base font-bold text-foreground">{name}</strong>
                    {ticker && (
                      <Badge variant="outline" className="font-bold tabular-nums">
                        {ticker}
                      </Badge>
                    )}
                  </div>
                  <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-xs font-medium text-muted-foreground">
                    <span>
                      비중 <strong className={cn(STRONG_NUMBER_TEXT_CLASS, "text-foreground")}>{fmtNumber(weightPct, "%")}</strong>
                    </span>
                    <span>
                      수익률{" "}
                      <strong className={cn(STRONG_NUMBER_TEXT_CLASS, portfolioPnlColorClass(returnPct))}>
                        {fmtPct(returnPct)}
                      </strong>
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className={cn("text-base", STRONG_NUMBER_TEXT_CLASS, portfolioPnlColorClass(pnl))}>
                    {formatSignedWon(pnl)}
                  </div>
                  <div className={cn("text-xs", STRONG_NUMBER_TEXT_CLASS, portfolioPnlColorClass(returnPct))}>
                    {fmtPct(returnPct)}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {canExpand && (
        <Button type="button" variant="outline" size="sm" onClick={() => setExpanded((value) => !value)}>
          {expanded ? <ChevronUp aria-hidden /> : <ChevronDown aria-hidden />}
          {expanded ? "요약 보기" : `전체 보기 (${allRows.length.toLocaleString("ko-KR")}종목)`}
        </Button>
      )}
    </div>
  );
}

function SectionHeading({ title, help }: { title: string; help: string }) {
  return (
    <div className="flex items-center gap-2">
      <h2 className="text-lg font-bold tracking-normal text-foreground">{title}</h2>
      <InfoHint label={help} />
    </div>
  );
}

function InfoHint({ label }: { label: string }) {
  const anchorRef = useRef<HTMLSpanElement>(null);
  const [position, setPosition] = useState<{ left: number; top: number } | null>(null);

  function show() {
    const anchor = anchorRef.current;
    if (!anchor || typeof window === "undefined") return;
    const rect = anchor.getBoundingClientRect();
    const width = 288;
    const margin = 16;
    const left = Math.min(
      Math.max(margin, rect.left + rect.width / 2 - width / 2),
      window.innerWidth - width - margin,
    );
    const preferredTop = rect.bottom + 10;
    const top = preferredTop > window.innerHeight - 120 ? Math.max(margin, rect.top - 112) : preferredTop;
    setPosition({ left, top });
  }

  return (
    <span
      ref={anchorRef}
      data-testid="portfolio-info-hint"
      className="relative inline-flex shrink-0"
      title={label}
      aria-label={label}
      onMouseEnter={show}
      onMouseLeave={() => setPosition(null)}
      onFocus={show}
      onBlur={() => setPosition(null)}
    >
      <span className="inline-flex size-5 items-center justify-center rounded-full border border-border bg-card text-muted-foreground shadow-sm">
        <HelpCircle className="size-3.5" aria-hidden />
      </span>
      {position && (
        <span
          role="tooltip"
          className="pointer-events-none fixed z-[80] w-72 rounded-lg border border-border bg-popover px-3 py-2 text-xs font-medium leading-relaxed text-popover-foreground shadow-soft"
          style={{ left: position.left, top: position.top }}
        >
          {label}
        </span>
      )}
    </span>
  );
}

function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="font-medium text-muted-foreground">{label}</span>
      <strong className={cn(STRONG_NUMBER_TEXT_CLASS, "text-foreground")}>{value}</strong>
    </div>
  );
}

function EmphasizedText({ text }: { text: string }) {
  const parts = text.split(EMPHASIS_PATTERN);
  return (
    <>
      {parts.map((part, index) => {
        if (!part) return null;
        const tone = part.startsWith("+") ? "text-brand" : part.startsWith("-") ? "text-destructive" : "text-foreground";
        const shouldEmphasize = EMPHASIS_EXACT_PATTERN.test(part);
        return shouldEmphasize ? (
          <strong key={`${part}-${index}`} className={cn("font-bold", tone)}>
            {part}
          </strong>
        ) : (
          <span key={`${part}-${index}`}>{part}</span>
        );
      })}
    </>
  );
}

function buildKpiCards(kpis?: Record<string, unknown>): PortfolioKpiCardModel[] {
  const data = kpis ?? {};
  const total = kpiNumber(data.total_assets ?? data["총자산"]);
  const market = kpiNumber(data.total_market_value ?? data["총평가금액"]);
  const cash = kpiNumber(data.cash ?? data["현금"]);
  const dailyPnl = kpiNumber(data.daily_pnl ?? data["일간손익"]);
  const dailyReturn = kpiNumber(data.daily_return_pct ?? data["일간수익률"]);
  const monthlyReturn = kpiNumber(data.monthly_return_pct ?? data["월간수익률"]);
  const unrealized = kpiNumber(data.unrealized_pnl ?? data["평가손익"]);
  const totalReturn = kpiNumber(data.total_return_pct ?? data["누적손익률"]);
  const cashRatio = kpiNumber(data.cash_ratio_pct ?? data["현금비중"]);
  const holdingsCount = kpiNumber(data.holdings_count ?? data["보유종목수"]);

  return [
    {
      id: "total",
      label: "총자산",
      value: total,
      valueMode: "won",
      delta: dailyReturn,
      deltaMode: "pct",
      deltaSigned: true,
      deltaTone: "pnl",
      help: "현금과 보유 종목 평가금액을 합산한 현재 계좌 기준 자산입니다.",
      detail: `총자산은 평가금액 ${fmtWon(market)}과 현금 ${fmtWon(cash)}을 함께 보는 기준값입니다.`,
      items: [
        { label: "평가금액", value: fmtWon(market) },
        { label: "현금", value: fmtWon(cash) },
        { label: "일간수익률", value: fmtPct(dailyReturn), tone: "pnl" },
      ],
    },
    {
      id: "unrealized",
      label: "평가손익",
      value: unrealized,
      valueMode: "won",
      valueSigned: true,
      delta: totalReturn,
      deltaMode: "pct",
      deltaSigned: true,
      deltaTone: "pnl",
      tone: "pnl",
      help: "현재 보유 종목을 지금 평가했을 때의 미실현 손익입니다.",
      detail: `평가손익은 아직 실현되지 않은 손익입니다. 누적손익률은 ${fmtPct(totalReturn)}입니다.`,
      items: [
        { label: "평가손익", value: formatSignedWon(unrealized), tone: "pnl" },
        { label: "누적손익률", value: fmtPct(totalReturn), tone: "pnl" },
        { label: "보유종목", value: `${holdingsCount.toLocaleString("ko-KR")}개` },
      ],
    },
    {
      id: "daily",
      label: "일간손익",
      value: dailyPnl,
      valueMode: "won",
      valueSigned: true,
      delta: dailyReturn,
      deltaMode: "pct",
      deltaSigned: true,
      deltaTone: "pnl",
      tone: "pnl",
      help: "오늘 하루 기준 평가금액 변화와 손익률입니다.",
      detail: `일간손익은 오늘 포트폴리오가 얼마나 움직였는지 보는 지표입니다. 현재 일간수익률은 ${fmtPct(dailyReturn)}입니다.`,
      items: [
        { label: "일간손익", value: formatSignedWon(dailyPnl), tone: "pnl" },
        { label: "일간수익률", value: fmtPct(dailyReturn), tone: "pnl" },
        { label: "평가금액", value: fmtWon(market) },
      ],
    },
    {
      id: "holdings",
      label: "보유종목",
      value: holdingsCount,
      valueMode: "raw",
      help: "현재 포트폴리오에 들어 있는 개별 종목 수입니다.",
      detail: `보유종목 ${holdingsCount.toLocaleString("ko-KR")}개를 기준으로 집중도와 분산 상태를 함께 봅니다.`,
      items: [
        { label: "보유종목", value: `${holdingsCount.toLocaleString("ko-KR")}개` },
        { label: "현금비중", value: fmtPct(cashRatio, false) },
        { label: "평가금액", value: fmtWon(market) },
      ],
    },
    {
      id: "monthly",
      label: "월간수익률",
      value: monthlyReturn,
      valueMode: "pct",
      valueSigned: true,
      tone: "pnl",
      help: "최근 약 한 달 동안 포트폴리오가 만든 수익률입니다.",
      detail: `월간수익률은 단기 성과 흐름입니다. 현재 값은 ${fmtPct(monthlyReturn)}입니다.`,
      items: [
        { label: "월간수익률", value: fmtPct(monthlyReturn), tone: "pnl" },
        { label: "일간수익률", value: fmtPct(dailyReturn), tone: "pnl" },
        { label: "누적손익률", value: fmtPct(totalReturn), tone: "pnl" },
      ],
    },
  ];
}

function findAutomaticGroup(overview: PortfolioOverviewResponse | undefined, groupId: string) {
  return overview?.groups?.automatic?.find((group) => group.id === groupId);
}

function buildCurveStats(data?: { rows: Record<string, unknown>[] }) {
  const values = (data?.rows ?? [])
    .map((row) => toNumber(row["자산"]))
    .filter((value) => Number.isFinite(value));
  if (values.length === 0) return null;
  const start = values[0] ?? 0;
  const current = values[values.length - 1] ?? 0;
  const change = current - start;
  const changePct = start ? (change / start) * 100 : 0;
  return {
    current,
    change,
    changePct,
    high: Math.max(...values),
    low: Math.min(...values),
    points: values.length,
  };
}

function clampPct(value: number): number {
  if (!Number.isFinite(value) || value <= 0) return 0;
  return Math.min(100, Math.max(3, value));
}

function sortMoverRows(rows: PortfolioHoldingRow[], sortKey: MoverSortKey, direction: SortDirection): PortfolioHoldingRow[] {
  return [...rows].sort((a, b) => {
    if (sortKey === "name") {
      const result = holdingText(a, "종목").localeCompare(holdingText(b, "종목"), "ko-KR");
      return direction === "asc" ? result : -result;
    }
    const aValue = sortKey === "pnl" ? holdingNumber(a, "평가손익") : sortKey === "return" ? holdingNumber(a, "손익률") : holdingNumber(a, "비중");
    const bValue = sortKey === "pnl" ? holdingNumber(b, "평가손익") : sortKey === "return" ? holdingNumber(b, "손익률") : holdingNumber(b, "비중");
    return direction === "desc" ? bValue - aValue : aValue - bValue;
  });
}

function formatKpiValue(value: unknown, mode: ValueMode, signed = mode === "pct"): string {
  const num = toNumber(value);
  if (mode === "pct") return fmtPct(num, signed);
  if (mode === "won") return signed ? formatSignedWon(num) : fmtWon(num);
  return num.toLocaleString("ko-KR");
}

function formatSignedWon(value: number): string {
  const sign = value > 0 ? "+" : value < 0 ? "-" : "";
  return `${sign}₩${Math.round(Math.abs(value)).toLocaleString("ko-KR")}`;
}

function fmtNumber(value: unknown, suffix = ""): string {
  const num = toNumber(value);
  return `${num.toLocaleString("ko-KR", { maximumFractionDigits: 1 })}${suffix}`;
}

function toNumber(value: unknown): number {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  const parsed = Number(String(value ?? "0").replace(/[₩,%+\s]/g, ""));
  return Number.isFinite(parsed) ? parsed : 0;
}

function kpiNumber(value: unknown): number {
  return toNumber(value);
}

function parseDisplayNumber(value: string): number {
  if (value.startsWith("-")) return -toNumber(value);
  return toNumber(value);
}

function portfolioPnlColorClass(value: number): string {
  if (value > 0) return "text-brand";
  if (value < 0) return "text-destructive";
  return "text-muted-foreground";
}

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function holdingText(row: PortfolioHoldingRow, key: string): string {
  return String(row[key] ?? "");
}

function holdingNumber(row: PortfolioHoldingRow, key: string): number {
  return toNumber(row[key]);
}

function symbolName(symbol: string, holdings: PortfolioHoldingRow[]): string {
  const row = holdings.find((item) => item.티커 === symbol);
  return row ? `${row.종목} · ${symbol}` : symbol;
}
