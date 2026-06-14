---
type: task
id: TASK-066
status: 완료
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
updated_at: 2026-06-14T20:04:53+09:00
---

# TASK-066 feat: 테스트 커버리지 60%+ 달성 (누락 36개 케이스)

작업 ID: TASK-066
상태: 완료
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

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-PRODUCT-MATURITY.md`
- Taskset: `agents/project/initiatives/TASKSET-PRODUCT-MATURITY.md`

## 완료 기록

완료 시각: 2026-06-14T20:04:53+09:00
검토자: Lead Engineer / QA

## 증거

정량 바(≥60%)는 이번 wave 누적 테스트로 이미 충족(측정 77.83%); 본 태스크는 안전-임계 실패모드 테스트 55개를 추가해 실패경로를 경화함.

- 신규 테스트 파일 4개, 신규 테스트 55개 (all pass)
- 전체 pytest: 805 passed (이전 756 → +49 순증)
- coverage: 77.85% (>= 50% CI gate, >= 60% 목표 모두 충족)
- `python scripts/check_agent_docs.py`: 0 error(s)
- 제품 코드 변경 없음 -- 테스트 파일만 추가

### 파일별 테스트 수

| 파일 | 테스트 수 | 카테고리 |
|------|-----------|---------|
| `tests/unit/test_boundary_conditions.py` | 10 | 경계값: 일일한도/주문금액/서킷브레이커 |
| `tests/unit/test_kis_failure_modes.py` | 14 | KIS: 타임아웃/인증만료/잘못된종목/부분체결 |
| `tests/unit/test_repository_edge_cases.py` | 21 | 레포: 빈DB/FK위반/중복삽입 |
| `tests/integration/test_alert_channel_fallback.py` | 10 | 알림버스: 채널폴백/버스상태/로그진단 |

## 리뷰

특이사항 없음. 모든 테스트 TZ-robust (UTC 서버에서도 통과). 네트워크 mock 적용 (실KIS 호출 없음). 제품 코드 미변경.

후속 발견 버그 없음.
