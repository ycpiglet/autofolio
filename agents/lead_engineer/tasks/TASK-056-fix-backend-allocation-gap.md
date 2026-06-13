---
type: task
id: TASK-056
status: 대기
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
updated_at: 2026-06-14T00:00:00+09:00
---

# TASK-056 fix: backend.allocation_gap() 미구현으로 portfolio/analysis 탭 mock fallback

작업 ID: TASK-056
상태: 대기
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
