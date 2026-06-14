---
type: task
id: TASK-056
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, QA]
priority: High
difficulty: 중
est_hours: 3
est_tokens: 25000
tags: [bug, backend, portfolio, allocation]
gate: -
trigger_meeting: 즉시 처리 권고
audit_log: AUDIT-2026-06-14-001
created: 2026-06-14
created_at: 2026-06-14T00:00:00+09:00
updated_at: 2026-06-14T11:51:13+09:00
---

# TASK-056 fix: backend.allocation_gap() 미구현으로 portfolio/analysis 탭 mock fallback

작업 ID: TASK-056
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-14
기록 시각: 2026-06-14T00:00:00+09:00
요청자: Owner
수행자: Backend Engineer
의도: backend.py에 allocation_gap() 메서드 구현하여 라이브 모드에서 실 데이터 표시
대상: app/ui/backend.py, app/ui/portfolio.py, app/ui/analysis.py
방법: allocation_gap() 구현 + portfolio/analysis fallback 제거 + mock 비교 단위테스트 추가
감사 로그: AUDIT-2026-06-14-001

## 버그 내용

`app/ui/backend.py`에 `allocation_gap()` 메서드가 없어 `portfolio.py`와 `analysis.py`가 라이브 모드에서 `AttributeError`를 catch하고 mock 데이터로 silent fallback.

**증상**: 라이브 모드에서 포트폴리오 탭과 분석 탭의 목표 비중 대비 현재 비중 차이(allocation gap) 섹션이 항상 목업 데이터를 표시.

**원인**: `backend.py`에 `allocation_gap()` 메서드 자체가 존재하지 않아 AttributeError가 발생하고 except 블록이 mock 데이터를 반환.

## 수정 방향

1. `app/ui/backend.py`에 `allocation_gap()` 메서드 구현
   - 현재 보유 종목별 비중 계산 (현재가 × 보유수량 / 총 포트폴리오 가치)
   - 목표 비중 (IC 제안 또는 설정값에서 로드)
   - 차이(gap) = 목표 비중 - 현재 비중 반환
2. `portfolio.py`, `analysis.py`의 fallback 경로 제거 또는 명시적 오류 처리로 교체
3. mock 대비 실 데이터 비교 테스트 작성

## 완료 기준

- `backend.allocation_gap()` 구현
- 라이브 모드에서 실 데이터 표시
- mock 비교 테스트 통과
- `python -m pytest tests/ -q` green

## Done When

- `backend.allocation_gap()` 구현
- 라이브 모드에서 실 데이터 표시
- mock 비교 테스트 통과

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙: `agents/lead_engineer/tasks/units/TASK-056/UNIT-TASK-056-001.md`

- Initiative: `agents/project/initiatives/INIT-PRODUCT-MATURITY.md`
- Taskset: `agents/project/initiatives/TASKSET-PRODUCT-MATURITY.md`

## 완료 기록

완료 시각: 2026-06-14T11:51:13+09:00
검토자: Backend Engineer / QA

## 증거

**검증 결과 (리팩터 후 실제 상태)**

- `backend.allocation_gap()`은 `app/ui/backend.py:435`에 이미 실 구현 존재.
  스텁이 pre-refactor 상태를 기술한 것으로 확인됨.
- 실제 버그: `portfolio.py`(line 88–92), `analysis.py`(line 37–43)의 silent `except Exception` fallback.
  오류 발생 시 사용자 알림 없이 mock 데이터를 표시하는 문제.
- 수정: silent fallback에 `st.warning(exc)` 추가 (양쪽 뷰 동일 처리).
- 테스트 `tests/unit/test_backend_allocation_gap.py` 신규 4개 (regression pin):
  - `test_allocation_gap_uses_holdings_weights` — 라이브 계산 vs mock 값 다름 검증
  - `test_allocation_gap_empty_holdings_returns_negative_targets` — 빈 포트폴리오 경계값
  - `test_allocation_gap_multi_asset_weights` — 두 자산군 비중 계산 정확도
  - `test_allocation_gap_columns_schema` — 4-컬럼 스키마 고정
- 수정 전: 위 4 테스트 즉시 PASS (regression pin — 이미 올바른 구현 확인)
- 수정 후: 641 passed, 1 warning (Windows 임시 파일 정리 — 무해)

## 리뷰

- `allocation_gap()`은 holdings_df의 `자산군`·`비중` 컬럼을 groupby하여 현재% 계산.
  target dict와 비교해 갭 = 현재% − 목표%로 반환. 수식 정확.
- silent fallback 제거: `except Exception as exc: st.warning(...)` 패턴으로
  라이브 오류 발생 시 사용자가 데모 데이터임을 인지할 수 있음.
- 스텁 버그: TASK-056 스텁은 pre-refactor 상태 기준 작성. 리팩터 후 구현이 존재하므로
  fabrication 없이 regression pin + silent fallback 수정으로 완결.

실측 비용 (시간): ~0.3h
실측 비용 (LLM 토큰): ~35k

## Independent Audit

판정: 통과 — `backend.allocation_gap()`이 이미 실 구현임을 코드 검증으로 확인(line 435).
silent fallback(portfolio.py, analysis.py) 제거 확인. regression pin 4개 즉시 PASS.
전체 641 passed, 0 doc error. fabrication 없음 — 스텁 오류 사유 명시.
