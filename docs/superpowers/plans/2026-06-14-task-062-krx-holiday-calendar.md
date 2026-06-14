# KRX Holiday Calendar Safety Check Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add KRX holiday detection to SafetyChecker so order attempts on public market holidays are blocked with a clear deny reason, eliminating false consecutive-failure triggers on holidays.

**Architecture:** Create a static `app/data/krx_holidays.py` module with `KRX_HOLIDAYS: set[str]` (ISO dates "YYYY-MM-DD") and an `is_krx_holiday(date)` helper. Inject the check into `SafetyChecker.check()` immediately after the trading-window check, using KST date from the `now` argument already passed. Tests monkeypatch `is_krx_holiday` for full determinism.

**Tech Stack:** Python 3.11+, pytest + monkeypatch, existing `app/risk/safety_checker.py`, `app/risk/trading_window.py`

---

### Task 1: Create the KRX holiday data module with failing test

**Files:**
- Create: `app/data/krx_holidays.py`
- Create: `tests/unit/test_krx_holidays.py`

- [ ] **Step 1: Write the failing test first**

Create `tests/unit/test_krx_holidays.py`:

```python
"""KRX 휴장일 캘린더 단위 테스트."""
from __future__ import annotations

from datetime import date

import pytest

from app.data.krx_holidays import KRX_HOLIDAYS, is_krx_holiday


# ---- data sanity ----

def test_krx_holidays_is_a_set_of_iso_strings():
    """KRX_HOLIDAYS is a set of YYYY-MM-DD strings."""
    assert isinstance(KRX_HOLIDAYS, (set, frozenset))
    for item in KRX_HOLIDAYS:
        assert isinstance(item, str)
        # Must be parseable as ISO date
        date.fromisoformat(item)


def test_krx_holidays_contains_2026_new_year():
    """2026-01-01 (신정) is in the holiday list."""
    assert "2026-01-01" in KRX_HOLIDAYS


def test_krx_holidays_contains_2025_new_year():
    """2025-01-01 (신정) is in the holiday list."""
    assert "2025-01-01" in KRX_HOLIDAYS


def test_krx_holidays_contains_seollal_2026():
    """2026 설날 (2026-01-28/29/30) included."""
    assert "2026-01-28" in KRX_HOLIDAYS
    assert "2026-01-29" in KRX_HOLIDAYS
    assert "2026-01-30" in KRX_HOLIDAYS


def test_krx_holidays_contains_christmas_2026():
    """2026-12-25 (성탄절) in holiday list."""
    assert "2026-12-25" in KRX_HOLIDAYS


# ---- is_krx_holiday helper ----

def test_is_krx_holiday_new_year_2026():
    """2026-01-01 is a KRX holiday."""
    assert is_krx_holiday(date(2026, 1, 1)) is True


def test_is_krx_holiday_known_trading_day():
    """2026-06-10 (Wednesday, not a holiday) is NOT a KRX holiday."""
    assert is_krx_holiday(date(2026, 6, 10)) is False


def test_is_krx_holiday_accepts_string():
    """is_krx_holiday also works with a date-string argument."""
    assert is_krx_holiday("2026-01-01") is True
    assert is_krx_holiday("2026-06-10") is False
```

- [ ] **Step 2: Run the test to verify it fails (module does not exist yet)**

```
cd C:\Users\ycpig\autofolio
python -m pytest tests/unit/test_krx_holidays.py -q 2>&1 | head -20
```

Expected: `ModuleNotFoundError` or `ImportError` — `app.data.krx_holidays` does not exist.

- [ ] **Step 3: Create `app/data/krx_holidays.py`**

```python
"""KRX 공식 휴장일 정적 캘린더.

한국거래소(KRX) 공식 휴장일 목록 — 2025·2026년.
출처: KRX 공식 공고 + 관공서 공휴일 규정.
이 목록은 연초에 KRX가 발표하는 공식 휴장일 공고를 반영한다.
대체공휴일(代替公休日)은 공휴일법에 따라 계산되며, 불확실한 일부 항목은
주석으로 표기한다. 매년 갱신 필요.
"""
from __future__ import annotations

from datetime import date as _date
from typing import Union

# ---------------------------------------------------------------------------
# 2025 KRX 휴장일
# ---------------------------------------------------------------------------
_2025: set[str] = {
    "2025-01-01",  # 신정
    "2025-01-28",  # 설날 연휴 전날
    "2025-01-29",  # 설날
    "2025-01-30",  # 설날 다음날
    "2025-03-01",  # 삼일절
    "2025-05-05",  # 어린이날
    "2025-05-06",  # 어린이날 대체공휴일 (2025-05-05가 월요일)
    "2025-05-12",  # 부처님오신날 (음력 4/8; 2025년 양력 5/12)
    "2025-06-06",  # 현충일
    "2025-08-15",  # 광복절
    "2025-10-03",  # 개천절
    "2025-10-06",  # 추석 연휴 전날
    "2025-10-07",  # 추석
    "2025-10-08",  # 추석 다음날
    "2025-10-09",  # 한글날
    "2025-12-25",  # 성탄절
    "2025-12-31",  # KRX 연말 휴장
}

# ---------------------------------------------------------------------------
# 2026 KRX 휴장일
# ---------------------------------------------------------------------------
_2026: set[str] = {
    "2026-01-01",  # 신정
    "2026-01-28",  # 설날 연휴 전날
    "2026-01-29",  # 설날 (음력 1/1; 2026년 양력 1/29)
    "2026-01-30",  # 설날 다음날
    "2026-03-01",  # 삼일절
    "2026-05-05",  # 어린이날
    "2026-05-24",  # 부처님오신날 (음력 4/8; 2026년 양력 5/24)
    "2026-06-06",  # 현충일
    "2026-08-15",  # 광복절
    "2026-08-17",  # 광복절 대체공휴일 (2026-08-15 토요일)
    "2026-09-24",  # 추석 연휴 전날
    "2026-09-25",  # 추석
    "2026-09-26",  # 추석 다음날
    "2026-10-03",  # 개천절
    "2026-10-09",  # 한글날
    "2026-12-25",  # 성탄절
    "2026-12-31",  # KRX 연말 휴장
}

# ---------------------------------------------------------------------------
# 통합 세트 (공개 API)
# ---------------------------------------------------------------------------
KRX_HOLIDAYS: frozenset[str] = frozenset(_2025 | _2026)


def is_krx_holiday(d: Union[_date, str]) -> bool:
    """KST 날짜가 KRX 휴장일인지 확인한다.

    Args:
        d: datetime.date 또는 "YYYY-MM-DD" 문자열

    Returns:
        True이면 KRX 휴장일(주문 차단), False이면 정규 거래일.
    """
    if isinstance(d, str):
        key = d
    else:
        key = d.strftime("%Y-%m-%d")
    return key in KRX_HOLIDAYS
```

- [ ] **Step 4: Run the holiday module tests to verify they pass**

```
python -m pytest tests/unit/test_krx_holidays.py -v
```

Expected: All 9 tests PASS.

- [ ] **Step 5: Commit the holiday data module**

```
git add app/data/krx_holidays.py tests/unit/test_krx_holidays.py
git commit -m "feat(data): KRX 공식 휴장일 캘린더 2025-2026 (TASK-062 step-1)"
```

---

### Task 2: Add holiday gate to SafetyChecker with failing test first

**Files:**
- Modify: `app/risk/safety_checker.py`
- Modify: `tests/unit/test_safety_checker.py`

- [ ] **Step 1: Write the failing test for holiday blocking**

Add these two tests to `tests/unit/test_safety_checker.py`. They must FAIL before the safety_checker change:

```python
# ---- KRX 휴장일 차단 ----

def test_krx_holiday_blocks_order(env, monkeypatch):
    """KRX 휴장일에는 SafetyChecker가 주문을 차단한다."""
    repo, checker = env
    import app.risk.safety_checker as sc_mod
    # 거래창 패치: 통과시킨다 (holiday gate만 테스트)
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    # holiday check를 날짜 인자 없이 True로 패치 (결정론적)
    monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: True)
    r = checker.check(condition=_cond(), current_price=70000, now=datetime.now())
    assert not r.allowed
    assert "휴장" in r.reason or "holiday" in r.reason.lower() or "krx" in r.reason.lower()


def test_non_holiday_does_not_block(env, monkeypatch):
    """KRX 휴장일이 아닌 날에는 holiday 사유로 차단하지 않는다."""
    repo, checker = env
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)
    r = checker.check(condition=_cond(), current_price=70000, now=datetime.now())
    assert r.allowed, r.reason
```

- [ ] **Step 2: Run the test to confirm FAIL (safety_checker doesn't import is_krx_holiday yet)**

```
python -m pytest tests/unit/test_safety_checker.py::test_krx_holiday_blocks_order -v
```

Expected: FAIL with `AttributeError` or the order is allowed (no holiday check).

- [ ] **Step 3: Add the KRX holiday check to `app/risk/safety_checker.py`**

At the top of the file, add the import after existing imports:

```python
from app.data.krx_holidays import is_krx_holiday
```

Then in `SafetyChecker.check()`, immediately after the `is_within_trading_window` block (line ~93-98), add the holiday check:

```python
        # --- KRX 휴장일 차단 ---
        if is_krx_holiday(now.date()):
            return SafetyResult(False, "KRX 휴장일 — 오늘은 KRX 휴장일입니다.")
```

The full updated block in context looks like:

```python
        if not is_within_trading_window(
            now,
            settings.default_trading_start,
            settings.default_trading_end,
        ):
            return SafetyResult(False, "Outside trading window.")

        # --- KRX 휴장일 차단 ---
        if is_krx_holiday(now.date()):
            return SafetyResult(False, "KRX 휴장일 — 오늘은 KRX 휴장일입니다.")

        if not is_condition_executable(
```

- [ ] **Step 4: Run the holiday safety tests to verify they pass**

```
python -m pytest tests/unit/test_safety_checker.py -v
```

Expected: All tests PASS including the two new holiday tests.

- [ ] **Step 5: Check if today (2026-06-14) is in KRX_HOLIDAYS — guard other tests**

2026-06-14 is a Sunday but NOT a KRX holiday (현충일 is 2026-06-06). Run full suite:

```
python -m pytest tests/ -q
```

Expected: ALL green. If any test breaks because `is_krx_holiday` now blocks (because today IS in the list), we need to also monkeypatch `is_krx_holiday` in those tests. Check each broken test and add:
```python
monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)
```

- [ ] **Step 6: Commit the safety checker update**

```
git add app/risk/safety_checker.py tests/unit/test_safety_checker.py
git commit -m "feat(safety): KRX 휴장일 SafetyChecker 차단 게이트 (TASK-062 step-2)"
```

---

### Task 3: Run full verification and update records

**Files:**
- Create: `agents/lead_engineer/tasks/units/TASK-062/UNIT-TASK-062-001.md`
- Modify: `agents/lead_engineer/tasks/TASK-062-feat-krx-holiday-calendar.md`
- Modify: `agents/lead_engineer/tasks/INDEX.md`

- [ ] **Step 1: Run full pytest suite**

```
python -m pytest tests/ -q
python -m pytest tests/unit -q
```

Record pass counts. Both must be fully green.

- [ ] **Step 2: Run doc and schema gates**

```
python scripts/check_agent_docs.py
python scripts/build_task_index.py --check
python scripts/generate_views.py --check
```

All must report 0 errors / OK.

- [ ] **Step 3: Create the unit spec**

Create `agents/lead_engineer/tasks/units/TASK-062/UNIT-TASK-062-001.md`:

```markdown
---
unit_id: UNIT-TASK-062-001
task_id: TASK-062
task_set_id: TASKSET-PRODUCT-MATURITY
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "SafetyChecker.check()가 KRX 공휴일·휴장일 캘린더를 검사하지 않아 공휴일에 주문 시도 → consecutive_failure 카운터 증가 → 서킷브레이커 오발동 위험. app/data/krx_holidays.py 작성 + SafetyChecker.check()에 휴장일 거부 게이트 추가."
inputs:
  - agents/lead_engineer/tasks/TASK-062-feat-krx-holiday-calendar.md
  - app/risk/safety_checker.py
  - app/risk/trading_window.py
target_files:
  - app/data/krx_holidays.py
  - app/risk/safety_checker.py
  - tests/unit/test_krx_holidays.py
  - tests/unit/test_safety_checker.py
scope: "app/data/krx_holidays.py 신규 작성. app/risk/safety_checker.py에 is_krx_holiday 호출 추가 (deny-only). 다른 risk/engine 로직 변경 금지. 주문 기능 추가 금지."
acceptance:
  - "KRX 휴장일에 SafetyChecker.check() → allowed=False, reason 포함 '휴장' or 'holiday' or 'KRX'"
  - "평일(비휴장일)에 SafetyChecker.check() → holiday 사유로 차단하지 않음"
  - "is_krx_holiday(date(2026,1,1)) == True (신정)"
  - "is_krx_holiday(date(2026,6,10)) == False (평일)"
  - "python -m pytest tests/ -q 전체 그린"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_krx_holidays.py -v"
  - "python -m pytest tests/unit/test_safety_checker.py -v"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
handoff: "변경 파일 목록, pytest 결과 (unit + full), 오늘이 휴장일인지 여부 + 타 테스트 영향 분석, KST 처리 방식, 실패 테스트 선행 증거."
stop_condition: "is_krx_holiday 추가 후 즉시 중단. 거래창 로직, TradingWindow, 다른 risk 모듈로 확장 금지."
depends_on: []
---

# UNIT-TASK-062-001 — KRX 휴장일 캘린더 SafetyChecker 연동

## Context

`SafetyChecker.check()`(`app/risk/safety_checker.py`)가 KRX 공휴일·휴장일을 검사하지 않아
공휴일에 주문 시도 → KIS API 거부 → `consecutive_failure` 카운터 증가 → 서킷브레이커 오발동 위험.

## Target Files

- `app/data/krx_holidays.py` (신규)
- `app/risk/safety_checker.py` (수정: import + holiday gate)
- `tests/unit/test_krx_holidays.py` (신규)
- `tests/unit/test_safety_checker.py` (수정: 2개 테스트 추가)

## Scope

In scope: `app/data/krx_holidays.py` 작성, `SafetyChecker.check()`에 deny-only 휴장일 게이트 추가.

Out of scope: `TradingWindow.is_open()` 수정, 주문 기능, UI 코드, 다른 risk 모듈.

## Steps

1. `tests/unit/test_krx_holidays.py` 작성 → FAIL 확인
2. `app/data/krx_holidays.py` 작성 → 테스트 PASS 확인
3. `tests/unit/test_safety_checker.py`에 `test_krx_holiday_blocks_order`, `test_non_holiday_does_not_block` 추가 → FAIL 확인
4. `app/risk/safety_checker.py`에 `is_krx_holiday` 임포트 + 게이트 추가 → 테스트 PASS 확인
5. 전체 suite (`tests/`) 그린 확인 (run-date 독립성 보장)

## Acceptance Criteria

- KRX 휴장일에 SafetyChecker.check() → allowed=False, reason 포함 '휴장' or 'holiday' or 'KRX'
- 평일에 holiday 사유로 차단 없음
- is_krx_holiday(date(2026,1,1)) True, is_krx_holiday(date(2026,6,10)) False
- `python -m pytest tests/ -q` 전체 그린
- `python scripts/check_agent_docs.py` 0 error

## Verification

```
python -m pytest tests/unit/test_krx_holidays.py -v
python -m pytest tests/unit/test_safety_checker.py -v
python -m pytest tests/ -q
python scripts/check_agent_docs.py
```

## Handoff

변경 파일 목록, pytest pass counts (unit + full), 오늘 휴장일 여부 + 타 테스트 영향,
KST 처리 방식, 실패 테스트 선행 증거, 커밋 SHA.

## Stop Boundary

`is_krx_holiday` 추가 후 즉시 중단. TradingWindow, 다른 risk 모듈로 확장 금지.
```

- [ ] **Step 4: Update TASK-062 frontmatter and body**

Update `agents/lead_engineer/tasks/TASK-062-feat-krx-holiday-calendar.md`:
- frontmatter `status:` → `완료`
- body `상태:` → `완료`
- Add completion block (see template from TASK-063)

- [ ] **Step 5: Update INDEX.md — TASK-062 status to 완료**

Change the INDEX.md row:
```
| [TASK-062](TASK-062-feat-krx-holiday-calendar.md) | 완료 | Backend Engineer | feat: KRX 휴장일 캘린더 연동 (safety) → v1 |
```

- [ ] **Step 6: Regenerate views and task index**

```
python scripts/generate_views.py
python scripts/build_task_index.py
```

- [ ] **Step 7: Run all gate checks**

```
python scripts/check_agent_docs.py
python scripts/build_task_index.py --check
python scripts/generate_views.py --check
```

All 0 errors.

- [ ] **Step 8: Final full pytest run**

```
python -m pytest tests/ -q
python -m pytest tests/unit -q
```

Record final counts.

- [ ] **Step 9: Commit everything**

```
git add app/data/krx_holidays.py app/risk/safety_checker.py \
    tests/unit/test_krx_holidays.py tests/unit/test_safety_checker.py \
    agents/lead_engineer/tasks/TASK-062-feat-krx-holiday-calendar.md \
    agents/lead_engineer/tasks/units/TASK-062/UNIT-TASK-062-001.md \
    agents/lead_engineer/tasks/INDEX.md \
    agents/lead_engineer/tasks/BACKLOG.md \
    agents/lead_engineer/tasks/VIEW-by-owner.md \
    agents/lead_engineer/tasks/VIEW-by-priority.md \
    agents/lead_engineer/tasks/VIEW-by-status.md \
    agents/lead_engineer/tasks/VIEW-by-tag.md \
    agents/lead_engineer/tasks/VIEW-by-workload.md \
    tasks.index.json
```

Commit message:
```
feat(safety): KRX 휴장일 캘린더 검사 — 공휴일 주문 차단 (TASK-062)

- app/data/krx_holidays.py: KRX_HOLIDAYS frozenset (2025-2026) + is_krx_holiday()
- app/risk/safety_checker.py: holiday gate deny (KST date from now arg)
- tests/unit/test_krx_holidays.py: 9개 단위테스트 (TDD, 실패 선행)
- tests/unit/test_safety_checker.py: test_krx_holiday_blocks_order, test_non_holiday_does_not_block 추가
- 모든 테스트에서 monkeypatch로 날짜 고정 — run-date 독립 결정론적

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
```

---

## Self-Review

**Spec coverage:**
- KRX holiday list 2025+2026: Task 1 Step 3 ✓
- is_krx_holiday helper: Task 1 Step 3 ✓
- SafetyChecker.check() holiday deny: Task 2 Step 3 ✓
- KST date (now.date() from the KST-aware now arg): Task 2 Step 3 ✓
- Deny-only (no order capability added): Task 2 Step 3 ✓, enforced by scope in Task 3
- TDD (failing test first): Task 1 Step 1-2, Task 2 Step 1-2 ✓
- Deterministic (monkeypatch, not wall-clock): Task 2 Step 1 ✓
- Today (2026-06-14) holiday check: 현충일은 2026-06-06; 2026-06-14 NOT in KRX_HOLIDAYS → other tests unaffected ✓
- UNIT record: Task 3 Step 3 ✓
- TASK-062 completion block: Task 3 Step 4 ✓
- INDEX.md updated: Task 3 Step 5 ✓
- generate_views + build_task_index: Task 3 Step 6 ✓
- check_agent_docs 0 errors: Task 3 Step 7 ✓

**Placeholder scan:** No TBDs, TODOs, or vague steps — each step has code.

**Type consistency:** `is_krx_holiday` signature `Union[date, str] -> bool` used consistently in tests (monkeypatch via `lambda d: True/False`) and in the module. `now.date()` call in `safety_checker.py` produces a `date` object.
