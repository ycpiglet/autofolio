import { test, expect, type Page } from "@playwright/test";

// ---------------------------------------------------------------------------
// Shared fixtures
// ---------------------------------------------------------------------------

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

type SsoProvider = { id: string; label: string; kind: string; enabled: boolean };
type SsoProvidersBody = { providers: SsoProvider[] };

const EMPTY_SSO_PROVIDERS: SsoProvidersBody = { providers: [] };
const GOOGLE_SSO_PROVIDERS: SsoProvidersBody = {
  providers: [
    { id: "google", label: "Google", kind: "oidc", enabled: true },
    { id: "kakao", label: "Kakao", kind: "sns", enabled: false },
  ],
};
const MOCK_SSO_PROVIDERS: SsoProvidersBody = {
  providers: [
    { id: "mock", label: "Mock SSO", kind: "mock", enabled: true },
    { id: "google", label: "Google", kind: "oidc", enabled: false },
  ],
};

/**
 * Mock GET-only background APIs that the post-login pages call.
 * Registered BEFORE the login-specific mock so that the login route
 * (registered after) gets LIFO priority.
 */
async function mockBackgroundApis(
  page: Page,
  session: typeof OWNER_SESSION,
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

async function mockSsoProviders(page: Page, body: SsoProvidersBody = EMPTY_SSO_PROVIDERS) {
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
  test("guest demo is not offered on the default login screen", async ({
    page,
  }) => {
    await mockSsoProviders(page);

    await page.goto("/login");

    await expect(page.getByRole("button", { name: /게스트 데모 시작/ })).toHaveCount(0);
    await expect(page.getByRole("button", { name: /가입 승인 신청/ })).toBeVisible();
    await expect(page.getByText(/Owner가 신청자와 입금 확인을 검증/)).toBeVisible();
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
        body: JSON.stringify({ detail: "아이디 또는 비밀번호가 올바르지 않습니다." }),
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
    const kakao = page.getByRole("button", { name: /Kakao로 계속하기/ });
    await expect(kakao).toBeVisible();
    await kakao.click();
    await expect(page.getByRole("dialog", { name: "Kakao 로그인 연동 설정" })).toBeVisible();
  });

  test("enabled mock SSO provider appears as a login button", async ({ page }) => {
    await mockSsoProviders(page, MOCK_SSO_PROVIDERS);

    await page.goto("/login");

    await expect(page.getByRole("button", { name: /Mock SSO.*개발용/ })).toBeVisible();
    await expect(page.getByRole("button", { name: /Google로 계속하기/ })).toBeVisible();
  });
});
