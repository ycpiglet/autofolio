---
type: task
id: TASK-066
status: 대기
owner: QA
assignees: [QA, Backend Engineer]
priority: High
difficulty: 중
est_hours: 12
est_tokens: 80000
tags: [testing, coverage, safety]
gate: Phase 3 전 필수
trigger_meeting: 다음 사이클
audit_log: AUDIT-2026-06-14-001
created: 2026-06-14
created_at: 2026-06-14T00:00:00+09:00
updated_at: 2026-06-14T00:00:00+09:00
---

# TASK-066 feat: 테스트 커버리지 60%+ 달성 (누락 36개 케이스)

작업 ID: TASK-066
상태: 대기
Owner: QA
요청 시각: 2026-06-14
기록 시각: 2026-06-14T00:00:00+09:00
요청자: Owner
수행자: QA, Backend Engineer
의도: 성숙도 감사 식별 36개 누락 테스트 케이스 구현으로 커버리지 60%+ 달성
대상: tests/ (신규 4개 파일 + 기존 파일 보완)
방법: 경계값/KIS실패모드/레포지터리엣지/주문플로우예외/알림채널실패 테스트 36개 구현 + pytest --cov 60%+ 검증
감사 로그: AUDIT-2026-06-14-001

## 배경

2026-06-14 성숙도 감사에서 테스트 커버리지가 ~50%로 목표(60%+) 미달 확인. 36개 누락 테스트 케이스가 식별되었다. Phase 3(UI 대개편 매매/설정 게이트) 진입 전 필수 완료 조건.

## 누락 케이스 분류

1. **경계값(boundary) 테스트** (~8개)
   - 일일 주문한도 경계 (정확히 한도액)
   - 최소 주문금액 경계
   - 서킷브레이커 임계치 경계

2. **KIS API 실패 모드** (~10개)
   - 네트워크 타임아웃
   - 인증 만료
   - 종목 코드 오류 응답
   - 부분 체결

3. **레포지터리 엣지케이스** (~8개)
   - 빈 DB에서 조회
   - 동일 시각 중복 삽입
   - FK 위반 시도

4. **주문 플로우 예외** (~6개)
   - 조건 평가 중 KIS 오류
   - 서킷브레이커 발동 후 주문 시도
   - kill_switch 중 자동 주문 시도

5. **알림 채널 실패 시나리오** (~4개)
   - Telegram 발송 실패 시 다음 채널 폴백
   - 모든 채널 실패 시 로그 기록

## 신규 테스트 파일

- `tests/unit/test_boundary_conditions.py`
- `tests/unit/test_kis_failure_modes.py`
- `tests/unit/test_repository_edge_cases.py`
- `tests/integration/test_alert_channel_fallback.py`

## 완료 기준

- 36개 테스트 all pass
- `pytest --cov` ≥ 60%
- `python scripts/check_agent_docs.py` 0 error

## Done When

- 36개 테스트 all pass
- pytest --cov ≥ 60%
- check_agent_docs 0 error
