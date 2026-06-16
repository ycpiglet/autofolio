import { test, expect } from "@playwright/test";

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

const INCOMPLETE_PROFILE = {
  username: "admin",
  survey_version: "investor-profile-v1",
  completed: false,
  risk_type: "미완료",
  knowledge_level: "미확인",
  scores: {},
  recommended_max_equity_pct: 0,
  recommended_autonomy_level: "L0",
  needs_advanced_survey: false,
  satisfaction_focus: [],
  last_checkin_at: null,
  satisfaction_score: null,
  confidence_score: null,
  stress_score: null,
  updated_at: null,
  completed_at: null,
};

const COMPLETE_PROFILE = {
  ...INCOMPLETE_PROFILE,
  completed: true,
  risk_type: "위험중립형",
  knowledge_level: "기초",
  recommended_max_equity_pct: 60,
  recommended_autonomy_level: "L2",
  satisfaction_focus: ["계획 준수", "이해 가능한 설명"],
};

const SURVEY = {
  version: "investor-profile-v1",
  questions: [
    {
      id: "investment_goal",
      title: "투자 목적",
      kind: "single",
      required: true,
      options: [
        { value: "preserve", label: "원금 보존" },
        { value: "growth", label: "장기 성장" },
      ],
    },
    {
      id: "satisfaction_focus",
      title: "만족 기준",
      kind: "multi",
      required: true,
      options: [
        { value: "plan_adherence", label: "계획 준수" },
        { value: "explainability", label: "이해 가능한 설명" },
      ],
    },
    {
      id: "final_ack",
      title: "최종 확인",
      kind: "acknowledgement",
      required: true,
      options: [{ value: "acknowledged", label: "확인합니다." }],
    },
  ],
};

test("investor profile onboarding saves and renders profile summary", async ({ page }) => {
  let profile = INCOMPLETE_PROFILE;

  await page.route(/\/api\/auth\/me/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ role: "owner", username: "admin", data_source: "backend", csrf_token: "csrf" }),
    }),
  );
  await page.route(/\/api\/engine\/status/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(ENGINE_STATUS),
    }),
  );
  await page.route(/\/api\/profile\/investor/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(profile),
    }),
  );
  await page.route(/\/api\/profile\/survey/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(SURVEY),
    }),
  );
  await page.route(/\/api\/profile\/survey$/, async (route) => {
    if (route.request().method() !== "POST") return route.fallback();
    profile = COMPLETE_PROFILE;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "saved", profile: COMPLETE_PROFILE }),
    });
  });

  await page.goto("/onboarding/investor-profile");

  await page.getByRole("button", { name: "장기 성장" }).click();
  await page.getByLabel("계획 준수").check();
  await page.getByLabel("이해 가능한 설명").check();
  await page.getByLabel("확인합니다.").check();
  await page.getByRole("button", { name: "프로필 저장" }).click();

  const main = page.locator("#main-content");
  await expect(main.getByText("위험중립형", { exact: true })).toBeVisible();
  await expect(main.getByText("L2", { exact: true })).toBeVisible();
});
