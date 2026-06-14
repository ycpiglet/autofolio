# TASK-065 Log Rotation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `FileHandler` with `RotatingFileHandler` in `app/common/logger.py` and resolve log paths to an absolute project-root `logs/` directory, eliminating unbounded log growth and CWD-relative path bugs.

**Architecture:** Single-file change in `app/common/logger.py`. `BASE_DIR` is computed from `Path(__file__).resolve().parents[2]` (logger lives at `app/common/logger.py` — two parents up reaches repo root). Both `trading_app.log` and `events.jsonl` get `RotatingFileHandler(maxBytes=10MB, backupCount=5)`. Tests are added to `tests/unit/test_log_rotation.py` (new file). Existing `test_structured_logger.py` is checked for CWD-path dependencies and fixed if needed.

**Tech Stack:** Python stdlib `logging.handlers.RotatingFileHandler`, `pathlib.Path`, `pytest`, `unittest.mock`

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `app/common/logger.py` | Modify | Replace `FileHandler` → `RotatingFileHandler`; derive `LOG_DIR` from `Path(__file__).resolve().parents[2] / "logs"` |
| `tests/unit/test_log_rotation.py` | Create | New TDD tests: assert `RotatingFileHandler` with 10MB/5, assert absolute path ending in `logs/trading_app.log` and `logs/events.jsonl` |
| `tests/unit/test_structured_logger.py` | Possibly modify | Fix any test that creates real `Path("logs")` with CWD assumption |
| `agents/lead_engineer/tasks/TASK-065-feat-log-rotation.md` | Modify | Update frontmatter `status: 대기` → `status: 완료`; body `상태: 대기` → `상태: 완료`; add completion block |
| `agents/lead_engineer/tasks/units/TASK-065/UNIT-TASK-065-001.md` | Create | Unit spec: worker-ready → completed |
| `agents/lead_engineer/tasks/INDEX.md` | Modify | Change `대기` → `완료` for TASK-065 row |

---

## Task 1: Create failing tests for log rotation

**Files:**
- Create: `tests/unit/test_log_rotation.py`

- [ ] **Step 1: Write the failing test file**

```python
# tests/unit/test_log_rotation.py
"""TDD tests for TASK-065: RotatingFileHandler + absolute log path."""
from __future__ import annotations

import logging
import logging.handlers
import importlib
from pathlib import Path


def _reset_logger(name: str) -> None:
    """Clear all handlers and markers from a named logger."""
    log = logging.getLogger(name)
    log.handlers.clear()
    if hasattr(log, "_jsonl_handler"):
        delattr(log, "_jsonl_handler")


class TestGetLoggerUsesRotatingFileHandler:
    def test_file_handler_is_rotating(self, tmp_path):
        """get_logger must attach a RotatingFileHandler, not a plain FileHandler."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.plain")
        logger = lg.get_logger("test.rotation.plain")
        file_handlers = [
            h for h in logger.handlers
            if isinstance(h, logging.FileHandler)
        ]
        assert file_handlers, "No FileHandler-family handler found"
        for h in file_handlers:
            assert isinstance(h, logging.handlers.RotatingFileHandler), (
                f"Expected RotatingFileHandler, got {type(h).__name__}"
            )

    def test_rotating_handler_max_bytes(self, tmp_path):
        """RotatingFileHandler must be configured for 10 MB max."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.maxbytes")
        logger = lg.get_logger("test.rotation.maxbytes")
        rotating = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert rotating, "No RotatingFileHandler attached"
        assert rotating[0].maxBytes == 10 * 1024 * 1024, (
            f"Expected 10485760 bytes, got {rotating[0].maxBytes}"
        )

    def test_rotating_handler_backup_count(self, tmp_path):
        """RotatingFileHandler must keep 5 backup files."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.backup")
        logger = lg.get_logger("test.rotation.backup")
        rotating = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert rotating, "No RotatingFileHandler attached"
        assert rotating[0].backupCount == 5, (
            f"Expected backupCount=5, got {rotating[0].backupCount}"
        )

    def test_log_path_is_absolute(self, tmp_path):
        """The log file path must be absolute (not CWD-relative)."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.abspath")
        logger = lg.get_logger("test.rotation.abspath")
        rotating = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert rotating, "No RotatingFileHandler attached"
        log_path = Path(rotating[0].baseFilename)
        assert log_path.is_absolute(), (
            f"Expected absolute path, got: {log_path}"
        )

    def test_log_path_ends_in_logs_dir(self):
        """Log path must end in <repo_root>/logs/trading_app.log."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.logdir")
        logger = lg.get_logger("test.rotation.logdir")
        rotating = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert rotating, "No RotatingFileHandler attached"
        log_path = Path(rotating[0].baseFilename)
        # The path must end with logs/trading_app.log
        assert log_path.parts[-1] == "trading_app.log", (
            f"Expected filename trading_app.log, got {log_path.parts[-1]}"
        )
        assert log_path.parts[-2] == "logs", (
            f"Expected parent dir 'logs', got {log_path.parts[-2]}"
        )


class TestGetStructuredLoggerUsesRotatingFileHandler:
    def test_jsonl_handler_is_rotating(self):
        """get_structured_logger must attach a RotatingFileHandler for events.jsonl."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.structured")
        logger = lg.get_structured_logger("test.rotation.structured")
        # Find handlers that are RotatingFileHandler and write to events.jsonl
        jsonl_rotating = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
            and "events.jsonl" in getattr(h, "baseFilename", "")
        ]
        assert jsonl_rotating, (
            "No RotatingFileHandler for events.jsonl found. "
            f"Handlers: {[(type(h).__name__, getattr(h, 'baseFilename', '')) for h in logger.handlers]}"
        )

    def test_jsonl_rotating_max_bytes(self):
        """events.jsonl RotatingFileHandler must use 10 MB."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.structured.mb")
        logger = lg.get_structured_logger("test.rotation.structured.mb")
        jsonl_rotating = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
            and "events.jsonl" in getattr(h, "baseFilename", "")
        ]
        assert jsonl_rotating
        assert jsonl_rotating[0].maxBytes == 10 * 1024 * 1024

    def test_jsonl_rotating_backup_count(self):
        """events.jsonl RotatingFileHandler must keep 5 backups."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.structured.bc")
        logger = lg.get_structured_logger("test.rotation.structured.bc")
        jsonl_rotating = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
            and "events.jsonl" in getattr(h, "baseFilename", "")
        ]
        assert jsonl_rotating
        assert jsonl_rotating[0].backupCount == 5

    def test_jsonl_path_is_absolute(self):
        """events.jsonl path must be absolute."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.structured.abs")
        logger = lg.get_structured_logger("test.rotation.structured.abs")
        jsonl_rotating = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
            and "events.jsonl" in getattr(h, "baseFilename", "")
        ]
        assert jsonl_rotating
        assert Path(jsonl_rotating[0].baseFilename).is_absolute()
```

- [ ] **Step 2: Run the test to verify it FAILS on current code**

```
cd C:\Users\ycpig\autofolio
python -m pytest tests/unit/test_log_rotation.py -v
```

Expected: FAIL — `AssertionError: Expected RotatingFileHandler, got FileHandler` (or similar). All 9 tests should fail.

---

## Task 2: Implement log rotation in `app/common/logger.py`

**Files:**
- Modify: `app/common/logger.py`

- [ ] **Step 3: Replace the logger implementation**

Replace the entire contents of `app/common/logger.py` with:

```python
import json
import logging
import logging.handlers
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Project-root absolute log directory
# ---------------------------------------------------------------------------
# logger.py lives at app/common/logger.py  →  .parents[0] = app/common
#                                             .parents[1] = app
#                                             .parents[2] = <repo root>
BASE_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
_BACKUP_COUNT = 5


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "trading_app.log",
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


class _JsonLinesFormatter(logging.Formatter):
    """Formats each log record as a single JSON object on one line."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        # Resolve the rendered message first so exc_info / stack_info are included.
        message = record.getMessage()

        # Collect extra fields: anything that is not a standard LogRecord attribute.
        _STANDARD_ATTRS = {
            "args", "asctime", "created", "exc_info", "exc_text", "filename",
            "funcName", "levelname", "levelno", "lineno", "message", "module",
            "msecs", "msg", "name", "pathname", "process", "processName",
            "relativeCreated", "stack_info", "thread", "threadName",
        }
        extra = {
            k: v
            for k, v in record.__dict__.items()
            if k not in _STANDARD_ATTRS and not k.startswith("_")
        }

        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%f"
            )[:-3] + "Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": message,
        }
        if extra:
            payload["extra"] = extra
        else:
            payload["extra"] = {}

        return json.dumps(payload, ensure_ascii=False, default=str)


def get_structured_logger(name: str) -> logging.Logger:
    """Return a logger that additionally writes JSON Lines to logs/events.jsonl.

    The logger also inherits standard StreamHandler + RotatingFileHandler
    behaviour from get_logger so that human-readable output is preserved.
    """
    # Re-use (or create) the plain-text logger first so we get its handlers.
    logger = get_logger(name)

    # Check whether we already attached a JSON Lines handler to avoid duplicates.
    _JSONL_MARKER = "_jsonl_handler"
    if getattr(logger, _JSONL_MARKER, False):
        return logger

    jsonl_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "events.jsonl",
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    jsonl_handler.setFormatter(_JsonLinesFormatter())
    jsonl_handler.setLevel(logging.INFO)
    logger.addHandler(jsonl_handler)

    # Mark so we don't double-add on repeated calls.
    setattr(logger, _JSONL_MARKER, True)
    return logger


def log_event(logger: logging.Logger, event_type: str, **kwargs: Any) -> None:
    """Emit a structured event as a JSON string through *logger* at INFO level.

    The message written to every handler is:
        {"event": event_type, <kwargs>}

    When the logger has a _JsonLinesFormatter handler attached (i.e. it was
    created with get_structured_logger), the JSON Lines file receives a fully
    structured record with ts / level / logger fields wrapping this payload.
    """
    payload = {"event": event_type, **kwargs}
    logger.info(json.dumps(payload, ensure_ascii=False, default=str))
```

- [ ] **Step 4: Run new rotation tests to verify they pass**

```
cd C:\Users\ycpig\autofolio
python -m pytest tests/unit/test_log_rotation.py -v
```

Expected: 9 passed.

- [ ] **Step 5: Run the existing structured-logger tests**

```
cd C:\Users\ycpig\autofolio
python -m pytest tests/unit/test_structured_logger.py -v
```

Expected: all pass. If `test_jsonl_handler_attached` fails because it calls `Path("logs")` directly (CWD assumption), fix that test to use `lg.LOG_DIR` or `tmp_path` — see Step 6.

- [ ] **Step 6: Fix `test_structured_logger.py` if CWD-relative path breaks it**

The test `test_jsonl_handler_attached` calls `Path("logs").mkdir(exist_ok=True)` and later `real_logs = Path("logs")`. After the change, `logger.py` creates `LOG_DIR` itself (absolute), so the `Path("logs").mkdir()` calls in the test are now redundant but harmless. The only risk is tests that patch `app.common.logger.Path` globally — reload after patching is needed.

Check if the test still passes after Step 5. If it FAILS, replace the fragile mock-patching block in `TestGetStructuredLogger.test_jsonl_handler_attached` with:

```python
def test_jsonl_handler_attached(self):
    """After get_structured_logger the logger must have a RotatingFileHandler
    writing to events.jsonl."""
    import app.common.logger as lg
    _fresh_logger("test.structured.b")
    structured = lg.get_structured_logger("test.structured.b")
    assert getattr(structured, "_jsonl_handler", False) is True
    jsonl_handlers = [
        h for h in structured.handlers
        if isinstance(h, logging.handlers.RotatingFileHandler)
        and "events.jsonl" in getattr(h, "baseFilename", "")
    ]
    assert jsonl_handlers, "No RotatingFileHandler for events.jsonl"
```

Also add `import logging.handlers` at the top of `test_structured_logger.py`.

- [ ] **Step 7: Run the full test suite**

```
cd C:\Users\ycpig\autofolio
python -m pytest tests/ -q
```

Expected: all pass (baseline was 630+ passed). Fix any failure before continuing.

- [ ] **Step 8: Run unit tests only**

```
cd C:\Users\ycpig\autofolio
python -m pytest tests/unit -q
```

Expected: all pass.

- [ ] **Step 9: Commit the implementation**

```
git add app/common/logger.py tests/unit/test_log_rotation.py tests/unit/test_structured_logger.py
git commit -m "feat(ops): 로그 로테이션(RotatingFileHandler) + 절대경로 (TASK-065)

- FileHandler → RotatingFileHandler(maxBytes=10MB, backupCount=5)
- CWD-relative Path('logs') → BASE_DIR / 'logs' (절대경로)
- trading_app.log + events.jsonl 모두 적용
- 신규: tests/unit/test_log_rotation.py (9개 TDD 테스트)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: Create UNIT spec and update task records

**Files:**
- Create: `agents/lead_engineer/tasks/units/TASK-065/UNIT-TASK-065-001.md`
- Modify: `agents/lead_engineer/tasks/TASK-065-feat-log-rotation.md`
- Modify: `agents/lead_engineer/tasks/INDEX.md`

- [ ] **Step 10: Get the current timestamp**

```
cd C:\Users\ycpig\autofolio
python scripts/now.py
```

Copy the output — use it as the completion timestamp in Steps 11 and 12.

- [ ] **Step 11: Create the UNIT spec**

Create directory `agents/lead_engineer/tasks/units/TASK-065/` and write `UNIT-TASK-065-001.md`:

```markdown
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

완료 시각: PLACEHOLDER_TS
```

Replace `PLACEHOLDER_TS` with the actual timestamp from `python scripts/now.py`.

- [ ] **Step 12: Update TASK-065 stub to completed**

Edit `agents/lead_engineer/tasks/TASK-065-feat-log-rotation.md`:

1. In the frontmatter (YAML header), change `status: 대기` → `status: 완료`
2. In the body line `상태: 대기` → `상태: 완료`
3. Add a completion block before the final `## v1 이행` section:

```markdown
## 완료 기록

완료 시각: <timestamp from now.py>
검토자: Backend Engineer / QA

## 증거

- `app/common/logger.py`: `FileHandler` → `RotatingFileHandler(maxBytes=10*1024*1024, backupCount=5)`.
  - `BASE_DIR = Path(__file__).resolve().parents[2]` (app/common/logger.py → app/common → app → repo root).
  - `LOG_DIR = BASE_DIR / "logs"` — 절대 경로, CWD 무관.
  - `trading_app.log` (get_logger) + `events.jsonl` (get_structured_logger) 모두 RotatingFileHandler 적용.
- `tests/unit/test_log_rotation.py` (신규): RotatingFileHandler 타입 검증, maxBytes=10MB, backupCount=5, 절대 경로, logs/ 디렉토리 검증 — 9개 테스트.
- 수정 전: `test_file_handler_is_rotating` FAILED (FileHandler, not RotatingFileHandler).
- 수정 후: 9 passed (test_log_rotation.py), 전체 pytest green.

## 리뷰

- `RotatingFileHandler`는 `FileHandler`의 서브클래스이므로 기존 `isinstance(h, FileHandler)` 검사는 여전히 통과.
- `LOG_DIR.mkdir(parents=True, exist_ok=True)` — 모듈 임포트 시 로그 디렉토리 자동 생성.
- 기존 `_JsonLinesFormatter`, `log_event()`, 로그 포맷/레벨 변경 없음.
```

- [ ] **Step 13: Update INDEX.md**

In `agents/lead_engineer/tasks/INDEX.md`, change the TASK-065 row:

```
| [TASK-065](TASK-065-feat-log-rotation.md) | 대기 | Backend Engineer | feat: 로그 로테이션 + 절대 경로 (ops) → v1 |
```

to:

```
| [TASK-065](TASK-065-feat-log-rotation.md) | 완료 | Backend Engineer | feat: 로그 로테이션 + 절대 경로 (ops) → v1 |
```

---

## Task 4: Regenerate views and build task index, run gates

**Files:**
- Auto-generated: `agents/lead_engineer/tasks/BACKLOG.md`, `VIEW-*.md`, `tasks.index.json`

- [ ] **Step 14: Run generate_views**

```
cd C:\Users\ycpig\autofolio
python scripts/generate_views.py
```

Expected: exits 0, regenerates BACKLOG.md and VIEW-*.md files.

- [ ] **Step 15: Run build_task_index**

```
cd C:\Users\ycpig\autofolio
python scripts/build_task_index.py
```

Expected: exits 0, regenerates `tasks.index.json`.

- [ ] **Step 16: Run check_agent_docs gate**

```
cd C:\Users\ycpig\autofolio
python scripts/check_agent_docs.py
```

Expected: `0 errors`.

- [ ] **Step 17: Run work_schema_gate checks (if available)**

```
cd C:\Users\ycpig\autofolio
python scripts/build_task_index.py --check
python scripts/generate_views.py --check
```

If `--check` flag is not supported, skip. The previous steps (generate + build) confirm correctness.

- [ ] **Step 18: Final full test suite run**

```
cd C:\Users\ycpig\autofolio
python -m pytest tests/ -q
python -m pytest tests/unit -q
```

Expected: all green.

- [ ] **Step 19: Commit records + generated files**

```
git add agents/lead_engineer/tasks/TASK-065-feat-log-rotation.md
git add agents/lead_engineer/tasks/units/TASK-065/UNIT-TASK-065-001.md
git add agents/lead_engineer/tasks/INDEX.md
git add agents/lead_engineer/tasks/BACKLOG.md
git add agents/lead_engineer/tasks/VIEW-by-owner.md
git add agents/lead_engineer/tasks/VIEW-by-priority.md
git add agents/lead_engineer/tasks/VIEW-by-status.md
git add agents/lead_engineer/tasks/VIEW-by-tag.md
git add agents/lead_engineer/tasks/VIEW-by-workload.md
git add tasks.index.json
git commit -m "docs(task): TASK-065 완료 기록 + VIEW/INDEX 재생성"
```

Do NOT add `logs/` files (they are gitignored runtime artifacts).

---

## Self-Review

**Spec coverage check:**

| Requirement | Task |
|-------------|------|
| `RotatingFileHandler` (10MB × 5) for `trading_app.log` | Task 2 Step 3 |
| `RotatingFileHandler` for `events.jsonl` | Task 2 Step 3 |
| Absolute log path via `Path(__file__).resolve().parents[N]` | Task 2 Step 3 |
| Preserve log format/levels/structured-logging | Task 2 Step 3 (unchanged code blocks) |
| Failing test first | Task 1 (run before impl) |
| Don't break existing tests | Task 2 Steps 5-8 |
| Create UNIT-TASK-065-001.md | Task 3 Step 11 |
| TASK-065 stub → 완료 | Task 3 Step 12 |
| INDEX.md → 완료 | Task 3 Step 13 |
| generate_views + build_task_index | Task 4 Steps 14-15 |
| check_agent_docs 0 errors | Task 4 Step 16 |
| Full pytest green | Task 4 Step 18 |
| Commit to feature branch, not main | Implicit — user created branch before starting |

**Placeholder scan:** No TBD/TODO/similar in any code step. All code blocks are complete.

**Type consistency:** `RotatingFileHandler` used consistently throughout. `LOG_DIR` defined once at module level and referenced in both `get_logger` and `get_structured_logger`. `_MAX_BYTES = 10 * 1024 * 1024` and `_BACKUP_COUNT = 5` defined as constants.

**One edge case to watch:** The existing `test_structured_logger.py::TestGetStructuredLogger::test_jsonl_handler_attached` patches `app.common.logger.Path` globally and then calls `reload()`. After our change, `LOG_DIR` is computed at import time — a reload inside the patched context will recompute it. The test's internal `real_logs = Path("logs")` / `real_logs.mkdir(exist_ok=True)` calls after the `with patch` block exit are CWD-relative but now redundant (our module doesn't use them). The test only asserts `getattr(structured, "_jsonl_handler", False) is True`, which is format-agnostic — should still pass. If it doesn't, Step 6 provides the exact fix.
