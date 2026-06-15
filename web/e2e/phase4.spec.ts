// web/e2e/phase4.spec.ts
import { test, expect, type Page } from "@playwright/test";

// ── Fixtures ──────────────────────────────────────────────────────────────

const CSRF_TOKEN = "test-csrf-token-phase4";

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

const AGENTS_LIST = {
  available: true,
  agents: [
    { name: "macro-strategist", role: "거시 전략" },
    { name: "kr-equity-specialist", role: "국내 주식" },
  ],
};

const AGENTS_ASK_RESPONSE = {
  answer: "삼성전자는 현재 매력적인 밸류에이션에 있습니다.",
};

const IC_RUN_RESPONSE = { job_id: "test-job-123" };

const IC_DECISIONS = [
  {
    id: 1,
    topic: "삼성전자 매수 여부",
    decision: "소량 매수 권장",
    created_at: "2026-06-14T10:00:00Z",
  },
];

// ── SSE mock bodies ────────────────────────────────────────────────────────

// IC stream: one step event + one done event
const IC_STREAM_BODY = [
  "event: step",
  'data: {"agent":"macro-strategist","content":"거시 환경을 분석 중입니다.","kind":"agent"}',
  "",
  "event: done",
  'data: {"decision":"단기 매수 전략 권장"}',
  "",
].join("\n");

// Event feed: one unnamed message + one named price event
const EVENT_FEED_BODY = [
  'data: {"id":"1","kind":"price","symbol":"005930","price":74000,"ts":"2026-06-15T09:00:00Z","message":"삼성전자 가격 업데이트"}',
  "",
  "event: price",
  'data: {"id":"2","kind":"price","symbol":"000660","price":145000,"ts":"2026-06-15T09:00:01Z","message":"SK하이닉스 가격 업데이트"}',
  "",
].join("\n");

// ── Helpers ────────────────────────────────────────────────────────────────

async function mockBackground(page: Page) {
  // Catch-all: GET /api/** → empty table (LIFO: register first = lowest priority)
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

  // Auth me (includes csrf_token)
  await page.route(/\/api\/auth\/me/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(OWNER_SESSION),
    }),
  );

  // agents/list
  await page.route(/\/api\/agents\/list/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(AGENTS_LIST),
    }),
  );

  // agents/ask (POST)
  await page.route(/\/api\/agents\/ask/, (route) => {
    if (route.request().method() === "POST") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(AGENTS_ASK_RESPONSE),
      });
    }
    return route.continue();
  });

  // agents/ic/run (POST)
  await page.route(/\/api\/agents\/ic\/run/, (route) => {
    if (route.request().method() === "POST") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(IC_RUN_RESPONSE),
      });
    }
    return route.continue();
  });

  // agents/ic/stream/:job_id (SSE)
  await page.route(/\/api\/agents\/ic\/stream\//, (route) =>
    route.fulfill({
      status: 200,
      headers: { "content-type": "text/event-stream; charset=utf-8" },
      body: IC_STREAM_BODY,
    }),
  );

  // agents/ic/decisions (GET)
  await page.route(/\/api\/agents\/ic\/decisions/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(IC_DECISIONS),
    }),
  );

  // stream/events (SSE)
  await page.route(/\/api\/stream\/events/, (route) =>
    route.fulfill({
      status: 200,
      headers: { "content-type": "text/event-stream; charset=utf-8" },
      body: EVENT_FEED_BODY,
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

test.describe("Phase 4 — /agents page", () => {
  test("shows agent team list from /api/agents/list", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/agents");

    // Team should appear
    await expect(page.getByTestId("agent-team")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByTestId("agent-team").getByText("macro-strategist")).toBeVisible();
    await expect(page.getByTestId("agent-team").getByText("kr-equity-specialist")).toBeVisible();
  });

  test("Ask panel: submit question → AgentMessage answer appears", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/agents");

    // Wait for agent panel to load
    await expect(page.getByTestId("agent-team")).toBeVisible({ timeout: 10_000 });

    // Fill question
    await page.getByLabel("질문").fill("삼성전자 전망은?");
    await page.getByRole("button", { name: "질문하기" }).click();

    // Answer should appear
    await expect(
      page.getByText("삼성전자는 현재 매력적인 밸류에이션에 있습니다."),
    ).toBeVisible({ timeout: 10_000 });
  });

  test("IC run: topic submit → streams step event → shows done decision", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/agents");

    await expect(page.getByTestId("agent-team")).toBeVisible({ timeout: 10_000 });

    // Fill topic and run
    await page.getByLabel("IC 토픽").fill("삼성전자 매수 여부");
    await page.getByRole("button", { name: "실행" }).click();

    // IC transcript should appear
    await expect(page.getByTestId("ic-transcript")).toBeVisible({ timeout: 10_000 });

    // Done decision should appear (the done event fires from the mocked SSE body)
    await expect(page.getByTestId("ic-decision")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText("단기 매수 전략 권장")).toBeVisible({ timeout: 5_000 });
  });

  test("past decisions list appears", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/agents");

    await expect(page.getByTestId("past-decisions")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText("삼성전자 매수 여부")).toBeVisible();
    await expect(page.getByText("소량 매수 권장")).toBeVisible();
  });

  test("unavailable agents → EmptyState shown", async ({ page }) => {
    await mockBackground(page);

    // Override agents/list AFTER mockBackground so this takes LIFO priority
    await page.route(/\/api\/agents\/list/, (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ available: false, message: "에이전트 오프라인", agents: [] }),
      }),
    );

    await loginAsOwner(page);

    await page.goto("/agents");

    await expect(page.getByText("에이전트 사용 불가")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText("에이전트 오프라인")).toBeVisible();
  });
});

test.describe("Phase 4 — /alerts page", () => {
  test("renders EventFeed and shows at least one event item", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/alerts");

    // EventFeed container should appear
    await expect(page.getByTestId("event-feed")).toBeVisible({ timeout: 10_000 });

    // Should show at least one feed item (from the mocked SSE body)
    await expect(page.getByTestId("feed-list")).toBeVisible({ timeout: 10_000 });
    await expect(
      page.getByText("삼성전자 가격 업데이트"),
    ).toBeVisible({ timeout: 10_000 });
  });

  test("alerts page has correct heading", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/alerts");

    await expect(page.getByRole("heading", { name: "알림", exact: true })).toBeVisible({
      timeout: 10_000,
    });
  });

  test("AppShell navigation visible on /alerts", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/alerts");

    await expect(page.getByRole("navigation")).toBeVisible();
  });
});
