// web/e2e/finance-roadmap.spec.ts — TASK-174 Finance Roadmap UI Preview
import { test, expect, type Page } from "@playwright/test";

// ── Fixtures ──────────────────────────────────────────────────────────────

const CSRF_TOKEN = "test-csrf-token-finance-roadmap";

const OWNER_SESSION = {
  role: "owner",
  username: "admin",
  data_source: "live",
  csrf_token: CSRF_TOKEN,
};

// Synthetic fixture — mirrors compute_goal_gap() output for the default contract.
// as_of is always "fixture_static" (not a date).
const FINANCE_ROADMAP_FIXTURE = {
  preview_mode: true,
  preview_label: "read-only planning preview — no action, no order",
  as_of: "fixture_static",
  fixture_id: "synthetic_plan_5_expected_around_10",
  planned: {
    planned_return_pct: 5.0,
    planning_horizon: "quarter",
  },
  expected: {
    low_pct: 8.0,
    high_pct: 10.0,
    confidence: "medium",
    not_guaranteed: true,
  },
  gap: {
    low_pct_points: 3.0,
    high_pct_points: 5.0,
  },
  allocation_drift: "candidate_review_signal_only",
  data_quality_flags: [
    { id: "cashflow_assumptions", owner_decision_required: true },
    { id: "professional_review", owner_decision_required: true },
  ],
  review_candidates: [
    {
      id: "synthetic_allocation_drift_review",
      candidate_for_owner_review_only: true,
      action_permitted_now: false,
      no_trade_instruction: true,
      why_flagged:
        "expected range is above planned return in the synthetic fixture",
      missing_evidence: [
        "portfolio source freshness",
        "risk constraints",
        "professional review if externalized",
      ],
    },
  ],
  timeline_candidates: [
    {
      id: "synthetic_quarter_review",
      candidate_for_owner_review_only: true,
      action_permitted_now: false,
      horizon: "quarter",
      trigger: "all required evidence is available and reviewed",
      required_evidence: [
        "read-only source freshness",
        "cashflow assumptions",
        "payment evidence posture",
        "compliance wording review",
      ],
    },
  ],
  boundary: {
    synthetic_fixture_only: true,
    read_only_planning_input_only: true,
    not_investment_recommendation: true,
    no_trade_instruction: true,
    no_order_execution: true,
    not_tax_accounting_final_advice: true,
  },
};

// ── Helpers ────────────────────────────────────────────────────────────────

async function mockBackground(page: Page) {
  // Catch-all: GET /api/** → empty object (lowest LIFO priority)
  await page.route(/\/api\//, (route) => {
    if (route.request().method() === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({}),
      });
    }
    return route.continue();
  });

  // Auth me
  await page.route(/\/api\/auth\/me/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(OWNER_SESSION),
    }),
  );

  // Finance roadmap goal-gap endpoint
  await page.route(/\/api\/finance-roadmap\/goal-gap/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(FINANCE_ROADMAP_FIXTURE),
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

test.describe("Finance Roadmap — /finance-roadmap page (TASK-174)", () => {
  test("renders page heading and AppShell navigation", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/finance-roadmap");

    // Page heading
    await expect(
      page.getByRole("heading", { name: "재무 로드맵 미리보기", exact: true }),
    ).toBeVisible({ timeout: 10_000 });

    // AppShell sidebar nav present
    await expect(page.getByRole("navigation")).toBeVisible();
  });

  test("panel loads and shows preview badge (fixture_static rendered as label)", async ({
    page,
  }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/finance-roadmap");

    await expect(
      page.locator('[data-testid="finance-roadmap-panel"]'),
    ).toBeVisible({ timeout: 10_000 });

    // as_of="fixture_static" rendered as preview badge, not a date
    await expect(
      page.locator('[data-testid="preview-badge"]'),
    ).toContainText("미리보기", { timeout: 5_000 });
  });

  test("plan vs expected section shows fixture planned return and range", async ({
    page,
  }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/finance-roadmap");

    await expect(
      page.locator('[data-testid="plan-vs-expected"]'),
    ).toBeVisible({ timeout: 10_000 });

    // planned_return_pct: 5.0 → fmtPct(5.0, signed=true) = "+5.00%"
    await expect(
      page.locator('[data-testid="planned-return"]'),
    ).toContainText("5.00%", { timeout: 5_000 });

    // expected range: 8.0% ~ 10.0%
    await expect(
      page.locator('[data-testid="expected-range"]'),
    ).toContainText("8.00%", { timeout: 5_000 });
  });

  test("gap matrix section shows gap values", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/finance-roadmap");

    await expect(
      page.locator('[data-testid="gap-matrix"]'),
    ).toBeVisible({ timeout: 10_000 });

    // gap low: 3.0 → "+3.00%"
    await expect(
      page.locator('[data-testid="gap-low"]'),
    ).toContainText("3.00%", { timeout: 5_000 });
  });

  test("timeline candidates section renders with fixture candidate id", async ({
    page,
  }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/finance-roadmap");

    await expect(
      page.locator('[data-testid="timeline-candidates"]'),
    ).toBeVisible({ timeout: 10_000 });

    await expect(
      page.locator('[data-testid="timeline-candidates"]').getByText(
        "synthetic_quarter_review",
      ),
    ).toBeVisible({ timeout: 5_000 });
  });

  test("review candidates section is visible", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/finance-roadmap");

    await expect(
      page.locator('[data-testid="review-candidates"]'),
    ).toBeVisible({ timeout: 10_000 });

    await expect(
      page.locator('[data-testid="review-candidates"]').getByText(
        "synthetic_allocation_drift_review",
      ),
    ).toBeVisible({ timeout: 5_000 });
  });

  test("operations support gaps section shows missing evidence items", async ({
    page,
  }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/finance-roadmap");

    await expect(
      page.locator('[data-testid="data-quality-flags"]'),
    ).toBeVisible({ timeout: 10_000 });

    await expect(
      page
        .locator('[data-testid="data-quality-flags"]')
        .getByText("cashflow_assumptions"),
    ).toBeVisible({ timeout: 5_000 });
  });

  test("panel error state shown when API returns 500", async ({ page }) => {
    // Auth OK, but finance-roadmap endpoint fails.
    // Routes are matched LIFO — register catch-all first so specific routes win.
    await page.route(/\/api\//, (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({}),
      }),
    );
    await page.route(/\/api\/auth\/me/, (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(OWNER_SESSION),
      }),
    );
    await page.route(/\/api\/finance-roadmap\/goal-gap/, (route) =>
      route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Internal server error" }),
      }),
    );

    await loginAsOwner(page);
    await page.goto("/finance-roadmap");

    // EmptyState with error illustration should appear
    await expect(
      page.getByRole("status", { name: "데이터를 불러오지 못했습니다." }),
    ).toBeVisible({ timeout: 10_000 });
  });

  test("unauthenticated user redirected to login", async ({ page }) => {
    await page.route(/\/api\/auth\/me/, (route) =>
      route.fulfill({
        status: 401,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Not authenticated" }),
      }),
    );
    await page.route(/\/api\/auth\/login/, (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(OWNER_SESSION),
      }),
    );
    await page.route(/\/api\//, (route) =>
      route.fulfill({
        status: 401,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Not authenticated" }),
      }),
    );

    await page.goto("/finance-roadmap");
    await expect(page).toHaveURL(/\/login/, { timeout: 10_000 });
  });
});
