---
type: task
id: TASK-038
status: 대기
owner: UI/UX Designer
assignees: [UI/UX Designer, Backend Engineer, QA]
priority: High
difficulty: 중
est_hours: 4
est_tokens: 45000
tags: [feature-landscape, watchlist, screener, alerts, ui, read-only]
gate: read-only UI/backend only; no order submission, order modification, broker order path, risk policy, schema migration, or prod mutation
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-13-004
created: 2026-06-13
created_at: 2026-06-13T00:53:23+09:00
updated_at: 2026-06-13T00:53:23+09:00
---

# TASK-038 Watchlist/Screener/Alert Rule Expansion

작업 ID: TASK-038
상태: 대기
Owner: UI/UX Designer
요청 시각: 2026-06-12
기록 시각: 2026-06-13T00:53:23+09:00

## 배경 및 목적

실제 투자 앱과 트레이딩 도구는 저장형 watchlist, screener, price/volume/fundamental/sector
filter, alert rule을 기본 discovery workflow로 제공한다. Autofolio는 이미 현재가, 업종,
재무, 배당, 공시, 호가 데이터가 있으므로 주문 경로를 건드리지 않고도 사용자 가시 가치가
큰 탐색/감시 레이어를 추가할 수 있다.

## 범위

- 포함:
  - saved watchlist/screener 모델 또는 파일 기반 설정.
  - 필터 후보: 가격대, 등락률, 거래량, 업종, PER/PBR/EPS, 배당수익률, 공시 keyword, 보유/미보유.
  - alert rule preview: price threshold, volume spike, disclosure keyword, portfolio weight threshold.
  - `EXTERNAL-APP-API-DECISION-RECORD`의 external channel approval boundary를 future delivery input으로 참조.
  - Streamlit UI에서 목록 생성/수정/삭제, 결과 미리보기, alert dry-run 표시.
  - AppTest/unit test.
- 제외:
  - alert가 자동 주문을 생성하는 기능.
  - 실시간 push delivery 확장.
  - 외부 앱/API token/OAuth/webhook 구현.
  - DB schema migration이 필요한 영구 저장소 변경.
  - KIS order endpoint 또는 `OrderFlow` 변경.

## Done When

1. 저장형 watchlist/screener가 UI에서 생성/수정/삭제 가능하다.
2. 현재 구현된 read-only 데이터로 screener 결과가 계산된다.
3. alert rule은 dry-run/preview 상태만 제공하고 주문 제출 경로가 없다.
4. AppTest와 focused unit test가 통과한다.
5. 기능 한계와 no-order boundary가 TASK/BRIEF에 기록된다.

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-RESEARCH-REPORTING.md`
- Taskset: `agents/project/initiatives/TASKSET-RESEARCH-REPORTING.md`
