---
unit_id: UNIT-TASK-065-001
task_id: TASK-065
task_set_id: TASKSET-PRODUCT-MATURITY
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "app/common/logger.py FileHandler → RotatingFileHandler(10MB×5) 교체 + CWD-relative Path('logs') → 절대경로(BASE_DIR/logs). trading_app.log + events.jsonl 모두 적용."
inputs:
  - agents/lead_engineer/tasks/TASK-065-feat-log-rotation.md
  - app/common/logger.py
  - tests/unit/test_structured_logger.py
target_files:
  - app/common/logger.py
  - tests/unit/test_log_rotation.py
  - tests/unit/test_structured_logger.py
scope: "app/common/logger.py의 FileHandler 교체와 경로 절대화만. 로그 포맷/레벨/구조화 동작 변경 금지."
acceptance:
  - "get_logger() → RotatingFileHandler(maxBytes=10485760, backupCount=5)"
  - "get_structured_logger() → events.jsonl도 RotatingFileHandler"
  - "baseFilename이 절대 경로이며 <repo_root>/logs/로 종료"
  - "python -m pytest tests/unit/test_log_rotation.py -v 9 passed"
  - "python -m pytest tests/ -q green"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_log_rotation.py -v"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
handoff: "변경 파일 목록, pytest 결과, BASE_DIR 계산 근거, 수정 전 FAIL → 수정 후 PASS 증거 보고."
stop_condition: "logger.py 수정 + 테스트 통과 후 즉시 중단. 인접 모듈 확장 금지."
depends_on: []
---

# UNIT-TASK-065-001 — 로그 로테이션 + 절대 경로

## Context

`app/common/logger.py`가 `logging.FileHandler`를 사용하여 `trading_app.log`와
`events.jsonl`이 무한 증가 가능. 경로도 `Path("logs")` CWD 상대 경로.

## Target Files

- `app/common/logger.py`
- `tests/unit/test_log_rotation.py`
- `tests/unit/test_structured_logger.py`

## Scope

In scope: `FileHandler` → `RotatingFileHandler` 교체, `Path("logs")` → 절대 경로.

Out of scope: 로그 포맷, 레벨, `_JsonLinesFormatter`, `log_event()` 시그니처.

## BASE_DIR 계산

`logger.py` 위치: `app/common/logger.py`
- `.parents[0]` = `app/common`
- `.parents[1]` = `app`
- `.parents[2]` = `<repo_root>`

`LOG_DIR = Path(__file__).resolve().parents[2] / "logs"`

## 완료 기록

완료 시각: 2026-06-14T17:09:06+09:00
