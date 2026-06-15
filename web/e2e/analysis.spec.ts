// web/e2e/analysis.spec.ts
import { test, expect, type Page } from "@playwright/test";

// ── Fixtures ──────────────────────────────────────────────────────────────

const CSRF_TOKEN = "test-csrf-token-phase5";

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

const EMPTY_TABLE = { columns: [], rows: [] };

// OHLC intraday mock — lightweight-charts candlestick format
// time column must be ISO or YYYY-MM-DD strings
const INTRADAY_OHLC = {
  columns: ["time", "open", "high", "low", "close", "volume"],
  rows: [
    { time: "2026-06-12 09:00", open: 74000, high: 74500, low: 73800, close: 74200, volume: 12000 },
    { time: "2026-06-12 09:01", open: 74200, high: 74800, low: 74100, close: 74600, volume: 8000 },
    { time: "2026-06-12 09:02", open: 74600, high: 75000, low: 74400, close: 74900, volume: 9500 },
  ],
};

const BACKTEST_RESULT = {
  symbol: "005930",
  strategy: "MA Crossover (5/20)",
  start: "2025-01-01",
  end: "2025-12-31",
  total_return_pct: 15.42,
  trade_count: 12,
  win_rate_pct: 66.67,
  max_drawdown_pct: 8.21,
};

const VAR_RESULT = {
  total_value: 12345678,
  n_simulations: 10000,
  horizon_days: 10,
  var_95: 450000,
  var_99: 680000,
  cvar_95: 520000,
  max_drawdown_pct: 12.5,
};

const VAR_RESULT_WITH_NOTE = {
  ...VAR_RESULT,
  note: "포트폴리오가 비어있어 시뮬레이션 결과가 제한적입니다.",
};

const SCENARIO_TABLE = {
  columns: ["시나리오", "영향 (%)", "비고"],
  rows: [
    { "시나리오": "금리 +1%p", "영향 (%)": -3.2, "비고": "채권 비중 영향" },
    { "시나리오": "주가 -20%", "영향 (%)": -15.8, "비고": "주식 비중 영향" },
  ],
};

const ATTRIBUTION_TABLE = {
  columns: ["source", "target", "value"],
  rows: [
    { source: "국내주식", target: "총수익", value: 8.5 },
    { source: "채권", target: "총수익", value: 2.1 },
    { source: "현금", target: "총수익", value: 0.3 },
  ],
};

// ── Helpers ────────────────────────────────────────────────────────────────

async function mockBackground(page: Page) {
  // Catch-all: GET /api/** → empty table (lowest LIFO priority)
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

  // Engine status
  await page.route(/\/api\/engine\/status/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(ENGINE_STATUS),
    }),
  );

  // Auth me
  await page.route(/\/api\/auth\/me/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(OWNER_SESSION),
    }),
  );

  // Intraday OHLC
  await page.route(/\/api\/market\/intraday/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(INTRADAY_OHLC),
    }),
  );

  // Backtest
  await page.route(/\/api\/analysis\/backtest/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(BACKTEST_RESULT),
    }),
  );

  // VaR
  await page.route(/\/api\/analysis\/var/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(VAR_RESULT),
    }),
  );

  // Scenario
  await page.route(/\/api\/analysis\/scenario/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(SCENARIO_TABLE),
    }),
  );

  // What-if
  await page.route(/\/api\/analysis\/whatif/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ expected_return_pct: 1.23, risk_delta_pct: 0.45 }),
    }),
  );

  // Attribution
  await page.route(/\/api\/analysis\/attribution/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(ATTRIBUTION_TABLE),
    }),
  );
}

async function loginAsOwner(page: Page) {
  await page.route(/\/api\/auth\/login/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(OWNER_SESSION),
    }),
  );

  await page.goto("/login");
  await page.getByLabel("아이디").fill("admin");
  await page.getByLabel("비밀번호").fill("secret");
  await page.getByRole("button", { name: /^로그인$/ }).click();
  await expect(page).toHaveURL(/\/home/, { timeout: 15_000 });
}

// ── Tests ─────────────────────────────────────────────────────────────────

test.describe("Phase 5 — /analysis page", () => {
  test("renders /analysis with AppShell navigation", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/analysis");

    // Page heading
    await expect(
      page.getByRole("heading", { name: "분석", exact: true }),
    ).toBeVisible({ timeout: 10_000 });

    // AppShell nav
    await expect(page.getByRole("navigation")).toBeVisible();
  });

  test("candle chart container appears after intraday fetch", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/analysis");

    // The candle-chart-section wrapper appears (symbol selector + chart)
    await expect(
      page.locator('[data-testid="candle-chart-section"]'),
    ).toBeVisible({ timeout: 10_000 });

    // The actual chart div appears once data loads (may take a moment for dynamic import)
    await expect(
      page.locator('[data-testid="candle-chart"]'),
    ).toBeVisible({ timeout: 15_000 });
  });

  test("backtest form submits and shows result KPIs", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/analysis");

    // Wait for backtest panel to appear
    await expect(page.locator('[data-testid="backtest-panel"]')).toBeVisible({
      timeout: 10_000,
    });

    // Click submit
    await page.getByRole("button", { name: "백테스트 실행" }).click();

    // Result KPIs appear
    await expect(
      page.locator('[data-testid="backtest-result"]'),
    ).toBeVisible({ timeout: 10_000 });

    // Check specific KPI values appear in the backtest result area
    await expect(
      page.locator('[data-testid="backtest-result"]').getByText(/15\.42/).first(),
    ).toBeVisible({ timeout: 5_000 });
  });

  test("VaR form submits and shows VaR result", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/analysis");

    // Wait for var panel
    await expect(page.locator('[data-testid="var-panel"]')).toBeVisible({
      timeout: 10_000,
    });

    // Submit
    await page.getByRole("button", { name: "VaR 계산" }).click();

    // Result appears
    await expect(page.locator('[data-testid="var-result"]')).toBeVisible({
      timeout: 10_000,
    });
  });

  test("VaR note banner shown when note field present", async ({ page }) => {
    await mockBackground(page);

    // Override VaR route with note version (registered AFTER mockBackground — LIFO priority)
    await page.route(/\/api\/analysis\/var/, (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(VAR_RESULT_WITH_NOTE),
      }),
    );

    await loginAsOwner(page);
    await page.goto("/analysis");

    await expect(page.locator('[data-testid="var-panel"]')).toBeVisible({
      timeout: 10_000,
    });
    await page.getByRole("button", { name: "VaR 계산" }).click();

    await expect(
      page.getByText("포트폴리오가 비어있어 시뮬레이션 결과가 제한적입니다."),
    ).toBeVisible({ timeout: 10_000 });
  });

  test("scenario table renders with Korean column headers", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/analysis");

    // Scenario DataTable should show the column "시나리오"
    await expect(
      page.getByRole("columnheader", { name: "시나리오" }),
    ).toBeVisible({ timeout: 10_000 });

    // And one data row
    await expect(page.getByRole("cell", { name: "금리 +1%p" })).toBeVisible({
      timeout: 5_000,
    });
  });

  test("attribution Sankey container appears", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/analysis");

    // Attribution chart (Sankey or bar fallback) container appears
    await expect(
      page.locator('[data-testid="attribution-sankey"]'),
    ).toBeVisible({ timeout: 15_000 });
  });

  test("backtest API error shows visible error message", async ({ page }) => {
    await mockBackground(page);

    // Override backtest with error
    await page.route(/\/api\/analysis\/backtest/, (route) =>
      route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Internal server error" }),
      }),
    );

    await loginAsOwner(page);
    await page.goto("/analysis");

    await expect(page.locator('[data-testid="backtest-panel"]')).toBeVisible({
      timeout: 10_000,
    });

    await page.getByRole("button", { name: "백테스트 실행" }).click();

    // Error alert appears
    await expect(
      page.getByRole("alert").filter({ hasText: /백테스트 오류/ }),
    ).toBeVisible({ timeout: 10_000 });
  });
});
