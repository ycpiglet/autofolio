---
type: task
id: TASK-174
started_at: 2026-06-21T16:30:12+09:00
completed_at: 2026-06-26T20:57:05+09:00
display_id: TASK-174
task_uid: fdbdc675-6b4b-43a0-97f3-d331439e0b82
registered_at: 2026-06-21T16:30:12+09:00
created_at: 2026-06-21T16:30:12+09:00
updated_at: 2026-06-26T20:57:05+09:00
status: 완료
owner: UI/UX Designer
assignees: [UI/UX Designer, Finance Accounting, Compliance Officer, QA, Beta Tester]
priority: Medium
difficulty: 중
est_hours: 5
est_tokens: 70000
tags: [finance, accounting, portfolio, ui, roadmap]
initiative_id: INIT-FINANCE-ACCOUNTING
task_set_id: TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT
gate: local UI preview only; no recommendation wording, no customer/payment action, no order/risk/prod/deploy
trigger_meeting: Owner direct request 2026-06-21
audit_log: AUDIT-2026-06-21-001
created: 2026-06-21
---

# TASK-174 Finance Roadmap UI Preview

작업 ID: TASK-174
상태: 완료
Owner: UI/UX Designer
요청 시각: 2026-06-21T16:30:12+09:00
기록 시각: 2026-06-21T16:30:12+09:00
완료 시각: 2026-06-26T20:57:05+09:00
요청자: Owner
수행자: UI/UX Designer, Finance Accounting, Compliance Officer, QA, Beta Tester
검토자: Lead Engineer (TASK-REVIEW-APPROVED, 수정 웨이브 후 클린) + Compliance Officer (금지 문구 17개 워딩 테스트 확인)
의도: Finance/accounting planning support를 사용자가 읽을 수 있는 preview로 보여주되,
추천/주문/세무회계 자문 문구를 넣지 않는다.
대상: finance roadmap read model, portfolio UI, roadmap panel
방법: TASK-173 read model을 기반으로 local UI preview와 E2E/wording checks를 만든다.
감사 로그: AUDIT-2026-06-21-001

## 범위

포함:

- plan-vs-expected summary.
- gap matrix.
- timeline candidate list.
- operations support gaps.
- blocked action and review-required labels.

제외:

- buy/sell/rebalance/profit-taking CTA.
- customer payment request.
- public performance claim.
- final tax/accounting/securities advice.
- KIS/order/risk/prod/deploy changes.

## 완료 조건

- [x] UI preview displays scenario and gaps without recommendation wording.
- [-] Mobile/desktop text does not overlap. (반응형 Tailwind 클래스 적용됨: grid-cols-1 sm:/lg:, flex-wrap, 고정폭 없음. 단, E2E 환경 차단(EACCES :3100 샌드박스 이슈)으로 시각적 비중첩 직접 확인 미완료 — 정상 환경 재실행 필요.)
- [x] Compliance wording check passes.
- [-] Focused E2E verifies the panel loads with fixture data. (E2E 스펙 작성 완료·구조 검증됨; 그러나 EACCES :3100 환경 차단으로 실행 불가 — build+vitest(136개) 대체 증거 사용, #123 선례 적용. 정상 환경에서 재실행 필요.)

## 다음

Start after TASK-173 is complete.

## 증거

- `web/src/components/domain/FinanceRoadmapPanel.tsx` — 시나리오/갭 표시 패널, 추천 문구 없음
- `web/src/app/finance-roadmap/page.tsx` — auth-gated 페이지, as_of 프리뷰 레이블 렌더링
- `web/src/lib/api.ts` — TASK-173 read model API seam
- `web/e2e/finance-roadmap.spec.ts` — E2E 스펙 (환경 차단으로 미실행; build+vitest 대체 증거)
- vitest 136/136 PASS (워딩 컴플라이언스 테스트 17 금지 문구 포함)
- verify:format 27/27 PASS
- lint PASS · build PASS
- SidebarNav finance-roadmap 항목 추가 확인

## 완료 내용

- `web/src/components/domain/FinanceRoadmapPanel.tsx` — 시나리오/갭 표시 패널(추천 문구 없음).
- `web/src/app/finance-roadmap/page.tsx` — auth-gated 페이지, as_of 프리뷰 레이블 렌더링.
- `web/src/lib/api.ts` seam 추가.
- 금지 문구 17개 vitest 워딩 테스트. `web/e2e/finance-roadmap.spec.ts` E2E 스펙(환경 차단 미실행).
- SidebarNav finance-roadmap 항목 추가.

결과: vitest 136/136 PASS (워딩 컴플라이언스 17 금지 문구 포함), verify:format 27/27 PASS, lint PASS, build PASS. CC2/CC4 환경 차단(EACCES :3100) → [-] 정직 기록.

## 리뷰

- Lead Engineer: 완료 조건 CC1(추천 문구 없음)/CC3(워딩 컴플라이언스) [x]. CC2(시각적 비중첩) [-] — 반응형 Tailwind 클래스 적용, 시각 미확인(환경 차단). CC4(E2E) [-] — 스펙 작성됨, EACCES :3100 환경 차단으로 미실행(#123 선례). vitest 136 PASS + build PASS. TASK-REVIEW-APPROVED.
- Compliance Officer perspective: 금지 문구 17개 워딩 테스트 통과 확인. buy/sell CTA·payment·tax/accounting advice 없음. as_of 프리뷰 레이블로 데이터 한계 명시.

## 클로즈아웃

완료일: 2026-06-26T20:57:05+09:00

**출시 내용:** `web/src/components/domain/FinanceRoadmapPanel.tsx` — 시나리오/갭 표시 패널(추천 문구 없음). `web/src/app/finance-roadmap/page.tsx` — auth-gated 페이지, as_of 프리뷰 레이블 렌더링. `web/src/lib/api.ts` seam 추가. 금지 문구 17개 vitest 워딩 테스트. `web/e2e/finance-roadmap.spec.ts` E2E 스펙(환경 차단으로 미실행). SidebarNav 항목 추가.

**테스트 증거:** vitest 136개 통과 + verify:format 27개 통과 + 워딩 컴플라이언스 테스트(금지 문구 17개) 통과. CC2(시각적 비중첩) 및 CC4(E2E 실행)는 EACCES :3100 환경 차단으로 미확인 — [-] 정직 마킹.

**리뷰어 판정:** TASK-REVIEW-APPROVED (수정 웨이브 후 클린).
