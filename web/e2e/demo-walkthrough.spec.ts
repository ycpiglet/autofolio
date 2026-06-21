// web/e2e/demo-walkthrough.spec.ts
import { expect, test, type Page } from "@playwright/test";

const CSRF_TOKEN = "test-csrf-token-demo-walkthrough";

const OWNER_SESSION = {
  role: "owner",
  username: "admin",
  data_source: "live",
  csrf_token: CSRF_TOKEN,
};

const ENGINE_STATUS = {
  env: "paper",
  auto_trading_enabled: false,
  kill_switch_active: false,
  circuit_breaker: {
    triggered: false,
    threshold_pct: 5,
    consecutive_failures: 0,
    today_pnl: 0,
  },
};

const INVESTOR_PROFILE = {
  username: "admin",
  survey_version: "v1",
  completed: true,
  risk_type: "balanced",
  knowledge_level: "intermediate",
  scores: {
    risk_tolerance: 3,
    knowledge: 3,
    autonomy: 2,
    stability: 3,
  },
  recommended_max_equity_pct: 60,
  recommended_autonomy_level: "confirm_each_trade",
  needs_advanced_survey: false,
  satisfaction_focus: ["drawdown_control", "explainability"],
  last_checkin_at: "2026-06-16T09:00:00+09:00",
  satisfaction_score: 4,
  confidence_score: 4,
  stress_score: 2,
  updated_at: "2026-06-16T09:00:00+09:00",
  completed_at: "2026-06-16T09:00:00+09:00",
};

const EMPTY_TABLE = { columns: [], rows: [] };

const KPI_RESPONSE = {
  총평가금액: 12345678,
  일간손익: 34567,
  일간수익률: 1.23,
  월간수익률: 3.45,
};

const HOLDINGS_TABLE = {
  columns: ["종목코드", "종목명", "수량", "평균단가", "현재가", "평가손익"],
  rows: [
    { 종목코드: "005930", 종목명: "삼성전자", 수량: 10, 평균단가: 72000, 현재가: 74000, 평가손익: 20000 },
  ],
};

const ASSET_CURVE = {
  columns: ["date", "자산"],
  rows: [
    { date: "2026-03-01", 자산: 11000000 },
    { date: "2026-06-01", 자산: 12345678 },
  ],
};

const ALLOCATION_TABLE = {
  columns: ["자산군", "현재비중", "목표비중"],
  rows: [
    { 자산군: "국내주식", 현재비중: 65, 목표비중: 60 },
    { 자산군: "채권", 현재비중: 20, 목표비중: 25 },
  ],
};

const PORTFOLIO_OVERVIEW = {
  kpis: {
    as_of: "2026-06-16T09:00:00+09:00",
    total_assets: 12_345_678,
    total_market_value: 9_345_678,
    cash: 3_000_000,
    cash_ratio_pct: 24.3,
    unrealized_pnl: 234_567,
    daily_pnl: 34_567,
    daily_return_pct: 1.23,
    total_return_pct: 4.56,
    monthly_return_pct: 3.45,
    holdings_count: 3,
  },
  holdings: {
    columns: ["종목", "티커", "자산군", "지역", "섹터", "수량", "평가금액", "평가손익", "손익률", "비중"],
    rows: [
      { 종목: "SK하이닉스", 티커: "000660", 자산군: "주식", 지역: "KR", 섹터: "반도체", 수량: 2, 평가금액: 5_370_000, 평가손익: 1_102_000, 손익률: 25.8, 비중: 57.5 },
      { 종목: "KODEX 200", 티커: "069500", 자산군: "ETF", 지역: "KR", 섹터: "국내지수", 수량: 3, 평가금액: 440_835, 평가손익: 36_163, 손익률: 8.9, 비중: 4.7 },
      { 종목: "삼성전자", 티커: "005930", 자산군: "주식", 지역: "KR", 섹터: "반도체", 수량: 3, 평가금액: 1_087_500, 평가손익: 166_312, 손익률: 18.1, 비중: 11.6 },
    ],
  },
  groups: {
    automatic: [
      {
        id: "asset-class",
        title: "자산군별",
        rows: [
          { name: "주식", weight_pct: 69.1, pnl: 1_268_312, market_value: 6_457_500 },
          { name: "ETF", weight_pct: 4.7, pnl: 36_163, market_value: 440_835 },
          { name: "현금", weight_pct: 24.3, pnl: 0, market_value: 3_000_000 },
        ],
      },
      {
        id: "sector",
        title: "섹터별",
        rows: [
          { name: "반도체", weight_pct: 69.1, pnl: 1_268_312, market_value: 6_457_500 },
          { name: "국내지수", weight_pct: 4.7, pnl: 36_163, market_value: 440_835 },
        ],
      },
    ],
    manual: [],
    saved: [],
  },
  diagnostics: [
    {
      level: "watch",
      title: "단일 종목 집중",
      message: "상위 1종목 비중이 57.5%입니다.",
      action: "보유 목적과 손실 허용 범위를 다시 확인하세요.",
      symbols: ["000660"],
    },
  ],
  top_movers: {
    contributors: [
      { 종목: "SK하이닉스", 티커: "000660", 평가손익: 1_102_000, 손익률: 25.8, 비중: 57.5 },
      { 종목: "삼성전자", 티커: "005930", 평가손익: 166_312, 손익률: 18.1, 비중: 11.6 },
    ],
    detractors: [],
  },
  concentration: {
    top1_weight_pct: 57.5,
    top3_weight_pct: 73.8,
    top5_weight_pct: 73.8,
    held_symbols: 3,
  },
  allocation_gap: {
    columns: ["자산군", "목표%", "현재%", "갭%"],
    rows: [
      { 자산군: "주식", "목표%": 35, "현재%": 69.1, "갭%": 34.1 },
      { 자산군: "ETF", "목표%": 30, "현재%": 4.7, "갭%": -25.3 },
      { 자산군: "현금", "목표%": 15, "현재%": 24.3, "갭%": 9.3 },
    ],
  },
  data_quality: {
    warnings: 0,
    fallback_ticker_name_symbols: [],
    missing_sector_symbols: [],
  },
};

const INDICES_TABLE = {
  columns: ["지수", "현재가", "등락률"],
  rows: [
    { 지수: "KOSPI", 현재가: 2600, 등락률: 0.45 },
    { 지수: "KOSDAQ", 현재가: 860, 등락률: -0.12 },
  ],
};

const FILLS_TABLE = {
  columns: ["일시", "종목명", "구분", "수량", "체결가"],
  rows: [
    { 일시: "2026-06-16 09:30", 종목명: "삼성전자", 구분: "매수", 수량: 10, 체결가: 74000 },
  ],
};

const ORDERS_TABLE = {
  columns: ["일시", "종목코드", "구분", "주문유형", "수량", "주문상태"],
  rows: [
    { 일시: "2026-06-16 09:31", 종목코드: "005930", 구분: "BUY", 주문유형: "LIMIT", 수량: 1, 주문상태: "FILLED" },
  ],
};

const CONDITIONS_TABLE = {
  columns: ["id", "symbol", "side", "target_price", "quantity", "status"],
  rows: [
    { id: 1, symbol: "005930", side: "BUY", target_price: 74250, quantity: 1, status: "ACTIVE" },
  ],
};

const SYMBOLS_MAP = {
  "005930": "삼성전자",
  "069500": "KODEX 200",
};

const INTRADAY_OHLC = {
  columns: ["time", "open", "high", "low", "close", "volume"],
  rows: [
    { time: "2026-06-16 09:00", open: 74000, high: 74500, low: 73800, close: 74200, volume: 12000 },
    { time: "2026-06-16 09:01", open: 74200, high: 74800, low: 74100, close: 74600, volume: 8000 },
  ],
};

const ATTRIBUTION_TABLE = {
  columns: ["source", "target", "value"],
  rows: [
    { source: "국내주식", target: "총수익", value: 8.5 },
    { source: "채권", target: "총수익", value: 2.1 },
  ],
};

const AGENTS_LIST = {
  available: true,
  agents: [
    {
      name: "macro-strategist",
      role: "거시 전략",
      category: "투자 리더십",
      description: "Top-down macro view",
      expert: true,
    },
  ],
};

const PREMARKET_SUMMARY = {
  date: "2026-06-16",
  created_at: "2026-06-16T08:30:00+09:00",
  file: "PREMARKET_20260616.md",
  market_open_reference: "09:00 KST regular session open",
  content: "# 프리마켓 핵심 요약\n\n- 정규장 시작 전 기준점 확인.",
  highlights: ["정규장 시작 전 기준점 확인."],
  agents: AGENTS_LIST.agents,
};

const IC_DECISIONS = [
  {
    id: 1,
    topic: "삼성전자 매수 여부",
    decision: "소량 매수 권장",
    created_at: "2026-06-16T10:00:00Z",
  },
];

const EVENT_FEED_BODY = [
  'data: {"id":"1","kind":"price","symbol":"005930","price":74000,"ts":"2026-06-16T09:00:00Z","message":"삼성전자 가격 업데이트"}',
  "",
].join("\n");

const WALKTHROUGH_PAGES = [
  { path: "/home", heading: "자산 추이 (90일)" },
  { path: "/portfolio", heading: "포트폴리오" },
  { path: "/trade", heading: "매매" },
  { path: "/history", heading: "거래 내역" },
  { path: "/analysis", heading: "분석" },
  { path: "/agents", heading: "에이전트" },
  { path: "/alerts", heading: "알림" },
  { path: "/settings", heading: "설정" },
] as const;

async function mockDemoApis(page: Page) {
  await page.route(/\/api\//, (route) => {
    if (route.request().method() === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(EMPTY_TABLE),
      });
    }
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "ok" }),
    });
  });

  await page.route(/\/api\/auth\/me/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(OWNER_SESSION) }),
  );
  await page.route(/\/api\/auth\/login/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(OWNER_SESSION) }),
  );
  await page.route(/\/api\/engine\/status/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(ENGINE_STATUS) }),
  );
  await page.route(/\/api\/profile\/investor/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(INVESTOR_PROFILE) }),
  );
  await page.route(/\/api\/portfolio\/kpis/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(KPI_RESPONSE) }),
  );
  await page.route(/\/api\/portfolio\/overview/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(PORTFOLIO_OVERVIEW) }),
  );
  await page.route(/\/api\/portfolio\/holdings/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(HOLDINGS_TABLE) }),
  );
  await page.route(/\/api\/portfolio\/asset-curve/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(ASSET_CURVE) }),
  );
  await page.route(/\/api\/portfolio\/allocation-gap/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(ALLOCATION_TABLE) }),
  );
  await page.route(/\/api\/market\/indices/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(INDICES_TABLE) }),
  );
  await page.route(/\/api\/market\/symbols/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(SYMBOLS_MAP) }),
  );
  await page.route(/\/api\/market\/intraday/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(INTRADAY_OHLC) }),
  );
  await page.route(/\/api\/trade\/fills\/recent/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(FILLS_TABLE) }),
  );
  await page.route(/\/api\/trade\/orders/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(ORDERS_TABLE) }),
  );
  await page.route(/\/api\/trade\/conditions/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(CONDITIONS_TABLE) }),
  );
  await page.route(/\/api\/analysis\/attribution/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(ATTRIBUTION_TABLE) }),
  );
  await page.route(/\/api\/agents\/list/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(AGENTS_LIST) }),
  );
  await page.route(/\/api\/agents\/premarket\/summary/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(PREMARKET_SUMMARY) }),
  );
  await page.route(/\/api\/agents\/ic\/decisions/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(IC_DECISIONS) }),
  );
  await page.route(/\/api\/stream\/events/, (route) =>
    route.fulfill({
      status: 200,
      headers: { "content-type": "text/event-stream; charset=utf-8" },
      body: EVENT_FEED_BODY,
    }),
  );

}

async function loginAsOwner(page: Page) {
  await page.goto("/login");
  await page.getByLabel("아이디").fill("admin");
  await page.getByLabel("비밀번호").fill("secret");
  await page.getByRole("button", { name: /^로그인$/ }).click();
  await page.goto("/home");
  await expect(page).toHaveURL(/\/home/, { timeout: 15_000 });
}

test.describe("Demo walkthrough — Next.js replacement surface", () => {
  test("owner can walk through the 8 primary app pages", async ({ page }) => {
    await mockDemoApis(page);
    await loginAsOwner(page);

    for (const item of WALKTHROUGH_PAGES) {
      await test.step(`visit ${item.path}`, async () => {
        await page.goto(item.path);
        await expect(page.getByRole("navigation", { name: "사이드바 내비게이션" })).toBeVisible({ timeout: 10_000 });
        await expect(page.getByRole("heading", { name: item.heading, exact: true })).toBeVisible({
          timeout: 10_000,
        });
        if (item.path === "/portfolio") {
          const kpis = page.getByLabel("포트폴리오 핵심 지표");
          await expect(kpis.locator('[data-kpi-id="unrealized"]')).toContainText("+4.56%");
          await expect(kpis.locator('[data-kpi-id="cash"]')).toHaveCount(0);

          await page.getByRole("button", { name: "진단" }).click();
          await expect(page.locator("strong", { hasText: "보유 목적" })).toBeVisible();
          await expect(page.locator("strong", { hasText: "손실 허용 범위" })).toBeVisible();
        }
      });
    }
  });
});
