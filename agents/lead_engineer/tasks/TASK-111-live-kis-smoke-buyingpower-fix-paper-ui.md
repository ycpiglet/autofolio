---
type: task
id: TASK-111
display_id: TASK-111
task_uid: 7c4e9b21-3a85-4f60-9d12-6b0e2a7c1f44
registered_at: 2026-06-19T17:29:42+09:00
created_at: 2026-06-19T17:29:42+09:00
started_at: 2026-06-19T13:00:00+09:00
updated_at: 2026-06-19T17:29:42+09:00
completed_at: 2026-06-19T17:29:42+09:00
status: 완료
owner: Lead Engineer
assignees: [Lead Engineer, KIS API Engineer, QA, UI/UX Designer]
priority: High
difficulty: 상
est_hours: 4
est_tokens: 180000
tags: [kis, prod, paper, live-smoke, buying-power, bugfix, ui, playwright]
gate: Owner explicitly requested live test during regular session; hard caps (≤5주·≤5,000원) + auto-cleanup; no risk-gate weakening; no secret output
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-111
created: 2026-06-19
---

# TASK-111 실계좌 최소 스모크 + 매수가능수량 버그수정 + 모의 UI 워크스루

작업 ID: TASK-111
상태: 완료
Owner: Lead Engineer
요청자: Owner
요청 시각: 2026-06-19T13:00:00+09:00
완료 시각: 2026-06-19T17:29:42+09:00
수행자: Lead Engineer, KIS API Engineer, QA, UI/UX Designer
의도: 정규장 중 모의→실계좌 최소 주문 경로와 UI 매매 흐름을 실제로 검증한다.

## 범위

포함:
- 모의 스모크 대본 복구(다른 세션이 빼먹은 헬퍼 `_is_open_like_order`/`_mask_account` 복원).
- 매수가능수량 필드 버그 수정 + 회귀 테스트.
- 실계좌(prod) 최소 주문 라이프사이클 검증(매수→매도→지정가취소→delta 0).
- 모의(paper) 전용 인스턴스에서 UI 직접 조작(로그인→조건등록→새로고침 지속) 검증.

제외:
- 자동매매 ON, risk gate 약화, secret/account/raw payload 기록.
- 저가 종목 모의 주문(모의 유니버스 매매불가).

## 완료 내용

수행:
- `scripts/kis_paper_order_smoke.py`: 누락된 `_is_open_like_order`(KIS 당일주문 open/pending 판정, kis_client 의미와 일치)와 `_mask_account`(계좌 마스킹) 추가 → 깨진 스모크 대본 복구.
- `app/brokers/kis/kis_client.py` `get_buying_power`: `psbl_qty`만 읽던 것을 `psbl_qty → nrcvb_buy_qty → max_buy_qty` fallback으로 수정. 모의 응답엔 `psbl_qty`가 없어 항상 0 → 모든 매수 차단되던 실버그.
- `tests/unit/test_kis_buying_power.py`: psbl_qty 부재 시 fallback 회귀 테스트 추가.
- `scripts/pp.py`: 터미널 줄바꿈 회피용 짧은 prod 스모크 래퍼(기본 읽기전용, `EXECUTE-REAL` 토큰 시에만 실주문).
- 실계좌 최소 주문 실행: `004870 티웨이홀딩스` 시장가 5주 매수→5주 매도→1주 below-market 지정가 매수→취소.
- 모의 UI 검증: paper 전용 백엔드(8009, 격리 DB) + 프로덕션 프런트(3009)를 띄우고 Playwright로 로그인→`005930` 조건등록→새로고침 지속 확인.

결과(검증):
- `python -m pytest tests/unit/test_kis_buying_power.py tests/unit/test_kis_minimal_order_smoke.py -q` → 10 passed.
- 모의 주문 경로(005930 대형주): 시장가 매수/매도 체결, 포지션 delta 0 → PASS.
- 실계좌 스모크(`prod_minimal_smoke_20260619T130935+0900.json`): overall_status **pass**, 매수 FILLED(5), 매도 FILLED(5, final delta 0), 지정가 CANCELED, final_position_qty 0, open_like_total 0.
- 모의 UI: 로그인(owner) → 프로필 게이트(미완료시 차단/완료시 활성) → 조건 등록 "조건이 등록되었습니다" → 새로고침 후 `삼성전자(005930) BUY 50000 1 ACTIVE` 지속. 스크린샷 `ui-paper-trade-condition.png`.

## 발견 / 학습
- 모의(모의투자) 서버는 **대형주 위주 제한 유니버스** — 저가 소형주·리츠(004870/145270 등)는 모의에서 `40070000 매매불가`. 저가 화이트리스트로는 모의 PASS 불가(설계 한계).
- 모의서버 간헐 timeout + 토큰 발급 1분/회 제한(EGW00133).
- Next.js `rewrites` 프록시 대상은 **빌드 시점 고정** → `API_INTERNAL_URL`을 빌드에 넣어야 함.
- dev 모드는 헤드리스/프록시 브라우저에서 HMR 웹소켓 실패로 하이드레이션이 깨짐 → **프로덕션 빌드로 검증**(메모리 playwright-prod-mode-verify와 일치).
- `scripts/now.py`가 OS 실제 시각과 어긋남(약 -12h) → 시각은 OS 클럭 기준.

## 증거
- `.autofolio/kis_smoke/prod_minimal_smoke_20260619T130935+0900.json` (실계좌 PASS)
- `ui-paper-trade-condition.png` (모의 UI 조건등록)

## Independent Audit
판정: 통과
- 실계좌 잔여 포지션/열린 주문 0, secret/account/raw payload 미기록.
- 하드캡(≤5주·≤5,000원)과 자동청산 유지, risk gate 변경 없음.
- 버그수정은 회귀 테스트로 고정.
