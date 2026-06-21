---
type: task
id: TASK-084
display_id: TASK-084
task_uid: ca678629-167b-49f3-8183-65c2dc99287e
registered_at: 2026-06-18T21:53:43+09:00
created_at: 2026-06-18T21:53:43+09:00
started_at: 2026-06-18T21:53:43+09:00
updated_at: 2026-06-18T21:53:43+09:00
completed_at: 2026-06-18T21:53:43+09:00
status: 완료
owner: UI/UX Designer
assignees: [UI/UX Designer, Lead Engineer, QA, Doc Steward]
priority: High
difficulty: 중
est_hours: 2
est_tokens: 18000
tags: [portfolio, ui, readability, interaction, qa]
gate: Owner direct implementation request; portfolio tab only, no order/risk/secret mutation
trigger_meeting: Owner direct request 2026-06-18
audit_log: AUDIT-2026-06-18-010
created: 2026-06-18
---

# TASK-084 Portfolio readability and interaction polish

작업 ID: TASK-084
상태: 완료
Owner: UI/UX Designer
요청 시각: 2026-06-18T21:53:43+09:00
기록 시각: 2026-06-18T21:53:43+09:00
완료 시각: 2026-06-18T21:53:43+09:00
요청자: Owner
수행자: UI/UX Designer, Lead Engineer, QA, Doc Steward
검토자: Lead Engineer self-review + QA perspective
협업 waiver: 단일 세션 내 Owner direct UI polish. 범위가 포트폴리오 탭 UI이며 실주문, secret, production DB apply는 없음.
의도: 포트폴리오 탭의 숫자, 종목, 손익, 섹션 의미를 더 직관적으로 읽히게 만든다.
대상: `PortfolioDashboard`, `HoldingsTable` opt-in emphasis, `docs/UI_SPEC.md`, browser/E2E verification
방법: 포트폴리오 전용 강조/색상/도움말/정렬 UI를 추가하고 공용 테이블 영향은 opt-in prop으로 제한한다.
감사 로그: AUDIT-2026-06-18-010
routing_ref: direct-owner-request / TASK-084
selected_model: Codex coding agent
policy_model: AGENTS.md §16 Autofolio R3 Surface; no order/risk/secret mutation
실측 비용 (시간): 약 1.5h
실측 비용 (LLM 토큰): unknown

## 범위

포함:

- 포트폴리오 전용 손익 색상: `+` 파랑, `-` 빨강.
- KPI 카드 클릭 상세 breakdown.
- 섹션 제목 옆 `?` 도움말 hover/focus tooltip.
- 숫자, 종목명, 티커, 금액, 비율 굵게 강조.
- 보유 테이블 숫자 글꼴 통일.
- 기여 상위/손실 기여 메일형 리스트, 정렬, 전체 보기.

제외:

- 다른 탭의 화면 구조 변경.
- KIS 주문, 리스크 게이트, secret, production DB migration.

## 완료 조건

- [x] 포트폴리오 KPI 카드가 클릭 가능하고 상세 정보가 보인다.
- [x] 도움말 아이콘 hover 시 지표 설명이 보인다.
- [x] 포트폴리오 손익은 `+` 파랑, `-` 빨강으로 표시된다.
- [x] 평가금액/평가손익 등 숫자 컬럼은 같은 고정폭 글꼴로 표시된다.
- [x] 기여 리스트는 정렬과 전체 보기 동작을 제공한다.
- [x] 기존 데모 워크스루가 깨지지 않는다.

## 완료 내용

수행:

- `PortfolioDashboard`에 포트폴리오 전용 KPI 카드, 상세 패널, `InfoHint`, `SectionHeading`, `TopMovers` 리스트를 구현했다.
- `HoldingsTable`은 `emphasizeValues`와 `pnlClassName` prop을 추가해 포트폴리오에서만 강조/색상 규칙을 켤 수 있게 했다.
- `docs/UI_SPEC.md`에 포트폴리오 가독성/상호작용 규칙을 추가했다.

결과:

- 상단 KPI는 클릭하면 총자산/평가손익/일간손익/현금/보유종목/월간수익률 상세 값을 보여준다.
- 자산 추이, 목표 배분, 진단, 데이터 품질 등 주요 제목 옆 `?`에 설명 tooltip이 붙었다.
- 기여 상위/손실 기여는 손익·수익률·비중·종목 기준 정렬과 전체 보기 버튼을 제공한다.

## 완료 기록

- 프롬프트 요구사항: 포트폴리오 탭 한정으로 굵은 숫자/종목, `+` 파랑/`-` 빨강, 큰 제목, hover 도움말, 정렬/더보기, KPI 클릭, 글꼴 통일을 구현한다.
- 작업 내용: `PortfolioDashboard`, `HoldingsTable`, `docs/UI_SPEC.md`를 수정했다.
- 작업 결과: 포트폴리오 탭의 가독성과 상호작용이 개선됐고 검증 명령이 통과했다.

## 검증

- `npm run lint` -> pass.
- `npm run build` -> pass, `/portfolio` route generated.
- Local browser smoke on `http://127.0.0.1:3002/portfolio` -> KPI detail, help tooltip, holdings tab, performance movers pass.
- `$env:E2E_PORT='3101'; npm run test:e2e -- e2e/demo-walkthrough.spec.ts --reporter=line` -> 1 passed.

## 증거

- `agents/research_agent/notes/EVIDENCE-2026-06-18-008-portfolio-readability-interaction-polish.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-18-008.md`

## 리뷰

- UI/UX Designer: 포트폴리오 탭의 읽기 위계와 직접 조작 가능성을 개선했다.
- Lead Engineer: 공용 `HoldingsTable` 변경은 opt-in prop으로 제한해 다른 탭 영향 범위를 줄였다.
- QA: lint/build/browser smoke/demo walkthrough가 통과했다.

## Independent Audit

판정: 통과

근거:

- 실주문, secret, production DB apply, risk gate 변경은 없다.
- 포트폴리오 전용 손익 색상은 `PortfolioDashboard` prop 경로로 적용된다.
- 공용 보유 테이블의 새 강조 포맷은 `emphasizeValues`를 켠 경우에만 활성화된다.
- 기존 8개 화면 E2E 워크스루가 통과했다.
