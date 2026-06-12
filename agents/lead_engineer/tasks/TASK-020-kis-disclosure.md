---
type: task
id: TASK-020
status: 완료
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Low
difficulty: 중
est_hours: 3
est_tokens: 50000
tags: [kis, disclosure, compliance]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
---

# TASK-020 KIS 공시 정보 조회

작업 ID: TASK-020
상태: 완료
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00
완료 시각: 2026-06-12T08:38:31+09:00

## 배경 및 목적

상장사 공시(유상증자, 분기보고서, 감사의견 등)는 매매 판단에 중요한 영향을 미친다. 공시 발생 시 Compliance Agent가 해당 종목의 주문을 일시 차단하거나 경고를 발송하면 리스크를 줄일 수 있다.

## 구현 범위

- KIS 공시 API 연동 (`inquire-disclosure` 또는 유사 엔드포인트)
- `KisClient.get_disclosures(symbol, days=1)` 구현
- 공시 유형 분류 (정기공시, 수시공시, 주요사항보고서)
- Compliance Agent 게이트: 중대 공시 발생 시 주문 차단 플래그 설정
- 알림 탭 또는 Telegram 공시 알림 발송

## 완료 기준

- [x] `get_disclosures()` 구현 및 단위 테스트
- [x] Compliance Agent 공시 차단 게이트 연동 확인
- [x] 공시 발생 시 Notifier 발송 smoke 테스트

## 완료 기록

- 원 요청: KIS 공시성 조회를 연결하고, 중대 공시 발생 시 Compliance 경고/차단 플래그와 알림 경로를 제공한다.
- 공식 정본 확인:
  - `inquire-disclosure` 샘플은 공식 repo에 없고, `news_title` 샘플이 "종합 시황/공시(제목) [국내주식-141]"로 제공된다.
  - endpoint: `/uapi/domestic-stock/v1/quotations/news-title`
  - TR: `FHKST01011800`
- 실제 작업:
  - `KisClient.get_disclosures(symbol, days=1)` 추가.
  - `classify_disclosure_title()`로 정기공시/수시공시/주요사항보고서/뉴스·기타 분류.
  - 유상증자, 감자, 합병, 거래정지, 상장폐지, 감사의견, 횡령, 배임 등 중대 키워드는 `block_order=True`로 분류.
  - `backend.disclosures_df()`, `refresh_disclosure_gate()`, `disclosure_gate_state()` 추가.
  - DB schema 변경 없이 `system_state`에 `compliance_disclosure_block:{symbol}`와 사유를 저장.
  - 매매 화면은 차단 플래그가 켜진 종목의 조건 저장 버튼을 비활성화.
  - 알림 탭에 뉴스/공시 조회 패널 추가. 중대 공시 감지 시 `Notifier.send()` 경로 사용.
- R3 경계:
  - `order_flow.py`, `app/risk/**`, DB schema/migration은 변경하지 않았다.
  - 실제 주문 차단을 엔진/리스크 계층에 강제하는 작업은 Autofolio R3 surface로 별도 Owner 승인 필요.
- 변경 파일:
  - `app/brokers/kis/kis_client.py`
  - `app/ui/backend.py`
  - `app/ui/views/trade.py`
  - `app/ui/views/alerts.py`
  - `tests/unit/test_kis_disclosures.py`
  - `tests/unit/test_backend_disclosures.py`
  - `tests/unit/test_alerts_disclosure_view.py`
  - `tests/unit/test_trade_order_book_view.py`
  - `docs/KIS_API_SPEC.md`
  - `docs/references/kis/PROJECT-MAPPING.md`
  - `docs/BACKLOG.md`
- 검증:
  - `python -m py_compile app\brokers\kis\kis_client.py app\ui\backend.py app\ui\views\trade.py app\ui\views\alerts.py tests\unit\test_kis_disclosures.py tests\unit\test_backend_disclosures.py tests\unit\test_alerts_disclosure_view.py tests\unit\test_trade_order_book_view.py` — 통과
  - `pytest tests\unit\test_kis_disclosures.py tests\unit\test_backend_disclosures.py tests\unit\test_alerts_disclosure_view.py tests\unit\test_trade_order_book_view.py` — 11 passed
  - `pytest tests\unit\test_kis_disclosures.py tests\unit\test_backend_disclosures.py tests\unit\test_alerts_disclosure_view.py tests\unit\test_trade_order_book_view.py tests\unit\test_kis_order_book.py tests\unit\test_backend_order_book.py` — 19 passed
  - `pytest tests` — 366 passed
  - `python scripts\validate_task_schema.py` — OK
  - `python scripts\generate_views.py --check` — OK
  - `python scripts\check_agent_docs.py` — OK, 0 errors / 124 warnings
