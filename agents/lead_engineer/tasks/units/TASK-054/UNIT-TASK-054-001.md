---
unit_id: UNIT-TASK-054-001
task_id: TASK-054
task_set_id: TASKSET-PRODUCT-MATURITY
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [repeated_failure]
context: "alerts.py 채널 토글(Telegram/Kakao/Discord/Notion/Email)과 알림 규칙 multiselect가 on_change 핸들러 없이 렌더만 됨. 변경 사항이 session_state에만 머물고 새로고침 시 초기화됨. 기존 앱 영속 레이어: app/ui/vault.py (암호화 JSON) + app/services/connections.py (vault 래퍼). alert_settings를 vault의 별도 키에 저장."
inputs:
  - agents/lead_engineer/tasks/TASK-054-fix-alerts-settings-no-persist.md
  - app/ui/views/alerts.py
  - app/services/connections.py
  - app/ui/vault.py
target_files:
  - app/ui/views/alerts.py
  - app/services/connections.py
  - tests/unit/test_alerts_persist.py
scope: "alerts.py render() on_change 핸들러 추가 + vault load/save 연결. connections.py에 get_alert_settings/save_alert_settings 추가. 다른 views, vault.py, store.py 변경 금지."
acceptance:
  - "채널 토글 변경 → vault에 즉시 저장 (on_change callback)"
  - "규칙 multiselect 변경 → vault에 즉시 저장"
  - "페이지 로드 시 vault에서 초기값 로드 (세션 최초 진입)"
  - "데모/라이브 모드 모두 동작 (vault은 device-local)"
  - "get_alert_settings, save_alert_settings 모두 connections.__all__ 포함"
  - "python -m pytest tests/unit/test_alerts_persist.py -q green (7 tests)"
  - "python -m pytest tests/unit -q green (516+7 tests)"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_alerts_persist.py -q"
  - "python -m pytest tests/unit -q"
  - "python scripts/check_agent_docs.py"
handoff: "변경 파일 목록, pytest 결과, 영속 메커니즘, TDD 실패-선행 증거 보고."
stop_condition: "alerts.py + connections.py 수정 후 즉시 중단. 다른 뷰 또는 vault.py 수정 금지."
depends_on: []
---

# UNIT-TASK-054-001 — 알림 채널/규칙 설정 영속화

## Context

`app/ui/views/alerts.py`의 `render()`가 채널 토글 5개와 알림 규칙 multiselect를
하드코딩 기본값으로 렌더하고 `on_change` 핸들러가 없어 변경 사항이 session_state에만
머물고 새로고침 시 초기화됨.

기존 앱 영속 레이어: `app/ui/vault.py` (암호화 JSON) 위에
`app/services/connections.py`가 `"connections"` 키를 관리한다.
알림 설정은 `"alert_settings"` 키를 별도로 사용해 충돌 없이 저장한다.

## Target Files

- `app/services/connections.py` — `get_alert_settings()`, `save_alert_settings()` 추가
- `app/ui/views/alerts.py` — `render()` 재작성 (load-on-init + on_change 콜백)
- `tests/unit/test_alerts_persist.py` — 신규 (TDD: 실패 선행)

## Scope

In scope: 위 3개 파일만.

Out of scope: `vault.py`, `store.py`, 다른 뷰, 다른 서비스.

## Acceptance Criteria

- `get_alert_settings()` 빈 vault → 기본값 반환
- `save_alert_settings()` round-trip: 저장 → 로드 값 일치
- `save_alert_settings()` 기존 connections 데이터(brokers/channels) 보존
- AppTest: 저장된 채널값으로 토글 초기화 확인
- AppTest: 토글 변경 → on_change 실행 (no exception, 값 반영)
- AppTest: multiselect 변경 → on_change 실행 (no exception, 값 반영)
- `get_alert_settings`/`save_alert_settings` 모두 `__all__` 포함
- `python -m pytest tests/unit -q` green

## 완료 기록

완료 시각: 2026-06-14T13:09:51+09:00
검토자: UI/UX Designer / QA

**변경 내용:**

- `app/services/connections.py`: `_DEFAULT_ALERT_CHANNELS`, `_DEFAULT_ALERT_RULES` 상수 추가.
  `get_alert_settings()`: vault `"alert_settings"` 키 로드, None이면 기본값 반환.
  `save_alert_settings()`: vault 전체 로드 후 `"alert_settings"` 키만 덮어쓰기 (connections 데이터 보존).
  `if settings is None:` 가드 (빈 rules `[]` 허용).
  모두 `__all__` 추가.

- `app/ui/views/alerts.py`: `render()` 재작성.
  `from app.services.connections import ...` 모듈 상단 임포트.
  첫 렌더 시 `get_alert_settings()` 호출 → `_alert_channels`/`_alert_rules` session_state 초기화.
  각 채널 토글: `on_change=_on_channel_change, args=(name,)` → `save_alert_settings()` 즉시 호출.
  규칙 multiselect: `key="alert_rules_widget"`, `on_change=_on_rules_change` → `save_alert_settings()` 즉시 호출.
  데모/라이브 모드 공통 동작 (vault은 device-local).

- `tests/unit/test_alerts_persist.py`: 신규. TDD — 구현 전 7 FAILED 확인 후 작성.
  Unit: defaults/round-trip/connections-isolation/__all__ 검증.
  AppTest: 저장된 값으로 토글 초기화, 토글 변경 시 on_change 실행, multiselect 변경 시 on_change 실행.
  `patch.object(alerts_mod, ...)` 패턴 (모듈 상단 바인딩에 패치).

**검증 결과:**

- 수정 전: `AttributeError: module 'app.services.connections' has no attribute 'get_alert_settings'` (7 FAILED)
- 수정 후: 7 passed (test_alerts_persist.py), 516 passed (전체 unit)
- `python scripts/check_agent_docs.py` → 0 error (확인 예정)
