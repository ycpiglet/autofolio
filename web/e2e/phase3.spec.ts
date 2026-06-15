// web/e2e/phase3.spec.ts
import { test, expect, type Page } from "@playwright/test";

// ── Fixtures ─────────────────────────────────────────────────────────────────

const CSRF_TOKEN = "test-csrf-token-phase3";

const OWNER_SESSION = {
  role: "owner",
  username: "admin",
  data_source: "live",
  csrf_token: CSRF_TOKEN,
};

const ENGINE_STATUS_OFF = {
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

// ── Helpers ───────────────────────────────────────────────────────────────────

async function mockBackground(page: Page) {
  // Catch-all: GET /api/** → empty table
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
      body: JSON.stringify(ENGINE_STATUS_OFF),
    }),
  );

  // Auth me — includes csrf_token
  await page.route(/\/api\/auth\/me/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(OWNER_SESSION),
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

// ── Tests ─────────────────────────────────────────────────────────────────────

test.describe("Phase 3 — Kill switch gate", () => {
  test("click kill switch → ConfirmModal → confirm → POST fires with X-CSRF-Token", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    let capturedHeaders: Record<string, string> = {};
    let capturedBody: unknown = null;

    await page.route(/\/api\/engine\/kill-switch/, (route) => {
      if (route.request().method() === "POST") {
        capturedHeaders = route.request().headers();
        capturedBody = JSON.parse(route.request().postData() ?? "{}");
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ ok: true }),
        });
      }
      return route.continue();
    });

    const killBtn = page.getByRole("button", { name: /자동매매 중단/ });
    await expect(killBtn).toBeVisible({ timeout: 10_000 });

    await killBtn.click();

    await expect(page.getByRole("dialog")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText(/자동매매를 즉시 중단합니까/)).toBeVisible();

    await page.getByRole("button", { name: "중단" }).click();

    await page.waitForResponse(/\/api\/engine\/kill-switch/, { timeout: 10_000 });

    expect(capturedHeaders["x-csrf-token"]).toBe(CSRF_TOKEN);
    expect(capturedBody).toEqual({ active: true });
  });
});

test.describe("Phase 3 — Auto-trading ON gate", () => {
  test("click auto-trading → ConfirmModal required before POST fires", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    let postFired = false;

    await page.route(/\/api\/engine\/auto-trading/, (route) => {
      if (route.request().method() === "POST") {
        postFired = true;
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ ok: true }),
        });
      }
      return route.continue();
    });

    const toggleBtn = page.getByRole("button", { name: /자동매매 OFF/ });
    await expect(toggleBtn).toBeVisible({ timeout: 10_000 });
    await toggleBtn.click();

    await expect(page.getByRole("dialog")).toBeVisible({ timeout: 5_000 });
    expect(postFired).toBe(false);

    await page.getByRole("button", { name: "활성화" }).click();
    await page.waitForResponse(/\/api\/engine\/auto-trading/, { timeout: 10_000 });

    expect(postFired).toBe(true);
  });
});

test.describe("Phase 3 — Condition CAUTION 2-step", () => {
  test("409 needs_acknowledgement → CAUTION modal → confirm → re-submit with ack_token", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    const VERDICT = "이 종목은 최근 공시가 있습니다. 주의가 필요합니다.";
    const ACK_TOKEN = "ack-token-abc123";

    let callCount = 0;
    let secondBody: unknown = null;

    await page.route(/\/api\/trade\/conditions/, (route) => {
      if (route.request().method() === "POST") {
        callCount++;
        if (callCount === 1) {
          return route.fulfill({
            status: 409,
            contentType: "application/json",
            body: JSON.stringify({
              detail: "needs_acknowledgement",
              verdict: VERDICT,
              ack_token: ACK_TOKEN,
            }),
          });
        }
        secondBody = JSON.parse(route.request().postData() ?? "{}");
        return route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({
            id: 42,
            symbol: "005930",
            side: "BUY",
            target_price: 74000,
            quantity: 10,
            status: "active",
            created_at: "2026-06-15T00:00:00Z",
          }),
        });
      }
      return route.continue();
    });

    await page.goto("/trade");

    await page.getByLabel("종목 코드").fill("005930");
    await page.getByRole("button", { name: "매수", exact: true }).click();
    await page.getByLabel("목표가 (원)").fill("74000");
    await page.getByLabel("수량 (주)").fill("10");
    await page.getByRole("button", { name: "조건 등록" }).click();

    await expect(page.getByRole("dialog")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(VERDICT)).toBeVisible();

    await page.getByRole("button", { name: "확인 후 제출" }).click();

    await page.waitForResponse(/\/api\/trade\/conditions/, { timeout: 10_000 });

    expect(callCount).toBe(2);
    expect((secondBody as Record<string, unknown>).ack_token).toBe(ACK_TOKEN);

    await expect(page.getByRole("status").filter({ hasText: /조건이 등록/ })).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("Phase 3 — run-once 409", () => {
  test("POST run-once 409 → '이미 실행 중' message appears", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.route(/\/api\/engine\/run-once/, (route) => {
      if (route.request().method() === "POST") {
        return route.fulfill({
          status: 409,
          contentType: "application/json",
          body: JSON.stringify({ detail: "already running" }),
        });
      }
      return route.continue();
    });

    await page.goto("/trade");

    await page.getByRole("button", { name: "엔진 1회 실행" }).click();

    await expect(page.getByRole("status").filter({ hasText: "이미 실행 중" })).toBeVisible({
      timeout: 10_000,
    });
  });
});
