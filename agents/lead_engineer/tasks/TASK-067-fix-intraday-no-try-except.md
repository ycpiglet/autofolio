---
type: task
id: TASK-067
status: 완료
owner: UI/UX Designer
assignees: [UI/UX Designer, QA]
priority: High
difficulty: 낮
est_hours: 2
est_tokens: 12000
tags: [bug, ui, analysis, error-handling]
gate: -
trigger_meeting: 즉시 처리 권고
audit_log: AUDIT-2026-06-14-001
created: 2026-06-14
created_at: 2026-06-14T00:00:00+09:00
updated_at: 2026-06-14T12:48:04+09:00
---

# TASK-067 fix: 인트라데이 섹션 try/except 누락으로 분석 탭 전체 크래시

작업 ID: TASK-067
상태: 완료
Owner: UI/UX Designer
요청 시각: 2026-06-14
기록 시각: 2026-06-14T00:00:00+09:00
요청자: Owner
수행자: UI/UX Designer
의도: analysis.py _intraday_section()에 try/except 추가로 분석 탭 크래시 방지
대상: app/ui/analysis.py _intraday_section()
방법: _intraday_section() try/except 감싸기 + 다른 섹션과 동일 에러 메시지 패턴 적용 + AppTest KIS 오류 시 탭 크래시 없음 확인
감사 로그: AUDIT-2026-06-14-001

## 버그 내용

`app/ui/analysis.py`의 `_intraday_section()`이 `backend.intraday_chart_df()` 호출에 `try/except`가 없음.

**증상**: KIS API 실패(네트워크 오류, 인증 만료 등) 시 분석 탭 전체가 사용자에게 Python traceback을 노출하며 크래시.

**원인**: 다른 섹션들(`_sector_section()`, `_fundamental_section()` 등)은 `except Exception as e: st.error(...)` 패턴으로 보호되어 있으나 `_intraday_section()`만 누락.

## 수정 방향

1. `_intraday_section()`을 try/except로 감싸기:
   ```python
   try:
       df = backend.intraday_chart_df(symbol)
       # ... 차트 렌더링
   except Exception as e:
       st.error(f"분봉 데이터를 불러올 수 없습니다: {e}")
   ```
2. 다른 섹션과 동일한 에러 메시지 스타일 사용
3. AppTest: KIS 오류 시 탭 크래시 없이 에러 메시지 표시 확인

## 완료 기준

- `_intraday_section` try/except 추가
- KIS 오류 시 탭 크래시 없이 에러 메시지 표시
- AppTest 통과

## Done When

- _intraday_section try/except 추가
- KIS 오류 시 탭 크래시 없이 에러 메시지 표시
- AppTest 통과

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙: `agents/lead_engineer/tasks/units/TASK-067/UNIT-TASK-067-001.md`

- Initiative: `agents/project/initiatives/INIT-PRODUCT-MATURITY.md`
- Taskset: `agents/project/initiatives/TASKSET-PRODUCT-MATURITY.md`

## 완료 기록

완료 시각: 2026-06-14T12:48:04+09:00
검토자: UI/UX Designer / QA (self-review 명시)

## 증거

- `app/ui/views/analysis.py` `_intraday_section()`: `backend.intraday_chart_df()` 호출을 `try/except Exception as exc` 블록으로 감쌈. 예외 발생 시 `st.error(f"분봉 데이터를 불러올 수 없습니다: {exc}")` 후 `return`. 기존 `_sector_performance()` 등 형제 섹션과 동일 패턴 (`except Exception as exc:  # noqa: BLE001`).
- `tests/unit/test_analysis_intraday_view.py`: `test_intraday_section_degrades_gracefully_on_error` 신규 추가.
  - `intraday_chart_df`를 `RuntimeError` raise로 mock → 수정 전 FAILED (at.exception 존재), 수정 후 PASSED.
  - 기존 `test_analysis_view_renders_intraday_controls` 계속 PASSED.
- 수정 전: `test_intraday_section_degrades_gracefully_on_error` FAILED — `RuntimeError: KIS API 인증 만료 — 분봉 조회 실패` 노출.
- 수정 후: 2 passed (test_analysis_intraday_view.py), 509 passed (unit), 656 passed (전체).
- `python scripts/check_agent_docs.py` → 0 error(s).
- `python scripts/generate_views.py --check` → OK (66 tasks / 6 views).
- `python scripts/build_task_index.py --check` → OK.

## 리뷰

- 패턴 일관성: 기존 `_sector_performance()` (line 55), `_backtest_section()` (line 167), `journal_tab` (line 315) 등과 동일한 `except Exception as exc:  # noqa: BLE001` 형식 적용.
- 해피패스 무변경: `df = backend.intraday_chart_df(...)` 이후 차트/테이블 렌더 로직 그대로 유지.
- 격리: `sys.modules` 오염 없음. AppTest embedded script + `patch.object` 사용.
- TZ 독립: 테스트에 날짜 계산 없음.

실측 비용 (시간): ~0.2h
실측 비용 (LLM 토큰): ~30k

## Independent Audit

판정: 통과 — 수정 전 FAILED / 수정 후 PASSED TDD 증거 확인. `_intraday_section` try/except 누락 버그 해소, 기존 패턴 일치, happy-path 테스트 유지. 656 passed (전체), 0 doc error. 격리 문제 없음 (AppTest + patch.object, sys.modules 미오염).
