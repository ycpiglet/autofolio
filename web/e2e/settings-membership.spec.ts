import { test, expect, type Page } from "@playwright/test";

const CSRF_TOKEN = "test-csrf-token-membership";

const OWNER_SESSION = {
  role: "owner",
  username: "alice",
  data_source: "backend",
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

const READINESS = {
  can_launch: false,
  mode: "local_prototype",
  score: 19,
  summary: "로컬 검증회원 플로우는 동작하지만, 외부 사용자/프로덕션 배포 전 R3 게이트가 남아 있습니다.",
  items: [
    {
      id: "local_membership_flow",
      label: "로컬 회원 승인 플로우",
      state: "pass",
      detail: "가입신청부터 app-user gate까지 로컬에서 구현됨.",
      evidence: "TASK-100..TASK-107",
      gate: "R2",
    },
    {
      id: "supabase_schema",
      label: "Supabase production schema",
      state: "block",
      detail: "production schema가 아직 적용되지 않음.",
      evidence: "TASK-087",
      gate: "R3",
    },
    {
      id: "kis_commercial_terms",
      label: "KIS 약관/상용 사용 확인",
      state: "watch",
      detail: "약관/전문가 확인 필요.",
      evidence: "TASK-088",
      gate: "Owner/professional",
    },
  ],
  required_owner_actions: ["Supabase/RLS production schema 승인 및 적용"],
  environment_flags: {
    supabase_url_present: false,
    membership_bank_runtime_config_present: false,
    guest_demo_enabled: false,
    local_auto_register_enabled: false,
  },
};

async function mockSettings(page: Page) {
  await page.route(/\/api\//, (route) => {
    if (route.request().method() === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ columns: [], rows: [] }),
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
      body: JSON.stringify(OWNER_SESSION),
    }),
  );

  await page.route(/\/api\/membership\/readiness/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(READINESS),
    }),
  );

  await page.route(/\/api\/membership\/requests/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ requests: [] }),
    }),
  );
}

test("settings membership tab shows production readiness blockers", async ({ page }) => {
  await mockSettings(page);
  await page.goto("/settings");
  await page.getByRole("tab", { name: "회원 승인" }).click();

  await expect(page.getByText("운영 전환 체크")).toBeVisible();
  await expect(page.getByText("로컬 프로토타입")).toBeVisible();
  await expect(page.getByText("로컬 회원 승인 플로우")).toBeVisible();
  await expect(page.getByText("Supabase production schema")).toBeVisible();
  await expect(page.getByText("KIS 약관/상용 사용 확인")).toBeVisible();
  await expect(page.getByText("접수된 가입 승인 신청이 없습니다.")).toBeVisible();
});
