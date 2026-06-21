---
type: task
id: TASK-083
display_id: TASK-083
task_uid: 6e0675a0-a171-4621-8d84-aa0ce30e139c
registered_at: 2026-06-18T19:18:46+09:00
created_at: 2026-06-18T19:18:46+09:00
started_at: 2026-06-18T19:18:46+09:00
updated_at: 2026-06-18T19:18:46+09:00
completed_at: 2026-06-18T19:18:46+09:00
status: 완료
owner: Lead Engineer
assignees: [Lead Engineer, Backend Engineer, UI/UX Designer, QA, Doc Steward]
priority: High
difficulty: 상
est_hours: 4
est_tokens: 35000
tags: [portfolio, ui, api, analytics, kis, qa]
gate: Owner direct implementation request; no live order, no secret, no production DB apply
trigger_meeting: Owner direct request 2026-06-18
audit_log: AUDIT-2026-06-18-009
created: 2026-06-18
---

# TASK-083 Portfolio diagnosis hub rebuild

작업 ID: TASK-083
상태: 완료
Owner: Lead Engineer
요청 시각: 2026-06-18T19:18:46+09:00
기록 시각: 2026-06-18T19:18:46+09:00
완료 시각: 2026-06-18T19:18:46+09:00
요청자: Owner
수행자: Lead Engineer, Backend Engineer, UI/UX Designer, QA, Doc Steward
검토자: Lead Engineer self-review + QA perspective
협업 waiver: 단일 세션 내 Owner direct implementation. 실주문, secret 변경, production DB migration apply, external deploy는 하지 않았다.
의도: 포트폴리오 탭을 사용자가 자산 상태와 문제를 빠르게 이해하는 핵심 화면으로 재구성한다.
대상: KIS position name/valuation parsing, portfolio overview API, portfolio group metadata, Next portfolio dashboard, API/unit/E2E tests, UI spec
방법: 현재 보유 데이터의 품질을 개선하고, KPI/진단/보유/그룹/성과를 한 화면의 탭형 분석 허브로 구성한다.
감사 로그: AUDIT-2026-06-18-009
routing_ref: direct-owner-request / TASK-083
selected_model: Codex coding agent
policy_model: AGENTS.md §16 Autofolio R3 Surface; no order/risk weakening
실측 비용 (시간): 약 2.5h
실측 비용 (LLM 토큰): unknown

## 범위

포함:

- KIS 잔고의 `prdt_name`, 평가금액, 평가손익, 수익률 필드 보존.
- 포트폴리오 KPI 확장: 총자산, 총평가금액, 현금, 일간손익, 일간수익률, 월간수익률, 평가손익, 현금비중, 보유종목수.
- `/api/portfolio/overview`와 portfolio group CRUD API.
- 종목 alias/group 저장용 DB 테이블.
- 포트폴리오 화면을 진단, 보유, 그룹, 성과 탭으로 재구성.
- 문서/테스트/E2E 모킹 갱신.

제외:

- 실제 주문, 자동매매 ON, risk gate 완화.
- KIS credential, account, secret 변경.
- production DB migration apply 또는 외부 배포.

## 완료 조건

- [x] 포트폴리오 상단 KPI가 빈 값이 아니라 API 기반 값으로 표시된다.
- [x] KIS가 제공하는 종목명이 숫자 티커보다 우선 표시된다.
- [x] 사용자가 자산군/지역/섹터/전략/위험/수동 그룹 단위로 포트폴리오를 볼 수 있다.
- [x] 데이터 품질, 집중도, 상위 기여/부진 종목이 화면에서 보인다.
- [x] 그룹 생성/수정/삭제 API는 Owner+CSRF gate를 유지한다.
- [x] focused backend tests, web lint/build, Playwright walkthrough가 통과한다.

## 완료 내용

수행:

- `Position` 모델과 KIS `get_positions()`가 종목명·평가금액·평가손익·수익률 raw 값을 보존하도록 확장했다.
- `app/services/backend.py`에 `portfolio_overview()`와 진단/그룹/집중도/품질/성과 보조 로직을 추가했다.
- `portfolio_symbol_aliases`, `portfolio_groups`, `portfolio_group_members` 스키마와 repository 메서드를 추가했다.
- `app/api/routers/portfolio.py`에 overview와 group CRUD endpoint를 추가했다.
- `web/src/components/domain/PortfolioDashboard.tsx`와 `/portfolio` 페이지를 새 분석 허브로 교체했다.
- `web/playwright.config.ts`에 `E2E_PORT`를 지원해 오래된 테스트 서버 재사용 충돌을 피할 수 있게 했다.
- `docs/UI_SPEC.md`의 포트폴리오 사양을 KPI/진단/그룹/성과 중심으로 갱신했다.

결과:

- 포트폴리오 탭은 총자산/손익/현금/보유수/월간수익률 KPI와 데이터 진단을 먼저 보여준다.
- 보유 테이블은 KIS 종목명 또는 alias를 우선 사용하므로 숫자 티커 단독 표시가 줄었다.
- 수동 그룹은 API로 저장할 수 있고, 자동 그룹은 자산군/지역/섹터/전략/위험 기준으로 제공된다.
- 성과 탭은 기존 자산곡선/목표배분 차트와 상위 기여·부진 종목을 함께 보여준다.

## 완료 기록

- 프롬프트 요구사항: 포트폴리오 상단 KPI 공백, 숫자 종목명, 포트폴리오 그룹/분석 효용 부족을 개선한다.
- 작업 내용: KIS position parsing, portfolio overview/group API, DB group metadata, Next dashboard, tests, UI spec, TASK/EVIDENCE/BRIEF 기록을 갱신했다.
- 작업 결과: 포트폴리오 화면과 API가 KPI/진단/보유/그룹/성과를 제공하고 검증 명령이 통과했다.

## 검증

- `.venv\Scripts\python.exe -m py_compile app\brokers\base.py app\brokers\kis\kis_client.py app\database\repositories.py app\services\backend.py app\services\portfolio.py app\api\routers\portfolio.py app\api\schemas\__init__.py` -> pass.
- `.venv\Scripts\python.exe -m pytest tests\unit\test_backend_holdings.py tests\unit\test_backend_kpis.py tests\unit\test_kis_client.py tests\unit\test_portfolio_groups.py tests\unit\test_services_shim.py tests\api\test_portfolio.py tests\api\test_gate.py -q` -> 91 passed.
- `.venv\Scripts\python.exe -m pytest tests\api\test_analysis.py tests\unit\test_perf_report.py tests\unit\test_backend_allocation_gap.py -q` -> 62 passed.
- `npm run lint` -> pass.
- `npm run build` -> pass, `/portfolio` route generated.
- `$env:E2E_PORT='3101'; npm run test:e2e -- e2e/demo-walkthrough.spec.ts --reporter=line` -> 1 passed.
- Local production smoke: API `http://127.0.0.1:8002/api/health` 200, web `http://127.0.0.1:3002/portfolio` 200, proxied `/api/portfolio/overview` 200.
- Browser smoke on `http://127.0.0.1:3002/portfolio` -> `포트폴리오`, `총자산`, `진단`, `수동 그룹` visible.

## 증거

- `agents/research_agent/notes/EVIDENCE-2026-06-18-007-portfolio-diagnosis-hub-rebuild.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-18-007.md`

## 리뷰

- Lead Engineer: R3 주문 표면은 변경하지 않았고, 포트폴리오 조회/분석/API/화면 개선으로 범위를 제한했다.
- QA: API/unit regression, web lint/build, Playwright walkthrough를 통과했다.
- Doc Steward: UI spec과 task/evidence/brief 기록을 갱신했다.

## Independent Audit

판정: 통과

근거:

- 실주문, secret 변경, production DB migration apply, external deploy는 수행하지 않았다.
- Owner-only group mutation은 기존 session+CSRF gate를 사용한다.
- 종목명 보강은 KIS raw name과 metadata alias를 우선하되, 누락 시 데이터 품질 진단으로 드러난다.
- E2E 포트 충돌은 `E2E_PORT`로 분리해 기존 로컬 서버를 건드리지 않고 검증했다.
