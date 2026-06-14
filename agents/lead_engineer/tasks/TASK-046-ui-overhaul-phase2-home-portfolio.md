---
type: task
id: TASK-046
status: 완료
owner: UI/UX Designer
assignees: [UI/UX Designer, Backend Engineer]
priority: Medium
difficulty: 중
est_hours: 12
est_tokens: 90000
tags: [ui-overhaul, next-js, home, portfolio, phase2]
gate: 선행 TASK-045 완료 전 착수 불가; 착수 전 선행 완료 확인 review 필요; no live orders
trigger_meeting: TASK-045 완료 후 자동 개시
audit_log: AUDIT-2026-06-13-007
created: 2026-06-13
created_at: 2026-06-13T01:33:29+09:00
updated_at: 2026-06-13T01:33:29+09:00
---

# TASK-046 UI 대개편 Phase 2 — 홈 + 포트폴리오 (읽기 화면)

작업 ID: TASK-046
상태: 완료
Owner: UI/UX Designer
기록 시각: 2026-06-13T01:33:29+09:00

## 배경 및 목적

UI 대개편 Phase 2. TASK-045(Phase 1)에서 빈 AppShell이 완성된 상태에서 홈과 포트폴리오 읽기 화면을 구현한다. 데모 스코프 서버 강제 — 폴백 없이 에러는 에러로 표시.

## 작업 범위

### 도메인 컴포넌트

- `KpiCard` — 수익률·평가금액·매입금액·손익
- `PnlText` — `data-pnl` 토글 손익 색상
- `EquityChart` — lightweight-charts 자산곡선
- `ProposalCard` — IC 투자 제안 카드
- `DataTable` — TanStack Table 기반 정렬·필터
- `HoldingsTable` — 보유 종목 전용
- `AllocationChart` — Recharts 파이/Sankey

### 화면

- `/home` — KpiCard(4개), EquityChart, ProposalCard(최신 1건), 지수 배너
- `/portfolio` — HoldingsTable, AllocationChart, KpiCard, 기간 선택

### 백엔드 추가 읽기 엔드포인트

- `market/price`, `market/order-book`, `market/fundamental`
- `market/intraday`, `market/sectors`, `market/disclosures`
- `trade/conditions` GET, `trade/orders/*` 읽기
- `analysis/*` 읽기

## 완료 기준

- `/home`, `/portfolio` Playwright 통과
- 데모 모드에서 목 데이터 렌더 확인
- Streamlit 동일 데이터 스팟체크 통과 (패리티)
- `npm run build` 오류 없음

## 근거 경로

- 디자인 스펙(레포 내 권위 문서): `docs/superpowers/specs/2026-06-13-ui-overhaul-design.md` §Phase 2 (원 플랜은 세션 로컬)

## Done When

- 홈/포트폴리오 화면 데모 모드 정상 렌더
- Playwright `home.spec.ts`, `portfolio.spec.ts` green


## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-UI-OVERHAUL.md`
- Taskset: `agents/project/initiatives/TASKSET-UI-OVERHAUL.md`
- Unit spec: `agents/lead_engineer/tasks/units/TASK-046/UNIT-TASK-046-001.md`

## 완료 기록

완료 시각: 2026-06-15T00:36:09+09:00
검토자: UI/UX Designer + Backend Engineer

## 증거

- **백엔드** (PR #75, merged): Phase2 읽기 엔드포인트 11종(market price·fundamental·order-book·intraday·sectors·disclosures, trade conditions·orders GET, analysis attribution·retro·daily-pnl) — 기존 `app/ui/backend.py` 함수 매핑, READ-ONLY, fail-loud(예외→500), symbol 검증. pytest 917 / app/api 94.9%.
- **프론트** (`web/`): 데이터 컴포넌트 7종(KpiCard·PnlText·DataTable·HoldingsTable·EquityChart[lightweight-charts]·AllocationChart[recharts]·ProposalCard). 홈 대시보드(KPI+자산곡선+지수+보유미리보기+최근체결) + 포트폴리오(HoldingsTable+배분차트+KPI+자산곡선). 차트 client-only(`next/dynamic ssr:false`)로 빌드세이프. **폴백 금지** — fetch 에러는 `role=alert` 가시 표시, 가짜 데이터 없음.
- **E2E**: `web/e2e/dashboard.spec.ts`(홈/포트폴리오 route-mock 렌더) + login 유지. `CI=1 npx playwright test` → 9 passed ×2(비플레이키).
- 검증: pytest 917 passed/coverage 78.8%, npm lint·build 그린, check_agent_docs 0 error.

## 리뷰

- **폴백 금지 준수**(스펙 §Phase2): 모든 데이터 컴포넌트가 fetch 에러 시 가시적 error state. 데모 스코프는 서버가 강제(프론트 무폴백).
- **차트 빌드세이프**: lightweight-charts/recharts는 `"use client"` + `ssr:false` 동적 임포트 + `useEffect` DOM 접근 — SSR/빌드 무파손.
- **prod≠dev 교훈 반영**: Playwright를 프로덕션 모드(`CI=1`)로 2회 검증(Phase1의 Base UI Portal 크래시 재발 방지).
- **안전**: 상태변경/주문 엔드포인트 0건(Phase 3 보류). KIS 키 미노출. 스트랭글러 무변경(app/ui·services·엔진 무수정).
- **한계(정직)**: Playwright는 route-mock(실 백엔드 미기동); 실데이터 패리티 스팟체크는 `run_api.bat`+`run_frontend.bat` 수동. ProposalCard는 읽기 엔드포인트 부재로 EmptyState(데이터 소스는 후속).

## Independent Audit

판정: 통과 — 읽기 화면 실데이터 + 폴백금지 + 프로덕션 E2E 그린. CI(test.yml+frontend.yml) 그린 확인 후 머지.

