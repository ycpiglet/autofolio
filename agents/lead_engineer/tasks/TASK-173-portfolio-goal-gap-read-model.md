---
type: task
id: TASK-173
display_id: TASK-173
task_uid: e8120499-841e-40a0-aadd-7887c610a48a
registered_at: 2026-06-21T16:30:12+09:00
created_at: 2026-06-21T16:30:12+09:00
updated_at: 2026-06-26T20:57:05+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, Finance Accounting, Compliance Officer, QA]
priority: Medium
difficulty: 중
est_hours: 5
est_tokens: 70000
tags: [finance, accounting, portfolio, backend, read-model]
initiative_id: INIT-FINANCE-ACCOUNTING
task_set_id: TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT
gate: read-only derived model only; no order path change, no trade recommendation, no private payment data, no KIS/order/risk/prod/deploy
trigger_meeting: Owner direct request 2026-06-21
audit_log: AUDIT-2026-06-21-001
created: 2026-06-21
---

# TASK-173 Portfolio Goal-Gap Read Model

작업 ID: TASK-173
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-21T16:30:12+09:00
기록 시각: 2026-06-21T16:30:12+09:00
완료 시각: 2026-06-26T20:57:05+09:00
요청자: Owner
수행자: Backend Engineer, Finance Accounting, Compliance Officer, QA
검토자: Lead Engineer (TASK-REVIEW-APPROVED, 수정 웨이브 후 클린) + Compliance Officer (no-advice 경계 확인)
의도: TASK-172 fixture와 read-only portfolio/account data를 사용해 planned vs expected,
gap, allocation drift, data-quality, timeline candidate를 계산하는 read model을 만든다.
대상: portfolio read surfaces, finance scenario fixture, future API schema
방법: order/trade/risk path를 건드리지 않고 derived read model과 tests만 추가한다.
감사 로그: AUDIT-2026-06-21-001

## 범위

포함:

- read-only finance roadmap model.
- deterministic calculations from fixture + available portfolio overview fields.
- no-action candidate records with evidence and missing-data fields.
- focused tests for no order path, no advice wording, no private data.

제외:

- actual order placement or order intent creation.
- buy/sell/rebalance/profit-taking instruction.
- portfolio mutation.
- customer payment/receipt/tax action.
- KIS/order/risk/prod/deploy changes.

## 완료 조건

- [x] Read model returns planned/expected/gap/timeline fields.
- [x] Output marks all portfolio changes as Owner-review candidates only.
- [x] Tests prove no order/advice/payment/private-data drift.
- [x] TASK-174 can consume the model in a UI preview.

## 다음

Start after TASK-172 is complete.

## 증거

- `app/services/finance_roadmap.py` — GoalGapResult Pydantic 모델 (planned/expected/gap/timeline 필드), Pydantic Literal 플래그 + 런타임 no-advice 가드 이중 잠금
- `app/api/routers/finance_roadmap.py` — auth-gated `GET /api/finance-roadmap/goal-gap`, as_of="fixture_static" 결정론적
- `app/main.py` — 라우터 등록
- pytest 49/49 PASS — read-only 경계(주문 경로 없음, 어드바이스 문구 없음, 결제/개인정보 없음) + 출력 결정론성 + Owner 후보 전용 플래그 검증
- TASK-174가 이 read model을 API seam을 통해 소비 (검증됨)

## 리뷰

- Lead Engineer: 완료 조건 4개 전부 확인. pytest 49/49 PASS. compliance boundary 이중 잠금(Pydantic Literal + 런타임 가드) 확인. auth gate 확인. TASK-REVIEW-APPROVED.
- Compliance Officer perspective: no-advice/no-order/no-payment/no-private-data 경계 확인 — 출력 필드 모두 read-only derived 값, 투자·세무·법률 자문 문구 없음.

## 클로즈아웃

완료일: 2026-06-26T20:57:05+09:00

**출시 내용:** `app/services/finance_roadmap.py` — GoalGapResult Pydantic 모델(planned/expected/gap/timeline 필드 포함), 준수 경계 이중 잠금(Pydantic Literal 플래그 + 런타임 no-advice 가드). `app/api/routers/finance_roadmap.py` — auth-gated `GET /api/finance-roadmap/goal-gap` 엔드포인트(as_of="fixture_static" 결정론적). main.py에 라우터 등록. TASK-174가 이 read model을 소비.

**테스트 증거:** 49/49 집중 테스트 통과 — read-only 경계(주문 경로 없음, 어드바이스 문구 없음, 결제/개인정보 없음) + 출력 결정론성 + Owner 후보 전용 플래그 검증.

**리뷰어 판정:** TASK-REVIEW-APPROVED (수정 웨이브 후 클린).
