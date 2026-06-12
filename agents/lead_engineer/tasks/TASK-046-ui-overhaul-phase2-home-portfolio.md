---
type: task
id: TASK-046
status: 대기
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
상태: 대기
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

