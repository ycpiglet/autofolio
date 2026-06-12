---
type: task
id: TASK-037
status: 완료
owner: Research Agent
assignees: [Research Agent, Lead Engineer, QA]
priority: High
difficulty: 중
est_hours: 2
est_tokens: 30000
tags: [research, feature-landscape, backlog, planning]
gate: record-only; no product code, live broker, order path, risk policy, schema, secret, or prod mutation
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-13-004
created: 2026-06-13
created_at: 2026-06-13T00:53:23+09:00
updated_at: 2026-06-13T00:53:23+09:00
---

# TASK-037 Feature Landscape Research

작업 ID: TASK-037
상태: 완료
Owner: Research Agent
요청 시각: 2026-06-12
기록 시각: 2026-06-13T00:53:23+09:00

## 배경 및 목적

Owner 요청은 실제 증권앱, 사이트, 거래소, 퀀트 트레이딩 플랫폼, 툴들이 어떤 기능을
제공하는지 조사하고 Autofolio에 반영할 만한 것과 잠재 후보를 구분해 기록하는 것이다.

## 범위

- 포함:
  - 공식/1차 문서 기반 기능군 조사.
  - Autofolio 현재 구현/검증 기록과 feature gap 매핑.
  - 반영 가능한 R1/R2 후속 TASK 등록.
  - R3/잠재 후보를 기존 보류 TASK에 중복 없이 매핑.
- 제외:
  - 제품 코드 구현.
  - KIS 주문 경로, `OrderFlow`, `app/risk/**`, DB schema/migration 변경.
  - prod 실전 주문 또는 prod safety policy 변경.

## 산출물

- Research evidence:
  - `agents/research_agent/notes/EVIDENCE-2026-06-13-004-feature-landscape-research.md`
- QA catalog:
  - `agents/qa/test_cases/FEATURE-LANDSCAPE-CATALOG.md`
- Owner BRIEF:
  - `agents/lead_engineer/reports/BRIEF-2026-06-13-004.md`
- 신규 후속 TASK:
  - `TASK-038` watchlist/screener/alert rule expansion.
  - `TASK-039` backtest/research report hardening.
  - `TASK-040` portfolio performance/tax-lot style reporting.
  - `TASK-041` broker capability/feature parity matrix.

## 결과

기능적으로 남은 영역은 있다. 다만 즉시 반영할 영역은 주문/리스크가 아니라
읽기전용 discovery, backtest/research reporting, portfolio reporting, capability matrix다.
고위험 주문/브로커/시장구조 확장은 기존 R3 보류 TASK에 유지한다.

## 완료 기록

완료 시각: 2026-06-13T00:53:23+09:00
검토자: Research Agent + Lead Engineer + QA (Codex self-review)
감사 로그: AUDIT-2026-06-13-004
실측 비용 (시간): 약 0.5h
실측 비용 (LLM 토큰): unknown

- 원 요청: 실제 증권앱, 사이트, 거래소, 퀀트 트레이딩 플랫폼, 툴의 기능을 조사하고 반영 후보와 잠재 후보를 구분해 기록한다.
- 실제 작업:
  - 공식/1차 출처 중심으로 feature family를 정리했다.
  - `FEATURE-LANDSCAPE-CATALOG`를 만들고 QA catalog index에 등록했다.
  - 즉시 반영 가능한 R1/R2 후속 TASK-038~041을 생성했다.
  - 고위험 후보는 기존 R3 보류 TASK에 매핑해 중복 task 생성을 피했다.
- 결과:
  - 연구 evidence와 Owner BRIEF가 생성됐다.
  - 제품 코드, KIS order path, risk policy, schema, prod 동작은 변경하지 않았다.

## 검증

- `python scripts/generate_views.py` -> generated 6 task views and `tasks.index.json`.
- `python scripts/generate_report_views.py` -> 12 reports indexed into 4 views.
- `python scripts/generate_views.py --check` -> OK.
- `python scripts/generate_report_views.py --check` -> OK.
- `python scripts/validate_task_schema.py` -> OK.
- `python scripts/check_agent_docs.py` -> OK, 0 errors; existing placeholder-link warnings only.
- `python scripts/doc_health_report.py` -> Status G, findings 0.
- `python scripts/check_upstream_issues.py --warn` -> OK.
- `python scripts/backlog_sweep.py` -> ACT 4 / ASK 9.
- `git diff --check` -> OK.
