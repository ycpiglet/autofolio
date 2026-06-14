---
unit_id: UNIT-TASK-067-001
task_id: TASK-067
task_set_id: TASKSET-PRODUCT-MATURITY
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "_intraday_section()가 backend.intraday_chart_df() 호출에 try/except 없음. KIS API 실패 시 분석 탭 전체가 Python traceback 노출하며 크래시. 다른 섹션(_sector_performance, _backtest_section 등)은 except Exception as exc: st.error(...) 패턴으로 보호되어 있으나 _intraday_section만 누락. app/ui/views/analysis.py line 211 수정 필요."
inputs:
  - agents/lead_engineer/tasks/TASK-067-fix-intraday-no-try-except.md
  - app/ui/views/analysis.py
  - tests/unit/test_analysis_intraday_view.py
target_files:
  - app/ui/views/analysis.py
  - tests/unit/test_analysis_intraday_view.py
scope: "app/ui/views/analysis.py _intraday_section() try/except 추가만. 다른 섹션·모듈 변경 금지."
acceptance:
  - "_intraday_section() try/except 추가 완료"
  - "KIS API 오류 시 탭 크래시 없이 st.error() 메시지 표시"
  - "test_intraday_section_degrades_gracefully_on_error PASSED"
  - "기존 test_analysis_view_renders_intraday_controls PASSED"
  - "python -m pytest tests/ -q green"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_analysis_intraday_view.py -v"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
handoff: "변경 파일 목록, TDD 실패→통과 증거, pytest 결과, check_agent_docs 결과 보고."
stop_condition: "_intraday_section() try/except 추가 후 즉시 중단. 다른 analysis.py 섹션이나 인접 모듈로 확장 금지."
depends_on: []
---

# UNIT-TASK-067-001 — 분석 탭 _intraday_section try/except 추가

## Context

`app/ui/views/analysis.py` `_intraday_section()` (line 211)에서
`backend.intraday_chart_df(options[label], time_unit=unit, count=int(count))` 호출이
`try/except` 없이 노출되어 있다.

KIS API 실패(네트워크 오류, 인증 만료 등) 시 `RuntimeError`/`Exception`이 전파되어
분석 탭 전체가 Python traceback을 사용자에게 노출하며 크래시된다.

형제 섹션들(`_sector_performance()` line 55, `_backtest_section()` line 167 등)은
`except Exception as exc:  # noqa: BLE001` → `st.error(...)`/`st.warning(...)` → `return` 패턴으로 보호되어 있다.

## Inputs

- `agents/lead_engineer/tasks/TASK-067-fix-intraday-no-try-except.md` — 버그 명세
- `app/ui/views/analysis.py` — `_intraday_section()` 구현
- `tests/unit/test_analysis_intraday_view.py` — 기존 테스트 + 신규 TDD 테스트

## Target Files

- `app/ui/views/analysis.py`
- `tests/unit/test_analysis_intraday_view.py`

## Scope

In scope: `_intraday_section()` 내 `backend.intraday_chart_df()` 호출을 try/except로 감싸기.

Out of scope: 다른 섹션, 다른 뷰, 서비스 레이어 변경.

## Steps

1. `tests/unit/test_analysis_intraday_view.py`에 `test_intraday_section_degrades_gracefully_on_error` 추가.
   - `backend.intraday_chart_df`를 `RuntimeError` raise로 mock.
   - `at.exception`이 falsy임을 assert.
   - `at.error`/`at.warning`/`at.info`에 '분봉' 포함 메시지 존재 assert.
2. 테스트가 현재 코드에서 FAILED임을 확인 (TDD red).
3. `app/ui/views/analysis.py` `_intraday_section()` line 211:
   ```python
   try:
       df = backend.intraday_chart_df(options[label], time_unit=unit, count=int(count))
   except Exception as exc:  # noqa: BLE001
       st.error(f"분봉 데이터를 불러올 수 없습니다: {exc}")
       return
   ```
4. 테스트 PASSED 확인 (TDD green).
5. 전체 pytest green 확인.

## Acceptance Criteria

- `_intraday_section()` try/except 추가 완료
- `test_intraday_section_degrades_gracefully_on_error` PASSED
- 기존 `test_analysis_view_renders_intraday_controls` PASSED
- `python -m pytest tests/ -q` green
- `python scripts/check_agent_docs.py` 0 error

## Verification

```powershell
python -m pytest tests/unit/test_analysis_intraday_view.py -v
python -m pytest tests/ -q
python scripts/check_agent_docs.py
```

## Handoff

변경 파일 목록, TDD 실패→통과 증거, pytest 결과 보고.

## Stop Boundary

`_intraday_section()` try/except 추가 후 즉시 중단.
다른 analysis.py 섹션·인접 모듈로 확장 금지.

## 완료 기록

완료 시각: 2026-06-14T12:48:04+09:00

**변경 내용:**
- `app/ui/views/analysis.py` `_intraday_section()`: `backend.intraday_chart_df()` 호출을 `try/except Exception as exc:  # noqa: BLE001` 블록으로 감쌈 (1+2줄 추가). 예외 시 `st.error(f"분봉 데이터를 불러올 수 없습니다: {exc}")` → `return`. 기존 섹션 패턴과 동일.
- `tests/unit/test_analysis_intraday_view.py`: `test_intraday_section_degrades_gracefully_on_error` 신규 추가. `intraday_chart_df_raises` mock으로 `RuntimeError` 주입 → 수정 전 FAILED, 수정 후 PASSED.

**검증 결과:**
- 수정 전: `test_intraday_section_degrades_gracefully_on_error` FAILED (`AssertionError: Page crashed: ...RuntimeError: KIS API 인증 만료 — 분봉 조회 실패`)
- 수정 후: 2 passed (test_analysis_intraday_view.py), 509 passed (unit), 656 passed (전체)
- `python scripts/check_agent_docs.py` → 0 error(s)
- `python scripts/generate_views.py --check` → OK
- `python scripts/build_task_index.py --check` → OK
