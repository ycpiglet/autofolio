---
type: task
id: TASK-044
status: 완료
owner: Doc Steward
assignees: [Doc Steward, Research Agent, Lead Engineer, QA]
priority: High
difficulty: 중
est_hours: 2
est_tokens: 30000
tags: [docs, external-api, integrations, owner-manual, setup, secrets]
gate: docs-only; no credentials, live API calls, OAuth app creation, token storage changes, product code, public webhook, external publication, order path, risk policy, schema, secret, or prod mutation
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-13-008
created: 2026-06-13
created_at: 2026-06-13T07:58:00+09:00
updated_at: 2026-06-13T08:06:38+09:00
---

# TASK-044 External API Owner Setup Manual

작업 ID: TASK-044
상태: 완료
Owner: Doc Steward
요청 시각: 2026-06-13
기록 시각: 2026-06-13T07:58:00+09:00

## 배경 및 목적

Owner 요청은 Telegram, Kakao, Google, X, Naver, Discord 등 외부 애플리케이션/API를
사용하려면 Owner가 직접 무엇을 준비해야 하는지, 어떤 계정 가입/API key 발급/검수/설정이
필요한지 자세히 정리한 매뉴얼 파일을 생성하는 것이다.

## 범위

- 포함:
  - Owner 직접 수행 항목과 Agent 수행 가능 항목 구분.
  - Telegram, Discord, Google, Kakao, Naver, X, Notion, Slack, Email/SMTP별 준비물.
  - API key/client secret/token/webhook/OAuth scope/redirect URI/checklist 정리.
  - 이전 `EXTERNAL-APP-API-DECISION-RECORD`와 연결.
- 제외:
  - 실제 외부 계정 생성.
  - API key/token 발급 또는 저장.
  - 외부 API live call.
  - 제품 코드 구현.
  - broker order, risk policy, schema, prod 동작 변경.

## 산출물

- Owner manual:
  - `docs/EXTERNAL_APP_API_OWNER_MANUAL.md`
- Research evidence:
  - `agents/research_agent/notes/EVIDENCE-2026-06-13-007-external-api-owner-setup-manual.md`
- Owner BRIEF:
  - `agents/lead_engineer/reports/BRIEF-2026-06-13-007.md`
- 연결 업데이트:
  - `docs/README.md`
  - `agents/qa/test_cases/EXTERNAL-APP-API-DECISION-RECORD.md`

## 결과

Owner가 앞으로 connector 구현을 승인하기 전에 채울 수 있는 사전 준비 매뉴얼을 생성했다.
매뉴얼은 각 서비스별로 계정/개발자 콘솔/API key/OAuth/검수/요금제/secret 보관/Agent 작업
가능 범위를 구분한다.

## 완료 기록

완료 시각: 2026-06-13T08:06:38+09:00
검토자: Doc Steward + Research Agent + Lead Engineer + QA (Codex self-review)
감사 로그: AUDIT-2026-06-13-008
실측 비용 (시간): 약 0.8h
실측 비용 (LLM 토큰): unknown

- 원 요청: 외부 앱/API 연동 전 Owner 준비물과 직접 수행 항목을 자세히 정리한 매뉴얼 파일을 생성한다.
- 실제 작업:
  - 공식/1차 문서를 다시 확인했다.
  - `TASK-043` decision record와 현재 docs/UI/API 설계를 대조했다.
  - Owner-only work와 Agent-safe work를 분리했다.
  - 서비스별 준비 값과 금지/R3 경계를 매뉴얼에 고정했다.
- 결과:
  - 매뉴얼은 connector implementation 전 preflight checklist 역할을 한다.
  - 실제 secrets, OAuth app, live API, product code, order/risk/prod 경로는 변경하지 않았다.

## 검증

- `python scripts/generate_views.py` -> OK; 51 TASK records reflected in 6 generated views.
- `python scripts/generate_report_views.py` -> OK; 15 reports reflected in 4 generated views.
- `python scripts/generate_views.py --check` -> OK.
- `python scripts/generate_report_views.py --check` -> OK.
- `python scripts/validate_task_schema.py` -> OK.
- `python scripts/check_agent_docs.py` -> OK with 0 errors / 20 existing placeholder-link warnings.
- `python scripts/doc_health_report.py` -> Status G, findings 0.
- `python scripts/check_upstream_issues.py --warn` -> OK; no unreported upstream bug signals.
- `git diff --check` -> OK.
