import { test, expect, type Page } from "@playwright/test";

// ---------------------------------------------------------------------------
// Shared fixtures
// ---------------------------------------------------------------------------

const GUEST_SESSION = { role: "guest", username: null, data_source: "demo" };
const OWNER_SESSION = { role: "owner", username: "admin", data_source: "live" };

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
const EMPTY_SSO_PROVIDERS = { providers: [] };
const GOOGLE_SSO_PROVIDERS = {
  providers: [
    { id: "google", label: "Google", kind: "oidc", enabled: true },
    { id: "kakao", label: "Kakao", kind: "sns", enabled: false },
  ],
};

/**
 * Mock GET-only background APIs that the post-login pages call.
 * Registered BEFORE the login-specific mock so that the login route
 * (registered after) gets LIFO priority.
 */
async function mockBackgroundApis(
  page: Page,
  session: typeof GUEST_SESSION | typeof OWNER_SESSION,
) {
  // All remaining GET /api/** → empty TableResponse
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

  // Engine status — used by TopStatusBar; registered after catch-all so it wins
  await page.route(/\/api\/engine\/status/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(ENGINE_STATUS),
    }),
  );

  // Auth session check (GET /api/auth/me) — used by home page guard
  await page.route(/\/api\/auth\/me/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(session),
    }),
  );
}

async function mockSsoProviders(page: Page, body = EMPTY_SSO_PROVIDERS) {
  await page.route(/\/api\/auth\/sso\/providers/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(body),
    }),
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

test.describe("Login flow", () => {
  test("guest login — navigates to /home and shows AppShell", async ({
    page,
  }) => {
    // Background API mocks first (lower LIFO priority)
    await mockBackgroundApis(page, GUEST_SESSION);
    await mockSsoProviders(page);

    // Login POST mock last — takes LIFO priority over catch-all
    await page.route(/\/api\/auth\/login/, (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(GUEST_SESSION),
      }),
    );

    await page.goto("/login");

    // Click "게스트 데모 시작" (the guest button)
    await page.getByRole("button", { name: /게스트 데모 시작/ }).click();

    // Should navigate to /home
    await expect(page).toHaveURL(/\/home/, { timeout: 10_000 });

    // AppShell renders a nav element (SidebarNav)
    await expect(page.getByRole("navigation")).toBeVisible();

    // EmptyState is rendered inside AppShell (role=status)
    await expect(page.getByRole("status")).toBeVisible();
  });

  test("local login — fill ID/PW and submit navigates to /home", async ({
    page,
  }) => {
    await mockBackgroundApis(page, OWNER_SESSION);
    await mockSsoProviders(page);

    await page.route(/\/api\/auth\/login/, (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(OWNER_SESSION),
      }),
    );

    await page.goto("/login");

    // Fill credentials
    await page.getByLabel("아이디").fill("admin");
    await page.getByLabel("비밀번호").fill("secret");

    // Submit the form
    await page.getByRole("button", { name: /^로그인$/ }).click();

    // Should reach /home
    await expect(page).toHaveURL(/\/home/, { timeout: 10_000 });

    // AppShell and EmptyState visible
    await expect(page.getByRole("navigation")).toBeVisible();
    await expect(page.getByRole("status")).toBeVisible();
  });

  test("wrong credentials — shows inline error, stays on /login", async ({
    page,
  }) => {
    await mockSsoProviders(page);
    // No background mocks needed — navigation to /home won't happen
    await page.route(/\/api\/auth\/login/, (route) =>
      route.fulfill({
        status: 401,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Invalid credentials" }),
      }),
    );

    await page.goto("/login");

    await page.getByLabel("아이디").fill("bad");
    await page.getByLabel("비밀번호").fill("wrong");
    await page.getByRole("button", { name: /^로그인$/ }).click();

    // Inline error paragraph with role="alert" filtered by text
    // (Next.js also injects a route announcer with role="alert")
    await expect(
      page.getByRole("alert").filter({ hasText: "올바르지 않습니다" }),
    ).toBeVisible({ timeout: 5_000 });

    // URL must stay on /login
    await expect(page).toHaveURL(/\/login/);
  });

  test("configured SSO provider appears as a login button", async ({ page }) => {
    await mockSsoProviders(page, GOOGLE_SSO_PROVIDERS);

    await page.goto("/login");

    const google = page.getByRole("button", { name: "Google로 계속하기" });
    await expect(google).toBeVisible();
    await expect(page.getByRole("button", { name: "Kakao로 계속하기" })).toHaveCount(0);
  });
});
