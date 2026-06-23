import { test, expect, type Page } from "@playwright/test";

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
  satisfaction_focus: [] as string[],
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
  version: "investor-profile-v2",
  categories: [
    { key: "goals", title: "투자 목표와 자금", description: "무엇을 위해 투자하는지" },
    { key: "preferences", title: "선호와 만족 기준", description: "어떤 결과에 만족하는지" },
    { key: "agreement", title: "확인과 동의", description: "투자 전 반드시 확인할 사항" },
  ],
  questions: [
    {
      id: "investment_goal",
      title: "투자 목적",
      kind: "single",
      required: true,
      category: "goals",
      description: "가장 가까운 목적을 고르세요.",
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
      category: "preferences",
      options: [
        { value: "plan_adherence", label: "계획 준수" },
        { value: "explainability", label: "이해 가능한 설명" },
        { value: "none", label: "없음", exclusive: true },
      ],
    },
    {
      id: "ack_loss_risk",
      title: "손실 위험 확인",
      kind: "acknowledgement",
      required: true,
      category: "agreement",
      options: [{ value: "acknowledged", label: "원금 손실 가능성을 이해합니다." }],
    },
    {
      id: "ack_not_advice",
      title: "투자자문 아님 확인",
      kind: "acknowledgement",
      required: true,
      category: "agreement",
      options: [{ value: "acknowledged", label: "투자자문이 아님을 이해합니다." }],
    },
    {
      id: "legal_signature",
      title: "전자 서명",
      kind: "signature",
      required: true,
      category: "agreement",
      description: "성명, 확인 문구, 직접 그린 서명이 모두 있어야 저장됩니다.",
      options: [],
    },
  ],
};

async function drawSignature(page: Page) {
  const canvas = page.getByLabel("전자 서명 서명 패드");
  await canvas.scrollIntoViewIfNeeded();
  const box = await canvas.boundingBox();
  expect(box).not.toBeNull();
  if (!box) return;
  await page.mouse.move(box.x + 42, box.y + 96);
  await page.mouse.down();
  await page.mouse.move(box.x + 120, box.y + 56);
  await page.mouse.move(box.x + 220, box.y + 118);
  await page.mouse.move(box.x + 310, box.y + 72);
  await page.mouse.up();
  await expect(page.getByRole("button", { name: "지우기" })).toBeEnabled();
}

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
    const payload = route.request().postDataJSON() as {
      answers: { legal_signature: { confirmation_text: string; signature_data_url: string } };
    };
    expect(payload.answers.legal_signature.confirmation_text).toBe("위 항목을 모두 이해했습니다.");
    expect(payload.answers.legal_signature.signature_data_url).toContain("data:image/png;base64,");
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
  await page.getByLabel("원금 손실 가능성을 이해합니다.").check();
  await page.getByLabel("투자자문이 아님을 이해합니다.").check();
  await page.getByLabel("전자 서명 성명").fill("홍길동");
  await page.getByLabel("확인 문구 입력").fill("위 항목을 모두 이해했습니다.");
  await expect(page.getByText("위 항목을 모두 이해했습니다.", { exact: true })).toBeVisible();
  await drawSignature(page);
  await page.getByRole("button", { name: "진단 저장" }).click();

  const main = page.locator("#main-content");
  await expect(main.getByText("위험중립형", { exact: true })).toBeVisible();
  await expect(main.getByText("L2", { exact: true })).toBeVisible();
});

test("investor profile onboarding blocks save when required answers are missing", async ({
  page,
}) => {
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
      body: JSON.stringify(INCOMPLETE_PROFILE),
    }),
  );
  await page.route(/\/api\/profile\/survey/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(SURVEY),
    }),
  );

  await page.goto("/onboarding/investor-profile");

  await page.getByRole("button", { name: "진단 저장" }).click();

  // The inline validation error surfaces as a role="alert" paragraph naming
  // the first missing question. (Next injects its own empty route-announcer
  // alert, so scope to the one carrying our message text.)
  await expect(page.getByRole("alert").filter({ hasText: "항목을 완료하세요" })).toBeVisible();
  await expect(page.locator('[data-invalid="true"]').first()).toBeVisible();
  await expect(page.locator('[data-invalid="true"]').first()).toHaveClass(/animate-missing-answer/);
  await expect(page).toHaveURL(/\/onboarding\/investor-profile/);
});

test("investor profile onboarding blocks save when confirmation text is wrong", async ({
  page,
}) => {
  let postAttempts = 0;

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
      body: JSON.stringify(INCOMPLETE_PROFILE),
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
    postAttempts += 1;
    await route.fulfill({
      status: 500,
      contentType: "application/json",
      body: JSON.stringify({ detail: "client validation should block this request" }),
    });
  });

  await page.goto("/onboarding/investor-profile");

  await page.getByRole("button", { name: "장기 성장" }).click();
  await page.getByLabel("계획 준수").check();
  await page.getByLabel("원금 손실 가능성을 이해합니다.").check();
  await page.getByLabel("투자자문이 아님을 이해합니다.").check();
  await page.getByLabel("전자 서명 성명").fill("홍길동");
  await page.getByLabel("확인 문구 입력").fill("위 항목을 이해했습니다");
  await expect(page.getByText("위 항목을 모두 이해했습니다.", { exact: true })).toBeVisible();
  await drawSignature(page);
  await page.getByRole("button", { name: "진단 저장" }).click();

  await expect(
    page.getByText("전자 서명: 확인 문구가 정확하지 않습니다. 회색 안내 문구와 동일하게 입력하세요."),
  ).toBeVisible();
  await expect(page.getByText("확인 문구가 정확하지 않습니다. 회색 문구를 그대로 입력하세요.")).toBeVisible();
  await expect(page.locator('[data-invalid="true"]').filter({ hasText: "전자 서명" })).toBeVisible();
  expect(postAttempts).toBe(0);
});
