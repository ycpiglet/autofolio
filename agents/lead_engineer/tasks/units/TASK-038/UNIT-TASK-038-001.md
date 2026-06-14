---
unit_id: UNIT-TASK-038-001
task_id: TASK-038
task_set_id: TASKSET-RESEARCH-REPORTING
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "워치리스트/스크리너/알림 dry-run 확장 — read-only UI/backend. 파일 기반 JSON 영속, 스크리너 필터, 알림 dry-run 평가. 주문 경로 완전 제외."
inputs:
  - agents/lead_engineer/tasks/TASK-038-watchlist-screener-alert-expansion.md
  - app/ui/backend.py
  - app/ui/vault.py
  - app/services/connections.py
target_files:
  - app/services/watchlist_screener.py
  - app/ui/views/watchlist.py
  - app/ui/autofolio_app.py
  - tests/unit/test_watchlist_screener_service.py
  - tests/unit/test_watchlist_view_apptest.py
scope: "file-backed watchlist/screener persistence, screener filter logic, alert dry-run evaluation, Streamlit view wired into navigation. No order path, no schema migration, no real-time push."
acceptance:
  - "저장형 watchlist/screener CRUD (파일 기반)"
  - "스크리너 필터 8종 (가격대/등락률/업종/PER/PBR/배당수익률/공시keyword/보유여부)"
  - "알림 dry-run 4종 (가격/거래량/공시/비중)"
  - "AppTest + unit tests 통과"
  - "no-order boundary AST 검증 테스트"
  - "960 passed, 78% coverage"
  - "check_agent_docs 0 error"
verification:
  - "python -m pytest tests/unit/test_watchlist_screener_service.py tests/unit/test_watchlist_view_apptest.py -v"
  - "python -m pytest tests/ -q --cov=app --cov-fail-under=50"
  - "python scripts/check_agent_docs.py"
  - "python scripts/generate_views.py --check"
  - "python scripts/build_task_index.py --check"
handoff: "변경 파일 목록, 960 passed, 78% coverage, 0 doc error, commit SHA."
stop_condition: "watchlist_screener service + view + nav wiring + tests 완료 후 즉시 중단."
depends_on: []
---

# UNIT-TASK-038-001 — Watchlist/Screener/Alert dry-run UI (read-only)

## Context

TASK-038 구현. 파일 기반 JSON 영속형 워치리스트/스크리너 + Streamlit 뷰 + 알림 dry-run.
주문 경로 없음, DB 스키마 마이그레이션 없음.

## Target Files

- `app/services/watchlist_screener.py` — 서비스 모듈 (신규)
- `app/ui/views/watchlist.py` — Streamlit 뷰 (신규)
- `app/ui/autofolio_app.py` — 내비게이션 추가
- `tests/unit/test_watchlist_screener_service.py` — 유닛 테스트 (신규)
- `tests/unit/test_watchlist_view_apptest.py` — AppTest (신규)

## 완료 기록

완료 시각: 2026-06-15T00:46:11+09:00

**변경 내용:**
- `app/services/watchlist_screener.py`: 파일 JSON 영속 CRUD, 스크리너 필터 순수함수, 알림 dry-run 평가 4종. 금지 import 없음.
- `app/ui/views/watchlist.py`: Streamlit 3탭 뷰 — 워치리스트 CRUD, 스크리너(필터+결과), 알림 dry-run. 주문 경로 없음.
- `app/ui/autofolio_app.py`: watchlist 페이지 인텔리전스 그룹에 추가.
- `tests/unit/test_watchlist_screener_service.py`: 44 테스트 (영속 4, 필터 13, 알림 21, no-order AST 1).
- `tests/unit/test_watchlist_view_apptest.py`: 5 테스트 (AppTest 3, 디스클레이머 1, no-order AST 1).

**검증 결과:**
- `python -m pytest tests/unit/test_watchlist_screener_service.py tests/unit/test_watchlist_view_apptest.py -v` → 43 passed (수정 후)
- `python -m pytest tests/ -q --cov=app --cov-fail-under=50` → 960 passed, 78% coverage
- `python scripts/check_agent_docs.py` → 0 error(s)
