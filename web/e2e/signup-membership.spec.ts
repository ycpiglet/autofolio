import { test, expect } from "@playwright/test";

const REQUESTED = {
  request_id: "mrq_test123",
  status: "requested",
  display_name: "홍길동",
  contact: "tester@example.com",
  plan: "pilot_monthly",
  price_krw: 20000,
  requested_at: "2026-06-19T15:00:00+09:00",
  updated_at: "2026-06-19T15:00:00+09:00",
  verified_at: null,
  activated_at: null,
  grant_expires_at: null,
  deposit_instruction: null,
  account_grant: null,
  subscription_grant: null,
  events: [],
  message: "가입 승인 신청이 접수되었습니다.",
};

const DEPOSIT_PENDING = {
  ...REQUESTED,
  status: "deposit_pending",
  updated_at: "2026-06-19T15:10:00+09:00",
  verified_at: "2026-06-19T15:10:00+09:00",
  deposit_instruction: {
    price_krw: 20000,
    currency: "KRW",
    deposit_code: "AF-123ABC",
    bank_name: "테스트은행",
    account_holder: "Autofolio",
    account_number: "000-0000-0000",
    account_configured: true,
    due_at: "2026-06-22T15:10:00+09:00",
  },
  message: "입금 확인 대기 상태입니다.",
};

test("signup page lets applicant check deposit instructions with request id and contact", async ({ page }) => {
  await page.route(/\/api\/membership\/requests$/, async (route) => {
    if (route.request().method() !== "POST") return route.continue();
    return route.fulfill({
      status: 201,
      contentType: "application/json",
      body: JSON.stringify(REQUESTED),
    });
  });

  await page.route(/\/api\/membership\/requests\/status$/, async (route) => {
    if (route.request().method() !== "POST") return route.continue();
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(DEPOSIT_PENDING),
    });
  });

  await page.goto("/signup");

  await page.getByLabel("이름 또는 별칭").fill("홍길동");
  await page.getByLabel("연락처").first().fill("tester@example.com");
  await page.getByRole("button", { name: "가입 승인 신청" }).click();

  await expect(page.getByText("mrq_test123")).toBeVisible();
  await expect(page.getByText("신청 접수").first()).toBeVisible();

  await page.getByRole("button", { name: "상태 확인" }).click();

  await expect(page.getByText("입금 확인 대기", { exact: true })).toBeVisible();
  await expect(page.getByText("20,000원")).toBeVisible();
  await expect(page.getByText("AF-123ABC")).toBeVisible();
  await expect(page.getByText("테스트은행")).toBeVisible();
  await expect(page.getByText("Autofolio", { exact: true })).toBeVisible();
  await expect(page.getByText("000-0000-0000")).toBeVisible();
});
