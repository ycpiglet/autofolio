---
type: task
id: TASK-027
status: 보류
owner: KIS API Engineer
assignees: [KIS API Engineer, QA, Compliance Officer]
priority: Low
difficulty: 상
est_hours: 10
est_tokens: 80000
tags: [kis, qa, derivatives, futures, options, fx-futures]
gate: Owner approval required; derivatives order routing and risk policy are R3 surfaces
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-12-009
created: 2026-06-12
created_at: 2026-06-12T12:27:28+09:00
updated_at: 2026-06-12T12:27:28+09:00
---

# TASK-027 KRX Derivatives Test Support

작업 ID: TASK-027
상태: 보류
Owner: KIS API Engineer
기록 시각: 2026-06-12T12:27:28+09:00

## 배경

카탈로그의 선물, 옵션, FX futures 케이스는 현재 실행 불가능하다. Autofolio의 현 주문 모델은 국내 현금주식형 `LIMIT`/`MARKET`만 지원한다.

## 왜 아직 실행 못하는가

- 선물/옵션/FX futures 전용 계좌, 증거금, 만기, 승수, Greeks/행사가/월물, risk model이 없다.
- 주문 경로와 위험 정책을 추가해야 하므로 R3 surface다.

## Done When

- derivatives symbol model과 contract metadata가 정의된다.
- mock-only 주문/리스크 테스트가 먼저 추가된다.
- paper/live 경로는 Owner 승인 전까지 비활성 유지된다.

## Verification

- derivatives mock matrix pytest
- margin/risk rejection tests
- no-prod guard test
