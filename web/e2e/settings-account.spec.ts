// web/e2e/settings-account.spec.ts
import { test, expect, type Page } from "@playwright/test";

// ── Fixtures ─────────────────────────────────────────────────────────────────

const CSRF_TOKEN = "test-csrf-token-account";

const OWNER_SESSION = {
  role: "owner",
  username: "alice",
  data_source: "backend",
  csrf_token: CSRF_TOKEN,
};

const GUEST_SESSION = {
  role: "guest",
  username: null,
  data_source: "demo",
  csrf_token: CSRF_TOKEN,
};

const OWNER_ACCOUNT = {
  username: "alice",
  role: "owner",
  data_source: "backend",
  is_owner: true,
};

const GUEST_ACCOUNT = {
  username: null,
  role: "guest",
  data_source: "demo",
  is_owner: false,
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

const INTEGRATIONS_RESPONSE = {
  providers: [
    {
      id: "openai",
      label: "OpenAI",
      kind: "llm",
      auth_type: "api_key",
      secret_label: "API key",
      account_label_hint: "email or project",
      description: "User-owned LLM API key for agent analysis.",
    },
    {
      id: "telegram",
      label: "Telegram",
      kind: "sns",
      auth_type: "bot_token",
      secret_label: "Bot token",
      account_label_hint: "chat id or handle",
      description: "User-owned Telegram destination for notifications.",
    },
  ],
  integrations: [
    {
      provider_id: "openai",
      label: "OpenAI",
      kind: "llm",
      auth_type: "api_key",
      configured: false,
      enabled: false,
      account_label: null,
      scopes: [],
      secret_set: false,
      secret_hint: null,
      created_at: null,
      updated_at: null,
      last_checked_at: null,
      status: "not_configured",
      message: "연동 정보가 없습니다.",
    },
    {
      provider_id: "telegram",
      label: "Telegram",
      kind: "sns",
      auth_type: "bot_token",
      configured: true,
      enabled: true,
      account_label: "owner-chat",
      scopes: ["notification"],
      secret_set: true,
      secret_hint: "****1234",
      created_at: "2026-06-19T15:16:01+09:00",
      updated_at: "2026-06-19T15:16:01+09:00",
      last_checked_at: null,
      status: "configured",
      message: "연동 정보가 저장되었습니다.",
    },
  ],
};

// ── Helpers ───────────────────────────────────────────────────────────────────

async function mockBackground(
  page: Page,
  session: typeof OWNER_SESSION | typeof GUEST_SESSION,
  account: typeof OWNER_ACCOUNT | typeof GUEST_ACCOUNT,
) {
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

  await page.route(/\/api\/engine\/status/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(ENGINE_STATUS),
    }),
  );

  await page.route(/\/api\/auth\/me/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(session),
    }),
  );

  await page.route(/\/api\/account(\?|$)/, (route) => {
    if (route.request().method() === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(account),
      });
    }
    return route.continue();
  });

  await page.route(/\/api\/integrations(\?|$)/, (route) => {
    if (route.request().method() === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(INTEGRATIONS_RESPONSE),
      });
    }
    return route.continue();
  });
}

async function openAccountTab(page: Page) {
  await page.goto("/settings");
  await page.getByRole("tab", { name: "계정/연결" }).click();
}

// ── Tests ─────────────────────────────────────────────────────────────────────

test.describe("Settings — Account tab (owner)", () => {
  test("shows account info and SSO provider status", async ({ page }) => {
    await mockBackground(page, OWNER_SESSION, OWNER_ACCOUNT);
    await openAccountTab(page);

    await expect(page.getByText("계정 정보")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText("alice")).toBeVisible();
    await expect(page.getByText("오너")).toBeVisible();
    await expect(page.getByText("SSO/SNS 로그인")).toBeVisible();
    await expect(
      page.getByText(/활성 provider가 없습니다/),
    ).toBeVisible();
    await expect(page.getByText("사용자 연동")).toBeVisible();
    await expect(page.getByText("owner-chat · ****1234")).toBeVisible();
  });

  test("integration save sends token write-only payload", async ({ page }) => {
    await mockBackground(page, OWNER_SESSION, OWNER_ACCOUNT);

    let capturedBody: Record<string, unknown> | null = null;
    let capturedCsrf = "";
    await page.route(/\/api\/integrations\/openai/, (route) => {
      if (route.request().method() === "PUT") {
        capturedBody = JSON.parse(route.request().postData() ?? "{}");
        capturedCsrf = route.request().headers()["x-csrf-token"] ?? "";
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            provider_id: "openai",
            label: "OpenAI",
            kind: "llm",
            auth_type: "api_key",
            configured: true,
            enabled: true,
            account_label: "owner project",
            scopes: ["analysis"],
            secret_set: true,
            secret_hint: "****alue",
            created_at: "2026-06-19T15:16:01+09:00",
            updated_at: "2026-06-19T15:16:01+09:00",
            last_checked_at: null,
            status: "configured",
            message: "연동 정보가 저장되었습니다.",
          }),
        });
      }
      return route.continue();
    });

    await openAccountTab(page);
    await page.getByLabel("계정 라벨").fill("owner project");
    await page.getByRole("textbox", { name: "API key", exact: true }).fill("sk-test-secret-value");
    await page.getByLabel("Scopes").fill("analysis");

    const resp = page.waitForResponse(/\/api\/integrations\/openai/, { timeout: 10_000 });
    await page.getByRole("button", { name: "연동 저장" }).click();
    await resp;

    await expect(page.getByRole("status").filter({ hasText: "저장되었습니다." })).toBeVisible();
    await expect(page.getByText("sk-test-secret-value")).toHaveCount(0);
    expect(capturedCsrf).toBe(CSRF_TOKEN);
    expect(capturedBody).toEqual({
      secret_value: "sk-test-secret-value",
      account_label: "owner project",
      scopes: ["analysis"],
      enabled: true,
    });
  });

  test("password change success → success status, body has session-derived target", async ({
    page,
  }) => {
    await mockBackground(page, OWNER_SESSION, OWNER_ACCOUNT);

    let capturedBody: Record<string, unknown> | null = null;
    let capturedCsrf = "";
    await page.route(/\/api\/account\/password/, (route) => {
      if (route.request().method() === "POST") {
        capturedBody = JSON.parse(route.request().postData() ?? "{}");
        capturedCsrf = route.request().headers()["x-csrf-token"] ?? "";
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ status: "changed", message: "ok" }),
        });
      }
      return route.continue();
    });

    await openAccountTab(page);

    await page.getByLabel("현재 비밀번호").fill("currentpw1");
    await page.getByLabel("새 비밀번호 (최소 8자)").fill("brandnew99");
    await page.getByLabel("새 비밀번호 확인").fill("brandnew99");

    const resp = page.waitForResponse(/\/api\/account\/password/, { timeout: 10_000 });
    await page.getByRole("button", { name: "비밀번호 변경" }).click();
    await resp;

    await expect(
      page.getByRole("status").filter({ hasText: /비밀번호가 변경/ }),
    ).toBeVisible({ timeout: 5_000 });

    expect(capturedCsrf).toBe(CSRF_TOKEN);
    // Body carries only old/new — username comes from the session server-side.
    expect(capturedBody).toEqual({
      old_password: "currentpw1",
      new_password: "brandnew99",
    });
  });

  test("wrong current password → 401 inline error", async ({ page }) => {
    await mockBackground(page, OWNER_SESSION, OWNER_ACCOUNT);

    await page.route(/\/api\/account\/password/, (route) => {
      if (route.request().method() === "POST") {
        return route.fulfill({
          status: 401,
          contentType: "application/json",
          body: JSON.stringify({ detail: "현재 비밀번호가 일치하지 않습니다." }),
        });
      }
      return route.continue();
    });

    await openAccountTab(page);

    await page.getByLabel("현재 비밀번호").fill("wrongpw12");
    await page.getByLabel("새 비밀번호 (최소 8자)").fill("brandnew99");
    await page.getByLabel("새 비밀번호 확인").fill("brandnew99");
    await page.getByRole("button", { name: "비밀번호 변경" }).click();

    await expect(
      page.getByRole("alert").filter({ hasText: /현재 비밀번호가 일치하지 않습니다/ }),
    ).toBeVisible({ timeout: 5_000 });
  });

  test("mismatched confirmation → client-side error, no request fired", async ({
    page,
  }) => {
    await mockBackground(page, OWNER_SESSION, OWNER_ACCOUNT);

    let fired = false;
    await page.route(/\/api\/account\/password/, (route) => {
      fired = true;
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ status: "changed", message: "ok" }),
      });
    });

    await openAccountTab(page);
    await page.getByLabel("현재 비밀번호").fill("currentpw1");
    await page.getByLabel("새 비밀번호 (최소 8자)").fill("brandnew99");
    await page.getByLabel("새 비밀번호 확인").fill("different9");
    await page.getByRole("button", { name: "비밀번호 변경" }).click();

    await expect(
      page.getByRole("alert").filter({ hasText: /일치하지 않습니다/ }),
    ).toBeVisible({ timeout: 5_000 });
    expect(fired).toBe(false);
  });
});

test.describe("Settings — Account tab (guest)", () => {
  test("guest sees disabled password form with a note", async ({ page }) => {
    await mockBackground(page, GUEST_SESSION, GUEST_ACCOUNT);
    await openAccountTab(page);

    await expect(page.getByText("게스트", { exact: true })).toBeVisible({
      timeout: 10_000,
    });
    await expect(
      page.getByText(/게스트 계정은 비밀번호를 변경할 수 없습니다/),
    ).toBeVisible();

    // The submit button is disabled for guests.
    await expect(
      page.getByRole("button", { name: "비밀번호 변경" }),
    ).toBeDisabled();
  });
});
