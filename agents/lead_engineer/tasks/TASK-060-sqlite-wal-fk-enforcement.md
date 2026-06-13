---
type: task
id: TASK-060
status: 대기
owner: Backend Engineer
assignees: [Backend Engineer, QA]
priority: Medium
difficulty: 중
est_hours: 3
est_tokens: 20000
tags: [database, performance, integrity, sqlite]
gate: -
trigger_meeting: 다음 사이클
audit_log: AUDIT-2026-06-14-001
created: 2026-06-14
created_at: 2026-06-14T00:00:00+09:00
updated_at: 2026-06-14T00:00:00+09:00
---

# TASK-060 fix: SQLite WAL 모드 및 FK 미적용 (repositories.py)

작업 ID: TASK-060
상태: 대기
Owner: Backend Engineer
요청 시각: 2026-06-14
기록 시각: 2026-06-14T00:00:00+09:00
요청자: Owner
수행자: Backend Engineer
의도: repositories.py에 WAL 모드와 외래키 제약 활성화
대상: app/database/repositories.py initialize_database(), app/database/schema.sql
방법: initialize_database()에 PRAGMA WAL/FK 추가 + schema.sql FK 선언 검증 + 기존 pytest 전체 green 확인
감사 로그: AUDIT-2026-06-14-001

## 버그 내용

`app/database/repositories.py`의 `initialize_database()`에 WAL 모드(`PRAGMA journal_mode=WAL`)와 외래키 적용(`PRAGMA foreign_keys=ON`)이 없음.

**증상**:
- 동시 읽기/쓰기 경합 발생 가능 (라이브 모드에서 엔진 + UI 동시 DB 접근 시)
- FK orphan 레코드 삽입 가능 (예: 존재하지 않는 order_id 참조하는 execution_log)

**원인**: SQLite 기본값은 DELETE journal mode이며 FK 비활성 상태.

## 수정 방향

1. `initialize_database()` 또는 커넥션 초기화 시점에 추가:
   ```sql
   PRAGMA journal_mode=WAL;
   PRAGMA foreign_keys=ON;
   ```
2. `schema.sql` FK 선언 추가 또는 검증 (execution_logs → order_logs 등)
3. 기존 pytest 전체 green 확인 (WAL 적용이 기존 테스트에 영향 없음 검증)

## 완료 기준

- WAL 모드 적용
- FK 제약 활성화
- 기존 pytest 전체 green

## Done When

- WAL 모드 적용
- FK 제약 활성화
- 기존 pytest 전체 green
