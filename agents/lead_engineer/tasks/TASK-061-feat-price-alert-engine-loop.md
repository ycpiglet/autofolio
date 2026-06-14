---
type: task
id: TASK-061
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, QA]
priority: High
difficulty: 중-상
est_hours: 8
est_tokens: 50000
tags: [feature, engine, alerts, notifications]
gate: -
trigger_meeting: 다음 사이클
audit_log: AUDIT-2026-06-14-001
created: 2026-06-14
created_at: 2026-06-14T00:00:00+09:00
updated_at: 2026-06-14T16:05:07+09:00
---

# TASK-061 feat: 가격 알림 엔진 평가 루프 구현

작업 ID: TASK-061
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-14
기록 시각: 2026-06-14T00:00:00+09:00
요청자: Owner
수행자: Backend Engineer
의도: live_trading_engine.py run_once()에 price_alerts 평가 루프 구현
대상: app/trading/live_trading_engine.py run_once(), app/services/alerts.py, app/database/repositories.py
방법: list_active_alerts/mark_alert_fired 구현 + run_once() 평가 루프 추가 + NotificationBus 연동 + 단위테스트
감사 로그: AUDIT-2026-06-14-001

## 배경

`app/services/alerts.py`의 `add_price_alert()`가 DB에 가격 알림을 저장하는 기능은 구현되어 있으나, 엔진에서 이 알림을 주기적으로 평가하고 발송하는 루프가 없어 dead feature 상태.

**증상**: 사용자가 가격 알림을 등록해도 조건 충족 시 알림이 발송되지 않음.

## 수정 방향

1. `live_trading_engine.py run_once()`에 price_alerts 평가 루프 추가:
   ```python
   alerts = repo.list_active_alerts()
   for alert in alerts:
       current_price = kis.get_price(alert.symbol)
       if alert.condition_met(current_price):
           NotificationBus.send(alert.message)
           repo.mark_alert_fired(alert.id)
   ```
2. `repositories.py`에 `list_active_alerts()` 및 `mark_alert_fired()` 구현 (미구현 시)
3. `NotificationBus.send()` 연동 확인
4. 단위테스트: 조건 충족/미충족 케이스, 발송 후 fired=True 확인

## 완료 기준

- `run_once()`가 price_alerts 평가
- 조건 충족 시 `NotificationBus.send()` 호출
- 알림 `fired=True` 업데이트
- 단위테스트 통과

## Done When

- `run_once()`가 price_alerts 평가
- 조건 충족 시 NotificationBus.send() 호출
- 알림 fired=True 업데이트
- 단위테스트 통과

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-PRODUCT-MATURITY.md`
- Taskset: `agents/project/initiatives/TASKSET-PRODUCT-MATURITY.md`

## 완료 기록

완료 시각: 2026-06-14T16:05:07+09:00
검토자: Backend Engineer

## 증거

- `tests/unit/test_price_alert_engine.py`: 7 신규 TDD 테스트 (RED→GREEN 검증 완료)
- `app/engine/live_trading_engine.py`: `evaluate_price_alerts()` 추가, `run_once()` 말미 연결
- `python -m pytest tests/unit/test_price_alert_engine.py -v` → 7 passed
- `python -m pytest tests/ -q` → 683 passed
- `python scripts/check_agent_docs.py` → 0 error

## 리뷰

구현 방향:
- 기존 `repo.trigger_alert()` 재사용 (`mark_alert_fired` 별칭 불필요 — 이미 존재하는 메서드 사용)
- `NotificationBus` 대신 `Notifier` 직접 사용 (엔진 기존 패턴 — `self.notifier`)
- 거래 시간 창 독립 (알림 = 주문 아님, 트레이딩 창 없이 언제든 발송)
- `notifier=None` 안전 처리 (`if self.notifier:` 가드)
- 가격 조회 실패 시 해당 알림 건너뜀 (다른 알림 평가 계속)
