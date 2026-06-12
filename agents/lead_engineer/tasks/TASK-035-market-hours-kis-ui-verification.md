---
type: task
id: TASK-035
status: 완료
owner: QA
assignees: [QA, KIS API Engineer, UI/UX Designer]
priority: High
difficulty: 중
est_hours: 2
est_tokens: 30000
tags: [qa, kis, ui, paper, market-hours, verification]
gate: paper-only; prod 실전 주문 전환 금지
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-12-010
created: 2026-06-12
created_at: 2026-06-12T12:44:22+09:00
updated_at: 2026-06-12T21:34:23+09:00
---

# TASK-035 Market-Hours KIS/UI Verification

작업 ID: TASK-035
상태: 완료
Owner: QA
요청 시각: 2026-06-12T12:40:00+09:00
기록 시각: 2026-06-12T12:44:22+09:00

## 배경 및 목적

Owner 요청은 정규장 동안만 직접 확인 가능한 UI + KIS paper 동작을 최대한 검증하고,
그 결과를 task/test/verification 기록으로 남기는 것이다. 실전 투자 전환은 명시
승인 전까지 금지한다.

## 범위

- 포함: Streamlit UI health, UI backend read-only functions, KIS paper read-only
  endpoints, KIS paper WebSocket smoke, paper order limit-place/status/cancel smoke,
  paper engine dry-run one-shot.
- 제외: prod 실전 주문, prod 환경 전환, 대량 paper 주문 반복, KIS secret/account
  value 기록.

## 검증 케이스

- QA catalog: `agents/qa/test_cases/MARKET-HOURS-KIS-UI-VERIFICATION.md`

## 진행 기록

### 2026-06-12T12:44:22+09:00

- 시장시간 검증 자체를 TASK-035로 등록.
- 재실행 가능한 QA checklist를 별도 test-case catalog로 보관.
- 현재 즉시 가능한 검증은 실행하고, 시간 조건이 아직 오지 않은 장마감 경계
  검증은 이 TASK에 남긴다.

### 2026-06-12T12:56:47+09:00

- Streamlit UI HTTP health 200 확인 및 Windows browser open 성공.
- KIS paper read-only summary 12/12 통과.
- UI backend read-only summary 10/10 통과.
- KIS paper WebSocket smoke에서 system/system/realtime quote 이벤트 3건 수신.
- `python scripts/kis_paper_order_smoke.py --symbol 005930 --qty 1`로 paper 주문
  접수/조회/취소 통과. 체결 수량은 0.
- `python scripts/run_paper_engine.py --dry-run --once`로 no-prod dry-run 실행:
  processed 2, executed 0, errors 0, kill switch blocked.
- UI/KIS focused regression 84 passed.
- generated scenario regression 119 passed.
- KIS paper post-order today-orders summary에서 open-like count 0 확인.

### 2026-06-12T13:02:29+09:00

- Owner 질문("장 마감까지 2시간 남았는데, 그러면 그동안 할 건 없어?")에 따라
  장중 soak 검증을 TASK-035 하위 실행으로 추가.
- 새 구현 없이 verification 범위만 확장:
  - repeated KIS read-only sampling
  - longer KIS WebSocket smoke
  - repeated UI backend read-only sampling
  - multiple-symbol paper limit-cancel smoke
  - engine dry-run timer loop

### 2026-06-12T13:09:36+09:00

- 장중 soak 추가 실행 완료.
- KIS read-only + UI backend repeated sampling: 3/3 iterations passed.
- KIS WebSocket longer smoke: 25 events received
  (`KisWsSystemMessage` 3, `KisRealtimeQuote` 10, `KisRealtimeTrade` 12).
- Multi-symbol paper order lifecycle:
  - `069500` below-market limit place/status/cancel OK, filled 0.
  - `000660` below-market limit place/status/cancel OK, filled 0.
  - post-check today orders open-like count 0.
- Engine dry-run repeated ticks:
  - controlled timer loop observed 3 run ends with no live paper order sent.
  - clean-exit confirmation via `--dry-run --once` repeated 3 times, all succeeded.

### 2026-06-12T15:17:46+09:00

- 15:15-15:20 close-window 검증 실행.
- `python scripts/run_paper_engine.py --dry-run --once`
  - run at 15:16:01 KST.
  - `in_window=True`.
  - processed 2, executed 0, errors 0.
  - kill switch rejected both candidate conditions.
- `python scripts/analyze_paper_transactions.py --kis-retries 5 --kis-retry-sleep 3`
  - paper_only true, KIS available true, no_open_like true.
  - KIS today orders 53, UI holdings rows 11, order logs 34, recent fills 20.
- 남은 항목: after 15:30 after-close behavior.

### 2026-06-12T21:34:23+09:00

- after 15:30 after-close 검증 실행.
- `python scripts/run_paper_engine.py --dry-run --once`
  - run at 15:53:06 KST.
  - `in_window=False`를 정확히 인식.
  - dry-run 설계상 장외에도 `engine.run_once()` path를 실행해 import/config/kill-switch 경로를 검증.
  - processed 2, executed 0, errors 0.
  - kill switch rejected both candidate conditions.
- `python scripts/analyze_paper_transactions.py --kis-retries 5 --kis-retry-sleep 3`
  - paper_only true, KIS available true, no_open_like true.
  - DB order rows 34, execution rows 22.
  - KIS today orders 53, open-like 0.
  - UI holdings rows 11, order logs 34, recent fills 20.
- `python scripts/verify_paper_ui_sync.py`
  - ok true.
  - portfolio contains_holdings true.
  - portfolio metrics include `평가금액 합`, `총 매입금액`, `총수익률`, `보유 종목`.
- `http://127.0.0.1:8502/portfolio` latest Streamlit browser verification:
  - live caption visible.
  - portfolio header, `보유 현황`, `평가금액 합`, `총 매입금액`, `평가손익`, `총수익률`, `보유 종목` visible.
  - paper holdings count visible as 11.
- TASK-035 시간 의존 verification 완료.

## 완료 기록

완료 시각: 2026-06-12T21:34:23+09:00
검토자: QA + KIS API Engineer + UI/UX Designer (Codex self-review)
감사 로그: AUDIT-2026-06-12-010, AUDIT-2026-06-12-013
실측 비용 (시간): 약 0.6h
실측 비용 (LLM 토큰): unknown

- 원 요청: 장중에 가능한 UI + KIS 검증을 task/test/verification으로 기록하고 실행.
- 실제 작업: TASK-035와 QA market-hours catalog 등록, UI/KIS/WebSocket/paper order/engine dry-run/자동화 회귀 실행.
- 결과: 즉시 실행 가능한 장중 검증, close-window 검증, after-close 검증 모두 통과.
- 남은 항목: 없음. prod 실전 주문은 별도 Owner 명시 승인 전 금지.
- 최종 상태: 완료.

## 증거

- `agents/research_agent/notes/EVIDENCE-2026-06-12-005-market-hours-kis-ui-verification.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-12-005.md`
- `agents/qa/test_cases/MARKET-HOURS-KIS-UI-VERIFICATION.md`

## 리뷰

- paper endpoint만 사용했고 prod 전환은 하지 않았다.
- paper order smoke는 below-market limit order + cancel 기본 경로만 사용했다.
- 계좌번호, token, app key, app secret, 현금 금액은 기록하지 않았다.
- in-app browser automation bootstrap은 로컬 도구 sandbox 오류로 실패했지만,
  Windows browser open과 HTTP health가 통과해 Autofolio UI 검증은 계속 진행했다.

## Done When

- Streamlit UI가 HTTP 200으로 응답한다.
- UI backend 조회 함수가 paper/mock fallback을 포함해 예외 없이 summary를 반환한다.
- KIS paper read-only API가 현재가/배치/분봉/지수/업종/호가/공시/계좌 요약 조회를
  성공한다.
- KIS paper 주문 lifecycle smoke가 paper endpoint에서 place/status/cancel을 통과한다.
- `run_paper_engine.py --dry-run --once`가 no-prod 상태에서 실행된다.
- KIS WebSocket smoke는 성공하거나, 외부/환경 실패면 재현 가능한 증거와 follow-up으로
  남긴다.
- 15:20 close-window 및 15:30 after-close boundary는 확인 완료.

## Verification

- `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8501/`
- KIS paper read-only summary script
- UI backend read-only summary script
- KIS paper WebSocket smoke script
- `python scripts/kis_paper_order_smoke.py --symbol 005930 --qty 1`
- `python scripts/run_paper_engine.py --dry-run --once`
- final docs/task gates
