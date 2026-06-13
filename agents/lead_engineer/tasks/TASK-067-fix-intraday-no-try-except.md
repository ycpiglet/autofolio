---
type: task
id: TASK-067
status: 대기
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
updated_at: 2026-06-14T00:00:00+09:00
---

# TASK-067 fix: 인트라데이 섹션 try/except 누락으로 분석 탭 전체 크래시

작업 ID: TASK-067
상태: 대기
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
