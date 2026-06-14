---
unit_id: UNIT-TASK-056-001
task_id: TASK-056
task_set_id: TASKSET-PRODUCT-MATURITY
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "TASK-056 스텁은 backend.allocation_gap()이 없다고 기술했으나, 코드베이스 리팩터 이후 app/ui/backend.py:435에 이미 실 구현이 존재함. 실제 버그는 portfolio.py와 analysis.py의 silent except Exception 폴백 — 오류 발생 시 사용자에게 알림 없이 mock 데이터를 표시. 수정 내용: silent fallback에 st.warning() 추가, regression pin 테스트 작성."
inputs:
  - agents/lead_engineer/tasks/TASK-056-fix-backend-allocation-gap.md
  - app/ui/backend.py
  - app/ui/views/portfolio.py
  - app/ui/views/analysis.py
  - tests/unit/test_backend_allocation_gap.py
target_files:
  - app/ui/views/portfolio.py
  - app/ui/views/analysis.py
  - tests/unit/test_backend_allocation_gap.py
scope: "silent fallback에 st.warning() 추가. backend.allocation_gap() 구현 자체는 정상이므로 수정 없음. 인접 뷰 로직 변경 금지."
acceptance:
  - "backend.allocation_gap()이 holdings_df 기반 실 계산값을 반환함"
  - "portfolio.py 라이브 실패 시 st.warning 표시 (silent fallback 제거)"
  - "analysis.py 라이브 실패 시 st.warning 표시 (silent fallback 제거)"
  - "test_allocation_gap_uses_holdings_weights PASS"
  - "test_allocation_gap_empty_holdings_returns_negative_targets PASS"
  - "test_allocation_gap_multi_asset_weights PASS"
  - "test_allocation_gap_columns_schema PASS"
  - "python -m pytest tests/ -q green"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_backend_allocation_gap.py -v"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
handoff: "변경 파일 목록, 검증 결과, 스텁 기반 오류 사유, regression pin 근거 보고."
stop_condition: "portfolio.py/analysis.py silent fallback 수정 + 테스트 작성 완료 후 즉시 중단."
depends_on: []
---

# UNIT-TASK-056-001 — allocation_gap silent fallback 제거 + regression pin

## Context

TASK-056 스텁에는 `backend.allocation_gap()`이 없다고 기술되어 있었으나,
코드베이스 리팩터 이후 `app/ui/backend.py:435`에 실 구현이 존재한다.

실제 버그:
- `portfolio.py` line 88-92: `except Exception: st.dataframe(data.allocation_gap())`
  → 오류 발생 시 사용자 알림 없이 mock 표시 (silent fallback)
- `analysis.py` line 37-43: `except Exception: pass; return mock_data.allocation_gap()`
  → 동일하게 silent fallback

## Target Files

- `app/ui/views/portfolio.py` — silent fallback에 `st.warning(exc)` 추가
- `app/ui/views/analysis.py` — silent fallback에 `st.warning(exc)` 추가
- `tests/unit/test_backend_allocation_gap.py` — 신규 (regression pin)

## Verification Basis

`backend.allocation_gap()`은 이미 올바르게 구현되어 있어 테스트는 regression pin으로
즉시 PASS. 스텁이 pre-refactor 상태를 기반으로 작성된 것이 확인됨.

## 완료 기록

완료 시각: 2026-06-14T11:51:13+09:00
검토자: Backend Engineer / QA

**변경 내용:**
- `app/ui/views/portfolio.py` silent `except Exception` → `except Exception as exc: st.warning(f"라이브 갭 조회 실패 — 데모 데이터로 대체합니다: {exc}")`
- `app/ui/views/analysis.py` silent `except Exception` → `except Exception as exc: st.warning(f"라이브 갭 조회 실패 — 데모 데이터로 대체합니다: {exc}")`
- `tests/unit/test_backend_allocation_gap.py` 신규: 4개 테스트 (regression pin)

**검증 결과:**
- 4 passed (test_backend_allocation_gap.py) — 즉시 PASS (regression pin)
- 641 passed, 1 warning (전체, Windows 임시 파일 정리 경고 — 무해)
- `python scripts/check_agent_docs.py` 0 error (아래 확인)
