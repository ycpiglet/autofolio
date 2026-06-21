---
type: task
id: TASK-080
display_id: TASK-080
task_uid: 1e1263f0-0fb6-435e-b338-22ec4d8cf4f5
registered_at: 2026-06-18T14:47:04+09:00
created_at: 2026-06-18T14:47:04+09:00
started_at: 2026-06-18T14:47:04+09:00
updated_at: 2026-06-18T14:47:04+09:00
completed_at: 2026-06-18T14:47:04+09:00
status: 완료
owner: Lead Engineer
assignees: [Lead Engineer, QA, KIS API Engineer]
priority: Critical
difficulty: 중
est_hours: 1
est_tokens: 12000
tags: [kis, prod, live-smoke, order-lifecycle, risk-minimization]
gate: Owner explicitly approved minimal prod live smoke; no auto-trading, no risk-gate weakening, no secret output
trigger_meeting: Owner direct request 2026-06-18
audit_log: AUDIT-2026-06-18-006
created: 2026-06-18
---

# TASK-080 Prod minimal live smoke

작업 ID: TASK-080
상태: 완료
Owner: Lead Engineer
요청 시각: 2026-06-18T14:32:46+09:00
기록 시각: 2026-06-18T14:47:04+09:00
완료 시각: 2026-06-18T14:47:04+09:00
요청자: Owner
수행자: Lead Engineer, QA, KIS API Engineer
검토자: Lead Engineer self-review + QA perspective + KIS API Engineer perspective
협업 waiver(사유): 정규장 중 시간이 제한된 Owner-approved live smoke. 하드캡과 redaction을 코드 실행 단위에 넣고 즉시 증거화했다.
협업 waiver: single-session scope with Owner-approved live-market time constraint.
실측 비용 (시간): 약 15분
실측 비용 (LLM 토큰): Codex session local meter unavailable
의도: Owner가 입금 후 승인한 최소 금액 실계좌 주문 경로를 보통주 저가 후보로 검증한다.
대상: KIS prod domestic cash market buy/sell, prod below-market limit cancel, KIS buying-power field mapping fix
방법: 화이트리스트 후보, 5주 이하, 예상 주문금액 5,000원 이하, prod URL guard, 계좌/현금/secret redaction, 보유수량 delta 기준 청산
감사 로그: AUDIT-2026-06-18-006
routing_ref: direct-owner-request / TASK-080
selected_model: Codex coding agent
policy_model: AGENTS.md §16 Autofolio R3 Surface with explicit Owner approval

## 범위

포함:

- prod read-only 시세, 호가, 예수금 존재 여부, 매수가능수량 확인.
- `004870 티웨이홀딩스` 5주 시장가 매수 후 5주 시장가 매도.
- 같은 종목 1주 below-market 지정가 매수 주문 후 취소.
- 최종 보유수량과 당일 주문 open-like 잔여 확인.
- `KisClient.get_buying_power()` read-only 필드 fallback 버그 수정.

제외:

- 자동매매 ON.
- 전략/추천/포트폴리오 판단.
- 레버리지, 인버스, ETN/ELW, 신용, 공매도, 해외, FX, 소수점 주문.
- risk gate 약화, secret/account/cash/raw broker payload 기록.

## 완료 조건

- [x] prod 후보가 실시간 시세/호가와 매수가능 필드로 재확인된다.
- [x] 실계좌 최소 시장가 매수/매도가 체결되고 포지션 delta가 0으로 돌아온다.
- [x] 실계좌 지정가 주문 취소가 open-like 잔여 0으로 확인된다.
- [x] paper API 장애/미검증 상태가 별도 기록된다.
- [x] 발견된 read-only 매수가능수량 해석 버그가 회귀 테스트와 함께 수정된다.

## 완료 내용

수행:

- `006490`은 paper 주문에서 매매불가로 거부되어 제외했다.
- `000040`/`004870` paper 주문은 KIS paper 서버 timeout으로 접수/취소 검증이 불안정해 prod live smoke의 필수 전제에서는 watch로 기록했다.
- prod 계정은 예수금 존재, 10단계 호가, 원시 KIS `max_buy_qty`/`nrcvb_buy_qty` 매수가능수량이 확인된 `004870`을 선택했다.
- `004870` 5주 시장가 매수, 5주 시장가 매도, 1주 below-market 지정가 매수 후 취소를 수행했다.
- `get_buying_power()`가 `psbl_qty`만 보던 버그를 `max_buy_qty`/`nrcvb_buy_qty` fallback으로 수정했다.

결과:

- 시장가 매수 5주는 FILLED, open-like 0.
- 시장가 매도 5주는 FILLED, 최종 position delta 0, open-like 0.
- below-market 지정가 1주는 CANCELED, open-like 0.
- 최종 `004870` 보유수량은 0.
- paper 서버는 주문/잔고/당일주문 조회가 timeout으로 불안정했으므로 오늘 paper 주문 재확인은 미검증이다.

검증:

- prod live smoke inline run -> buy filled, sell filled, cancel confirmed, open-like 0.
- prod post-check -> selected position qty 0, selected today-order open-like count 0.
- `python -m pytest tests/unit/test_kis_buying_power.py -q` -> 3 passed.
- prod read-only `get_buying_power("004870")` after patch -> max quantity positive, cash positive.

## 증거

- `agents/research_agent/notes/EVIDENCE-2026-06-18-004-prod-minimal-live-smoke.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-18-004.md`

## 리뷰

- Lead Engineer review: Owner approval 범위를 최소 live smoke로 해석했고 자동매매·risk gate·secret·DB·CI는 변경하지 않았다.
- QA review: 매수/매도/취소 각각 terminal 상태와 open-like 0을 확인했다.
- KIS API Engineer review: KIS `inquire-psbl-order` 응답 필드 차이를 회귀 테스트로 고정했다.

## Independent Audit

판정: 통과

근거:

- 실계좌 잔여 포지션과 open-like 주문이 남지 않았다.
- 현금/계좌/토큰/raw broker payload를 기록하지 않았다.
- paper 서버 timeout으로 "paper에서도 같은 주문/취소가 되는 종목" 조건은 오늘 완전 충족되지 않았고 watch로 남긴다.
