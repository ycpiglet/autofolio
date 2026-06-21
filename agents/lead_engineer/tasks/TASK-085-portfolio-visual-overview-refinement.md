---
type: task
id: TASK-085
display_id: TASK-085
task_uid: 86efc8f8-779a-4455-95ce-f42ff98d36cf
registered_at: 2026-06-18T22:48:23+09:00
created_at: 2026-06-18T22:48:23+09:00
started_at: 2026-06-18T22:48:23+09:00
updated_at: 2026-06-18T23:16:12+09:00
completed_at: 2026-06-18T22:48:23+09:00
status: 완료
owner: UI/UX Designer
assignees: [UI/UX Designer, Backend Engineer, QA, Doc Steward]
priority: High
difficulty: 중
est_hours: 3
est_tokens: 22000
tags: [portfolio, ui, visualization, api, qa]
gate: Owner direct portfolio UI request; read-only overview API and owner-gated group metadata only; no order/risk/secret/prod mutation
trigger_meeting: Owner direct request 2026-06-18
audit_log: AUDIT-2026-06-18-011
created: 2026-06-18
---

# TASK-085 Portfolio visual overview refinement

작업 ID: TASK-085
상태: 완료
Owner: UI/UX Designer
요청 시각: 2026-06-18T22:48:23+09:00
기록 시각: 2026-06-18T22:48:23+09:00
완료 시각: 2026-06-18T22:48:23+09:00
요청자: Owner
수행자: UI/UX Designer, Backend Engineer, QA, Doc Steward
검토자: UI/UX Designer self-review + Backend Engineer perspective + QA perspective + Doc Steward perspective
협업 waiver: 단일 세션 내 Owner direct UI refinement. 범위가 포트폴리오 탭과 read-only portfolio API이며 실주문, secret, production DB apply는 없음.
의도: 포트폴리오 탭을 사용자 자산 이해에 가장 가치 있는 시각 분석 허브로 재구성하고, 종목명/tooltip/폰트/KPI 전환/API 404 문제를 함께 해결한다.
대상: `web/src/app/portfolio/page.tsx`, `PortfolioDashboard`, `HoldingsTable`, `AllocationChart`, portfolio API, backend holdings metadata, repository group metadata, `docs/UI_SPEC.md`
방법: read-only overview API를 복구하고, Morningstar/Fidelity 포트폴리오 분석 축을 참고해 포트폴리오-local UI를 그래프/노출/집중도/성과 기여 중심으로 재구성한다.
감사 로그: AUDIT-2026-06-18-011
routing_ref: direct-owner-request / TASK-085
selected_model: Codex coding agent
policy_model: AGENTS.md §16 Autofolio R3 Surface; no order/risk/secret/prod DB migration
실측 비용 (시간): 약 2h
실측 비용 (LLM 토큰): unknown

## 원 요청

포트폴리오 탭에서 굵기 기준이 들쭉날쭉하고, 도움말이 사이드바에 잘리며, 자산 추이 차트의 의도가 불명확하고, 숫자 폰트가 보기 좋지 않다. KPI 카드는 클릭 시 하단 주제가 바뀌어야 하며, 첫 화면에는 목표 배분 도넛 등 시각 그래프를 모아야 한다. 실제 금융/포트폴리오 플랫폼 사례를 리서치해 반영한다.

## 범위

포함:

- `/api/portfolio/overview` 읽기 전용 집계 API 복구.
- 포트폴리오 첫 화면을 시각 요약 허브로 재구성.
- KPI 클릭 시 하단 주제 전환.
- 종목명/숫자/키워드 강조 일관화.
- fixed tooltip으로 설명 잘림 방지.
- 자산 추이 카드에 현재값, 기간 변화, 변화율, 고점, 저점 추가.
- 목표 배분 도넛, 자산군 노출, 섹터/지역/전략 노출, 집중도, 성과/손실 기여 리스트 추가.
- 수동 포트폴리오 그룹 저장소 메서드와 Owner+CSRF 그룹 API 연결.
- 대표 보유 종목 기본 별칭과 섹터 메타데이터 보강.

제외:

- 실주문, 자동매매, 리스크 게이트, KIS secret, production DB migration.
- 투자 판단 또는 종목 추천.

## 리서치 반영

- Morningstar X-Ray: Asset Class, World Regions, Stock Style 등 보유 breakdown과 security-level contribution을 핵심 분석 축으로 둠.
- Fidelity Portfolio Analyzer: graphical/holdings views, asset allocation, domestic/foreign stock exposure, industry weightings, historical performance를 제공.
- Fidelity asset allocation guide: 주식/채권/현금의 큰 자산 배분이 장기 성과와 위험에 큰 영향을 준다는 원칙을 확인.

## 완료 내용

- `web/src/app/portfolio/page.tsx`가 기존 단순 KPI/표 화면 대신 `PortfolioDashboard`를 렌더링하도록 교체했다.
- `PortfolioDashboard` 기본 탭을 `요약`으로 바꾸고 첫 화면을 그래프 중심으로 재구성했다.
- `InfoHint`를 viewport fixed tooltip으로 바꿔 사이드바/컨테이너 clipping을 피했다.
- 부분 대문자 강조를 제거해 `SK하이닉스`의 `SK`만 굵게 보이는 문제를 해결했다.
- 숫자 표시를 mono 대신 Pretendard + `tabular-nums`로 통일했다.
- `AllocationChart`가 `목표%`가 아니라 `현재%`를 우선 사용하도록 수정했다.
- `HoldingsTable`의 포트폴리오 전용 강조 props를 실제 구현했다.
- `backend.holdings_df`에 기본 종목 별칭/섹터 메타데이터를 보강해 숫자 종목명 표시를 줄였다.
- `Repository`에 portfolio group / symbol alias JSON-state 저장 메서드를 추가했다.
- `/api/portfolio/groups` POST/PUT/DELETE를 Owner+CSRF gate로 연결했다.
- KIS read-only 잔고/시세 조회가 일시적으로 500을 반환해도 포트폴리오 화면이 500으로 죽지 않도록 `holdings_df()`에 마지막 정상 holdings 캐시/빈 schema fallback을 추가했다.
- `docs/UI_SPEC.md`에 포트폴리오 시각 분석 규칙을 기록했다.
- demo walkthrough mock에 `/api/portfolio/overview` payload를 추가하고 nav strict locator를 보정했다.

## 완료 기록

- 프롬프트 요구사항: 포트폴리오 탭의 inconsistent bold, clipped tooltip, unclear trend graph, numeric font, KPI click behavior, visual first-screen graphs를 리서치 기반으로 개선한다.
- 작업 내용: read-only overview API, symbol metadata, group metadata, portfolio dashboard, holdings emphasis, allocation chart, UI spec, focused tests/E2E를 수정했다.
- 작업 결과: `/portfolio`가 그래프 중심 요약 화면으로 열리고, 종목명/tooltip/폰트/KPI 전환/API 404 회귀가 해소됐다. 로컬 production smoke에서는 3002 프록시를 최신 8002 API로 맞춰 `/api/portfolio/overview` 200을 확인했다.

## 검증

- `.venv\Scripts\python.exe -m pytest tests/unit/test_backend_holdings.py tests/unit/test_backend_kpis.py tests/unit/test_backend_allocation_gap.py tests/unit/test_portfolio_groups.py tests/api/test_portfolio.py -q` -> 50 passed, 1 warning.
- `npm run lint` -> pass.
- `npm run build` -> pass, `/portfolio` generated. 최종 local production build는 `API_INTERNAL_URL=http://127.0.0.1:8002`로 생성.
- `API_INTERNAL_URL=http://127.0.0.1:8002 npm run test:e2e -- e2e/demo-walkthrough.spec.ts --reporter=line` -> 1 passed.
- Local API/web smoke on `http://127.0.0.1:3002/portfolio` -> 200, proxied overview 200, asset-curve 200, `SK하이닉스` 표시, `목표 배분`/`자산군 노출` 표시, KPI 평가손익 click -> 성과 탭 전환, tooltip visible, console errors 0.

## 증거

- `agents/research_agent/notes/EVIDENCE-2026-06-18-009-portfolio-visual-overview-refinement.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-18-009.md`

## 리뷰

- UI/UX Designer: 첫 화면을 KPI 텍스트보다 배분/노출/집중도/성과 기여 중심으로 재구성해 사용자가 자산 상태를 더 빨리 스캔할 수 있게 했다.
- Backend Engineer: `/api/portfolio/overview`는 읽기 전용이며, 수동 그룹 저장은 기존 `system_state` JSON을 사용해 DB migration R3 경계를 넘지 않았다.
- QA: focused pytest, lint, build, demo walkthrough, real browser smoke에서 포트폴리오 로드/tooltip/KPI 전환/종목명 표시를 확인했다.

## Independent Audit

판정: 통과

근거:

- 실주문, 자동매매, risk gate, secret, production DB migration 변경은 없다.
- 신규 group mutation API는 Owner+CSRF gate를 사용한다.
- `/api/portfolio/overview`는 read-only 집계 API이며 404 회귀를 막는 API/E2E mock을 추가했다.
- live KIS read-only 조회가 거래횟수 초과 등으로 실패할 때도 포트폴리오 overview는 cached/empty schema로 degrade한다.
- 포트폴리오 강조/색상은 `PortfolioDashboard`와 opt-in `HoldingsTable` prop 경로로 제한했다.

## 리스크/메모

- 수동 그룹 저장은 새 DB 스키마가 아니라 기존 `system_state` JSON을 사용한다. DB migration R3 경계를 넘지 않았다.
- 기본 종목 별칭은 현재 보유/테스트 basket의 대표 코드 보강이다. 장기적으로는 KIS 상품명 조회 또는 사용자가 관리하는 별칭 테이블을 우선해야 한다.
- Next production rewrites는 build 시점 `API_INTERNAL_URL` 영향을 받는다. 이번 local smoke는 stale 8000 API가 아니라 최신 8002 API를 명시해 재빌드/재시작한 뒤 검증했다.
- 3100 E2E 서버가 stale build를 재사용해 JS/CSS chunk 500을 냈고, 해당 프로세스 종료 후 재실행해 walkthrough가 통과했다.
