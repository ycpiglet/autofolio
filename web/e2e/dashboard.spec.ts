// web/e2e/dashboard.spec.ts
import { test, expect, type Page } from "@playwright/test";

// ── Fixtures ────────────────────────────────────────────────────────────────

const GUEST_SESSION = { role: "guest", username: null, data_source: "demo" };

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
  columns: ["종목명", "수량", "평균단가", "현재가", "평가손익"],
  rows: [
    { 종목명: "삼성전자", 수량: 10, 평균단가: 72000, 현재가: 74000, 평가손익: 20000 },
    { 종목명: "SK하이닉스", 수량: 5, 평균단가: 140000, 현재가: 145000, 평가손익: 25000 },
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
      body: JSON.stringify(GUEST_SESSION),
    }),
  );

  // 4. Portfolio KPIs (plain dict)
  await page.route(/\/api\/portfolio\/kpis/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(KPI_RESPONSE),
    }),
  );

  // 5. Holdings
  await page.route(/\/api\/portfolio\/holdings/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(HOLDINGS_TABLE),
    }),
  );

  // 6. Asset curve
  await page.route(/\/api\/portfolio\/asset-curve/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(ASSET_CURVE),
    }),
  );

  // 7. Allocation gap
  await page.route(/\/api\/portfolio\/allocation-gap/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(ALLOCATION_TABLE),
    }),
  );

  // 8. Market indices
  await page.route(/\/api\/market\/indices/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(INDICES_TABLE),
    }),
  );

  // 9. Recent fills
  await page.route(/\/api\/trade\/fills\/recent/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(FILLS_TABLE),
    }),
  );

  // 10. Login POST (catch-all won't match POST; add explicit mock)
  await page.route(/\/api\/auth\/login/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(GUEST_SESSION),
    }),
  );
}

// ── Shared: log in as guest and reach /home ──────────────────────────────────

async function loginAsGuest(page: Page) {
  await page.goto("/login");
  await page.getByRole("button", { name: /게스트 데모 시작/ }).click();
  await expect(page).toHaveURL(/\/home/, { timeout: 15_000 });
}

// ── Tests ────────────────────────────────────────────────────────────────────

test.describe("Dashboard — Home", () => {
  test("shows a KPI value on /home", async ({ page }) => {
    await mockDashboardApis(page);
    await loginAsGuest(page);

    // KPI value should contain the formatted total (₩12,345,678)
    // Use a broad text match so minor formatting differences don't break it
    await expect(page.getByText(/12,345,678/)).toBeVisible({ timeout: 10_000 });
  });

  test("renders holdings table with Korean header on /home", async ({ page }) => {
    await mockDashboardApis(page);
    await loginAsGuest(page);

    // Holdings table should show Korean column header "종목명"
    await expect(page.getByRole("columnheader", { name: "종목명" })).toBeVisible({
      timeout: 10_000,
    });

    // And at least one data row
    await expect(page.getByRole("cell", { name: "삼성전자" })).toBeVisible({
      timeout: 5_000,
    });
  });

  test("shows AppShell navigation on /home", async ({ page }) => {
    await mockDashboardApis(page);
    await loginAsGuest(page);

    await expect(page.getByRole("navigation")).toBeVisible();
  });
});

test.describe("Dashboard — Portfolio", () => {
  test("renders HoldingsTable on /portfolio", async ({ page }) => {
    await mockDashboardApis(page);
    await loginAsGuest(page);

    // Navigate to /portfolio
    await page.goto("/portfolio");

    // HoldingsTable: Korean column header visible
    await expect(page.getByRole("columnheader", { name: "종목명" }).first()).toBeVisible({
      timeout: 10_000,
    });
  });

  test("renders allocation chart container on /portfolio", async ({ page }) => {
    await mockDashboardApis(page);
    await loginAsGuest(page);

    await page.goto("/portfolio");

    // AllocationChart renders a div with data-testid="allocation-chart"
    await expect(page.locator('[data-testid="allocation-chart"]')).toBeVisible({
      timeout: 10_000,
    });
  });

  test("AppShell navigation visible on /portfolio", async ({ page }) => {
    await mockDashboardApis(page);
    await loginAsGuest(page);

    await page.goto("/portfolio");

    await expect(page.getByRole("navigation")).toBeVisible();
  });
});
