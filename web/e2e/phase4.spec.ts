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

// Whitelist symbol map for the briefing symbol picker
const SYMBOLS_MAP = {
  "005930": "삼성전자",
  "069500": "KODEX 200",
};

// Per-symbol research briefing (READ-ONLY)
const RESEARCH_RESPONSE = {
  symbol: "005930",
  name: "삼성전자",
  price: 75000,
  fundamental: { per: 12.5, pbr: 1.3 },
  disclosures: {
    columns: ["date", "title", "category"],
    rows: [
      { date: "20260612", title: "사업보고서 제출", category: "정기공시" },
    ],
  },
  disclosure_gate: { symbol: "005930", blocked: false, reason: "" },
  proposal: {
    symbol: "005930",
    side: "BUY",
    target_price: 74250,
    quantity: 1,
    order_type: "LIMIT",
    allow_market_fallback: false,
    rationale: "현재가보다 1% 낮은 보수적 매수 대기 조건 예시. 재무 지표: PER 12.5, PBR 1.3.",
    risk_note: "가격이 목표가에 도달해도 추가 하락 가능성이 있음.",
  },
};

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

  // market/symbols (whitelist code → name map) for the briefing picker
  await page.route(/\/api\/market\/symbols/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(SYMBOLS_MAP),
    }),
  );

  // agents/research (GET) — per-symbol READ-ONLY briefing
  await page.route(/\/api\/agents\/research/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(RESEARCH_RESPONSE),
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

test.describe("Phase 4 — /agents page (종목 전문가 브리핑)", () => {
  test("honest gap banners + briefing section render", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/agents");

    // Primary section heading (CardTitle renders a div, not a heading role)
    await expect(
      page.getByText("종목 전문가 브리핑", { exact: true }),
    ).toBeVisible({ timeout: 10_000 });

    // Honest gap banner with the no-news + manual-trigger notes
    const banner = page.getByTestId("honest-gap-banner");
    await expect(banner).toBeVisible();
    await expect(banner).toContainText("실시간 뉴스 연동은 미구현");
    await expect(banner).toContainText("자동 트리거는 미가동");
  });

  test("리서치 실행 → briefing card with price, fundamental, disclosure, proposal", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/agents");

    await expect(page.getByTestId("run-research-btn")).toBeVisible({ timeout: 10_000 });
    await page.getByTestId("run-research-btn").click();

    // Briefing card appears
    await expect(page.getByTestId("briefing-card")).toBeVisible({ timeout: 10_000 });

    // Current price
    await expect(page.getByTestId("briefing-price")).toContainText("75,000");

    // Fundamental metrics
    await expect(page.getByTestId("fundamental-grid")).toContainText("PER");

    // Disclosure (news-NOT, disclosure-based) + gate clear badge
    await expect(page.getByTestId("disclosures-list")).toContainText("사업보고서 제출");
    await expect(page.getByTestId("disclosure-gate-clear")).toBeVisible();

    // Proposal direction / target
    await expect(page.getByTestId("proposal-side")).toContainText("매수");
    await expect(page.getByTestId("proposal-target")).toContainText("74,250");
  });

  test("\"이 제안으로 조건 만들기\" navigates to /trade with prefill (does not submit)", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/agents");
    await page.getByTestId("run-research-btn").click();
    await expect(page.getByTestId("briefing-card")).toBeVisible({ timeout: 10_000 });

    // Track POST /api/trade/conditions to PROVE no order/condition is created.
    let conditionPosted = false;
    await page.route(/\/api\/trade\/conditions/, (route) => {
      if (route.request().method() === "POST") {
        conditionPosted = true;
      }
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(EMPTY_TABLE),
      });
    });

    await page.getByTestId("make-condition-btn").click();

    // Navigates to /trade with the proposal in the querystring (prefill, not submit)
    await expect(page).toHaveURL(/\/trade\?.*symbol=005930/, { timeout: 10_000 });
    await expect(page).toHaveURL(/side=BUY/);
    await expect(page).toHaveURL(/price=74250/);

    // The OrderForm fields are PREFILLED — but nothing was submitted
    await expect(page.getByLabel("종목 코드")).toHaveValue("005930");
    await expect(page.getByLabel("목표가 (원)")).toHaveValue("74250");
    expect(conditionPosted).toBe(false);
  });

  test("owner sees AI 인사이트 button; clicking returns an AgentMessage", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/agents");
    await page.getByTestId("run-research-btn").click();
    await expect(page.getByTestId("briefing-card")).toBeVisible({ timeout: 10_000 });

    const insight = page.getByTestId("ai-insight");
    await expect(insight).toBeVisible();
    await insight.getByRole("button", { name: "AI 인사이트 요청" }).click();

    await expect(
      page.getByText("삼성전자는 현재 매력적인 밸류에이션에 있습니다."),
    ).toBeVisible({ timeout: 10_000 });
  });

  test("Ask panel: submit question → AgentMessage answer appears", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/agents");

    await expect(page.getByLabel("질문", { exact: true })).toBeVisible({ timeout: 10_000 });
    await page.getByLabel("질문", { exact: true }).fill("삼성전자 전망은?");
    await page.getByRole("button", { name: "질문하기" }).click();

    await expect(
      page.getByText("삼성전자는 현재 매력적인 밸류에이션에 있습니다."),
    ).toBeVisible({ timeout: 10_000 });
  });

  test("IC run: topic submit → EventSource opened → transcript visible without crash", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/agents");

    await expect(page.getByLabel("IC 토픽")).toBeVisible({ timeout: 10_000 });
    await page.getByLabel("IC 토픽").fill("삼성전자 매수 여부");
    await page.getByRole("button", { name: "실행", exact: true }).click();

    await expect(page.getByTestId("ic-transcript")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByRole("button", { name: "실행", exact: true })).toBeDisabled({ timeout: 5_000 });
  });

  test("past decisions list appears", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/agents");

    await expect(page.getByTestId("past-decisions")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText("삼성전자 매수 여부")).toBeVisible();
    await expect(page.getByText("소량 매수 권장")).toBeVisible();
  });

  test("research API error shows visible error (no silent fallback)", async ({ page }) => {
    await mockBackground(page);

    // Override research with error AFTER mockBackground (LIFO priority)
    await page.route(/\/api\/agents\/research/, (route) =>
      route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ detail: "price feed down" }),
      }),
    );

    await loginAsOwner(page);
    await page.goto("/agents");

    await page.getByTestId("run-research-btn").click();

    await expect(
      page.getByRole("alert").filter({ hasText: /리서치 오류/ }),
    ).toBeVisible({ timeout: 10_000 });
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
