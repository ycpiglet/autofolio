---
type: task
id: TASK-043
status: 완료
owner: Research Agent
assignees: [Research Agent, Lead Engineer, QA]
priority: High
difficulty: 중
est_hours: 2
est_tokens: 30000
tags: [research, external-api, integrations, approval-record, capability, backlog]
gate: record-only; no credentials, live API calls, token storage changes, product code, public webhook, OAuth app, external publication, order path, risk policy, schema, secret, or prod mutation
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-13-006
created: 2026-06-13
created_at: 2026-06-13T02:06:53+09:00
updated_at: 2026-06-13T02:15:08+09:00
---

# TASK-043 External App/API Decision Record

작업 ID: TASK-043
상태: 완료
Owner: Research Agent
요청 시각: 2026-06-13
기록 시각: 2026-06-13T02:06:53+09:00

## 배경 및 목적

Owner 요청은 Telegram, Kakao, Google, X, Naver, Discord 등 외부 애플리케이션과
API를 Autofolio에 어떻게 녹일 수 있는지 조사하는 것이다. 문장이 끝에서 끊겼으므로
직전 흐름과 동일하게 리서치 및 승인/기각 기록으로 해석했다.

## 범위

- 포함:
  - 공식/1차 출처 중심의 외부 앱/API 연동 feasibility 조사.
  - 앱별 승인/조건부 승인/보류/R3/기각 matrix 작성.
  - API 권한 class별 capability vocabulary 정의.
  - TASK-038, TASK-040, TASK-041 입력으로 연결.
- 제외:
  - 제품 코드 구현.
  - credentials/OAuth app 생성, token 발급, secret 저장 변경.
  - 외부 API live call.
  - public webhook endpoint 노출.
  - broker order, risk policy, schema, prod 동작 변경.

## 산출물

- Research evidence:
  - `agents/research_agent/notes/EVIDENCE-2026-06-13-006-external-app-api-decision-research.md`
- QA decision record:
  - `agents/qa/test_cases/EXTERNAL-APP-API-DECISION-RECORD.md`
- Owner BRIEF:
  - `agents/lead_engineer/reports/BRIEF-2026-06-13-006.md`
- TASK-038/TASK-041 업데이트:
  - external app/API decision record를 alert/channel/capability 입력으로 연결.

## 결과

Autofolio는 외부 앱/API를 channel adapter와 capability matrix로 흡수할 수 있다.
기본 승인 범위는 outbound notification, read-only command, owner-visible report export다.
OAuth private-data scopes, public posting, inbound webhooks, remote automation enablement,
order/cancel/prod/risk commands는 기본 보류/R3 또는 기각이다.

## 완료 기록

완료 시각: 2026-06-13T02:15:08+09:00
검토자: Research Agent + Lead Engineer + QA (Codex self-review)
감사 로그: AUDIT-2026-06-13-006
실측 비용 (시간): 약 0.5h
실측 비용 (LLM 토큰): unknown

- 원 요청: Telegram, Kakao, Google, X, Naver, Discord 등 외부 앱/API 연동 가능성을 조사한다.
- 실제 작업:
  - Telegram/Kakao/Google/Discord/X/Naver/Notion/Slack 공식 또는 1차 문서를 확인했다.
  - 현재 코드의 Telegram, Discord, Email, Notion, Sheets adapter와 UI placeholder를 대조했다.
  - 앱별 및 capability별 승인/조건부 승인/보류/R3/기각 record를 작성했다.
  - TASK-038/TASK-041에 입력 record로 연결했다.
- 결과:
  - approved path는 outbound alert/report/read-only command 중심이다.
  - OAuth write/private data, public posting, inbound webhook, remote state changes는 R3 hold다.
  - broker order/cancel/prod/risk/secret/money movement 관련 외부 명령은 기본 기각이다.

## 검증

- `python scripts/generate_views.py` -> OK; 42 TASK records reflected in 6 generated views.
- `python scripts/generate_report_views.py` -> OK; 14 reports reflected in 4 generated views.
- `python scripts/generate_views.py --check` -> OK.
- `python scripts/generate_report_views.py --check` -> OK.
- `python scripts/validate_task_schema.py` -> OK.
- `python scripts/check_agent_docs.py` -> OK with 0 errors / 20 existing placeholder-link warnings.
- `python scripts/doc_health_report.py` -> Status G, findings 0.
- `python scripts/check_upstream_issues.py --warn` -> OK; no unreported upstream bug signals.
- `git diff --check` -> OK.
