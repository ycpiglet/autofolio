---
unit_id: UNIT-TASK-061-001
task_id: TASK-061
task_set_id: TASKSET-PRODUCT-MATURITY
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "price_alerts 테이블에 저장된 가격 알림이 엔진에서 평가되지 않아 dead feature. LiveTradingEngine.evaluate_price_alerts() 신규 메서드 추가 및 run_once() 호출 연결."
inputs:
  - agents/lead_engineer/tasks/TASK-061-feat-price-alert-engine-loop.md
  - app/engine/live_trading_engine.py
  - app/database/repositories.py
  - app/notification/notifier.py
target_files:
  - app/engine/live_trading_engine.py
  - tests/unit/test_price_alert_engine.py
scope: "LiveTradingEngine.evaluate_price_alerts() 신규 메서드 + run_once() 연결. 주문/거래 기능 변경 금지."
acceptance:
  - "ABOVE 조건 충족 시 notifier.send() 1회 호출 + alert active=0"
  - "ABOVE 조건 미충족 시 notifier.send() 미호출 + alert active=1 유지"
  - "BELOW 조건 충족 시 notifier.send() 1회 호출 + alert active=0"
  - "BELOW 조건 미충족 시 notifier.send() 미호출 + alert active=1 유지"
  - "active=0 사전 발동 알림 재발송 금지"
  - "run_once() 호출 시 evaluate_price_alerts() 실행"
  - "notifier=None 시 예외 없음"
  - "python -m pytest tests/ -q green"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_price_alert_engine.py -v"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
  - "python scripts/work_schema_gate.py --items --check"
  - "python scripts/build_task_index.py --check"
  - "python scripts/generate_views.py --check"
handoff: "변경 파일: live_trading_engine.py (evaluate_price_alerts + run_once 연결), tests/unit/test_price_alert_engine.py (신규 7 테스트). trigger_alert() 기존 메서드 재사용 (mark_alert_fired 별칭 불필요)."
stop_condition: "evaluate_price_alerts() 구현 후 즉시 중단. 주문/거래/리스크 로직 변경 금지."
depends_on: []
---

# UNIT-TASK-061-001 — 가격 알림 엔진 평가 루프 구현

## Context

`Repository.list_active_alerts()` / `trigger_alert()` 는 이미 구현되어 있음.
`LiveTradingEngine.run_once()`가 이를 호출하지 않아 dead feature.

## Target Files

- `app/engine/live_trading_engine.py`
- `tests/unit/test_price_alert_engine.py` (신규)

## Scope

In scope: `LiveTradingEngine.evaluate_price_alerts()` 신규 메서드, `run_once()` 연결, TDD 테스트.

Out of scope: 주문/거래 로직, repositories.py 변경, UI, 리스크 한도.

## Acceptance Criteria

- ABOVE/BELOW 조건 충족/미충족 케이스 정확히 평가
- 충족 시 `self.notifier.send()` 호출 + `repo.trigger_alert(id)` 호출
- `active=0` 알림 재발송 없음
- `run_once()` → `evaluate_price_alerts()` 호출 검증
- `notifier=None` 안전

## 완료 기록

완료 시각: 2026-06-14T16:05:07+09:00
검토자: Backend Engineer

**변경 내용:**
- `app/engine/live_trading_engine.py`: `evaluate_price_alerts()` 신규 메서드 추가. `run_once()` 말미에 호출. ABOVE/BELOW 조건 평가, 충족 시 `notifier.send()` + `repo.trigger_alert()`, 가격 조회 예외 처리(로그+continue), `notifier=None` 안전.
- `tests/unit/test_price_alert_engine.py` (신규): 7 TDD 테스트. 실제 네트워크/브로커 없이 MagicMock 사용. 격리된 TemporaryDirectory DB. 거래창 독립 (알림 = 주문 아님).

**구현 세부:**
- `list_active_alerts()` / `trigger_alert()` 기존 메서드 재사용 (신규 DB 메서드 없음)
- `NotificationBus` 대신 `Notifier` 직접 사용 (엔진 기존 패턴)
- 거래 시간 창 독립 (알림은 주문이 아님)

**검증 결과:**
- `test_price_alert_engine.py`: 7 passed (RED→GREEN 검증)
- 전체: 683 passed
- `check_agent_docs.py`: 0 error (gates below)
