// web/e2e/dashboard.spec.ts
import { test, expect, type Page } from "@playwright/test";

// ── Fixtures ────────────────────────────────────────────────────────────────

const MEMBER_SESSION = { role: "member", username: "member1", data_source: "backend" };

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

const KPI_RESPONSE = {
  총평가금액: 12345678,
  일간손익: 34567,
  일간수익률: 1.23,
  월간수익률: 3.45,
};

const HOLDINGS_TABLE = {
  columns: ["종목", "티커", "자산군", "수량", "평단", "현재가", "평가금액", "평가손익", "손익률", "비중"],
  rows: [
    {
      종목: "삼성전자",
      티커: "005930",
      자산군: "국내주식",
      지역: "한국",
      섹터: "반도체",
      전략: "핵심",
      수량: 10,
      평단: 72000,
      현재가: 74000,
      평가금액: 740000,
      평가손익: 20000,
      손익률: 2.78,
      비중: 60,
    },
    {
      종목: "SK하이닉스",
      티커: "000660",
      자산군: "국내주식",
      지역: "한국",
      섹터: "반도체",
      전략: "위성",
      수량: 5,
      평단: 140000,
      현재가: 145000,
      평가금액: 725000,
      평가손익: 25000,
      손익률: 3.57,
      비중: 40,
    },
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
    { 자산군: "국내주식", 현재비중: 65.0, 목표비중: 60.0 },
    { 자산군: "채권", 현재비중: 20.0, 목표비중: 25.0 },
    { 자산군: "현금", 현재비중: 15.0, 목표비중: 15.0 },
  ],
};

const PORTFOLIO_OVERVIEW = {
  kpis: {
    total_assets: 12345678,
    total_market_value: 1465000,
    cash: 10880678,
    daily_pnl: 34567,
    daily_return_pct: 1.23,
    monthly_return_pct: 3.45,
    unrealized_pnl: 45000,
    total_return_pct: 3.16,
    cash_ratio_pct: 88.1,
    holdings_count: 2,
    as_of: "2026-06-19T09:30:00+09:00",
  },
  holdings: HOLDINGS_TABLE,
  groups: {
    automatic: [
      {
        id: "asset-class",
        title: "자산군 노출",
        rows: [
          { name: "국내주식", weight_pct: 100, pnl: 45000 },
        ],
      },
      {
        id: "sector",
        title: "섹터 노출",
        rows: [
          { name: "반도체", weight_pct: 100, pnl: 45000 },
        ],
      },
    ],
    manual: [],
    saved: [],
  },
  diagnostics: [],
  top_movers: {
    contributors: HOLDINGS_TABLE.rows,
    detractors: [],
  },
  concentration: {
    top1_weight_pct: 60,
    top3_weight_pct: 100,
    top5_weight_pct: 100,
  },
  allocation_gap: ALLOCATION_TABLE,
  data_quality: {},
};

const INDICES_TABLE = {
  columns: ["지수", "현재가", "등락률"],
  rows: [
    { 지수: "KOSPI", 현재가: 2600.00, 등락률: 0.45 },
    { 지수: "KOSDAQ", 현재가: 860.00, 등락률: -0.12 },
  ],
};

const FILLS_TABLE = {
  columns: ["일시", "종목명", "구분", "수량", "체결가"],
  rows: [
    { 일시: "2026-06-14 09:30", 종목명: "삼성전자", 구분: "매수", 수량: 10, 체결가: 74000 },
  ],
};

const EMPTY_TABLE = { columns: [], rows: [] };

// ── Mock helper ─────────────────────────────────────────────────────────────

/**
 * Registers all API mocks needed for the dashboard pages.
 * LIFO order: catch-all first, specific routes after (last wins).
 */
async function mockDashboardApis(page: Page) {
  // 1. Catch-all: any remaining GET /api/** → empty table
  await page.route(/\/api\//, (route) => {
    if (route.request().method() === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(EMPTY_TABLE),
      });
    }
    return route.continue();
  });

  // 2. Engine status (TopStatusBar)
  await page.route(/\/api\/engine\/status/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(ENGINE_STATUS),
    }),
  );

  // 3. Auth session
  await page.route(/\/api\/auth\/me/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(MEMBER_SESSION),
    }),
  );

  // 4. Portfolio KPIs (plain dict)
  await page.route(/\/api\/portfolio\/overview/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(PORTFOLIO_OVERVIEW),
    }),
  );

  // 5. Portfolio KPIs (plain dict)
  await page.route(/\/api\/portfolio\/kpis/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(KPI_RESPONSE),
    }),
  );

  // 6. Holdings
  await page.route(/\/api\/portfolio\/holdings/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(HOLDINGS_TABLE),
    }),
  );

  // 7. Asset curve
  await page.route(/\/api\/portfolio\/asset-curve/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(ASSET_CURVE),
    }),
  );

  // 8. Allocation gap
  await page.route(/\/api\/portfolio\/allocation-gap/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(ALLOCATION_TABLE),
    }),
  );

  // 9. Market indices
  await page.route(/\/api\/market\/indices/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(INDICES_TABLE),
    }),
  );

  // 10. Recent fills
  await page.route(/\/api\/trade\/fills\/recent/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(FILLS_TABLE),
    }),
  );

}

// ── Shared: reach /home as an already approved member session ────────────────

async function openHomeAsMember(page: Page) {
  await page.goto("/home");
  await expect(page).toHaveURL(/\/home/, { timeout: 15_000 });
}

// ── Tests ────────────────────────────────────────────────────────────────────

test.describe("Dashboard — Home", () => {
  test("shows a KPI value on /home", async ({ page }) => {
    await mockDashboardApis(page);
    await openHomeAsMember(page);

    // KPI value should contain the formatted total (₩12,345,678)
    // Use a broad text match so minor formatting differences don't break it
    await expect(page.getByText(/12,345,678/)).toBeVisible({ timeout: 10_000 });
  });

  test("renders holdings table with Korean header on /home", async ({ page }) => {
    await mockDashboardApis(page);
    await openHomeAsMember(page);

    // Holdings table should show Korean column header "종목"
    // Use .first() because multiple tables on the page share this header name
    await expect(page.getByRole("columnheader", { name: "종목" }).first()).toBeVisible({
      timeout: 10_000,
    });

    // And at least one data row
    await expect(page.getByRole("cell", { name: "삼성전자" }).first()).toBeVisible({
      timeout: 5_000,
    });
  });

  test("shows AppShell navigation on /home", async ({ page }) => {
    await mockDashboardApis(page);
    await openHomeAsMember(page);

    await expect(page.getByRole("navigation")).toBeVisible();
  });
});

test.describe("Dashboard — Portfolio", () => {
  test("renders HoldingsTable on /portfolio", async ({ page }) => {
    await mockDashboardApis(page);
    await openHomeAsMember(page);

    // Navigate to /portfolio
    await page.goto("/portfolio");

    await page.getByRole("button", { name: "보유", exact: true }).click();

    // HoldingsTable: Korean column header visible
    await expect(page.getByRole("columnheader", { name: "종목" }).first()).toBeVisible({
      timeout: 10_000,
    });
  });

  test("renders allocation chart container on /portfolio", async ({ page }) => {
    await mockDashboardApis(page);
    await openHomeAsMember(page);

    await page.goto("/portfolio");

    // AllocationChart renders a div with data-testid="allocation-chart"
    await expect(page.locator('[data-testid="allocation-chart"]')).toBeVisible({
      timeout: 10_000,
    });
  });

  test("AppShell navigation visible on /portfolio", async ({ page }) => {
    await mockDashboardApis(page);
    await openHomeAsMember(page);

    await page.goto("/portfolio");

    await expect(page.getByRole("navigation", { name: "사이드바 내비게이션" })).toBeVisible();
  });
});
