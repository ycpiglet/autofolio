---
type: task
id: TASK-032
status: 대기
owner: Data Engineer
assignees: [Data Engineer, QA]
priority: Medium
difficulty: 중
est_hours: 5
est_tokens: 45000
tags: [qa, data-quality, corporate-actions, holiday, stale-data]
gate: no live orders; risk integration requires review
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-12-009
created: 2026-06-12
created_at: 2026-06-12T12:27:28+09:00
updated_at: 2026-06-12T12:27:28+09:00
---

# TASK-032 Data Quality and Corporate Action Tests

작업 ID: TASK-032
상태: 대기
Owner: Data Engineer
기록 시각: 2026-06-12T12:27:28+09:00

## 배경

카탈로그의 stale price, zero/negative/NaN price, missing bar, holiday, split/dividend/corporate action 케이스는 아직 실행 불가능하다.

## 왜 아직 실행 못하는가

- 데이터 freshness/quality contract가 엔진 입력으로 명시되어 있지 않다.
- corporate action adjustment와 holiday calendar가 표준화되어 있지 않다.

## Done When

- data quality validator가 stale/missing/invalid price를 차단하거나 명시적으로 fallback한다.
- holiday/missing-bar/corporate-action mock fixtures가 추가된다.
- no-order behavior가 테스트로 고정된다.

## Verification

- data quality unit tests
- engine no-order tests for invalid market data
