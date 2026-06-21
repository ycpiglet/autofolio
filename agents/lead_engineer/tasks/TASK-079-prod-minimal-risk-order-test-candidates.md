---
type: task
id: TASK-079
display_id: TASK-079
task_uid: 87c15e3e-c7d6-4d40-8bd0-f5f63dc07052
registered_at: 2026-06-18T14:14:57+09:00
created_at: 2026-06-18T14:14:57+09:00
started_at: 2026-06-18T14:14:57+09:00
updated_at: 2026-06-18T14:14:57+09:00
completed_at: 2026-06-18T14:14:57+09:00
status: 완료
owner: Research Agent
assignees: [Research Agent, QA, KIS API Engineer, Lead Engineer]
priority: High
difficulty: 낮
est_hours: 1
est_tokens: 15000
tags: [research, kis, prod-readiness, paper, risk-minimization]
gate: research only; no prod order, no paper order, no code path mutation
trigger_meeting: Owner direct request 2026-06-18
audit_log: AUDIT-2026-06-18-005
created: 2026-06-18
---

# TASK-079 Prod minimal-risk order test candidates

작업 ID: TASK-079
상태: 완료
Owner: Research Agent
요청 시각: 2026-06-18T14:14:57+09:00
기록 시각: 2026-06-18T14:14:57+09:00
완료 시각: 2026-06-18T14:14:57+09:00
요청자: Owner
수행자: Research Agent, QA, KIS API Engineer, Lead Engineer
검토자: Research Agent self-review + QA perspective + KIS API Engineer perspective
협업 waiver(사유): 단일 세션 범위. 실전 주문을 실행하지 않는 조사/테스트 설계이며, 공식 문서와 KIS read-only live checks로 보완했다.
실측 비용 (시간): 약 20분
실측 비용 (LLM 토큰): Codex session local meter unavailable
의도: 실전 계좌 1주 수동 주문 테스트의 현금 리스크를 최소화할 수 있는 저가 후보와 테스트 케이스를 정리한다.
대상: KIS paper/prod read-only 후보 조회, 공식 Open API/거래 안내, evidence note
방법: 외부 공식/시장 자료로 거래 단위와 소수점 지원 범위를 확인하고, 후보 종목은 KIS paper/prod 현재가·호가·paper 매수가능조회 shape만 확인한다.
감사 로그: AUDIT-2026-06-18-005
routing_ref: direct-owner-request / TASK-079
selected_model: Codex coding agent
policy_model: AGENTS.md §16 Autofolio R3 Surface

## 범위

포함:

- 1주 주문금액이 낮은 국내 KRX 후보군 조사.
- paper/prod read-only 현재가와 호가 조회 확인.
- paper 매수가능조회 shape 확인.
- 실전 1주 테스트 절차 제안.

제외:

- 실전 주문, 실전 취소, 실전 자동매매 ON.
- paper 주문 실행.
- 레버리지/신용/공매도/파생/해외/FX 주문 설계.
- secret, token, account, cash amount 기록.

## 완료 조건

- [x] 저가 후보군과 제외 후보 기준이 명시된다.
- [x] KIS paper/prod read-only 조회 결과가 기록된다.
- [x] 모의계좌와 실전계좌 모두에서 재사용 가능한 테스트 케이스가 작성된다.
- [x] prod 실전 주문은 별도 Owner 승인 전까지 미실행으로 남긴다.

## 완료 내용

수행:

- 한국투자증권 공식 Open API 안내, KIS Developers/Open API 샘플 repo, 미니스탁 안내, 호가단위 자료를 확인했다.
- 후보 14개에 대해 KIS paper/prod 현재가와 10단계 호가 read-only 조회를 실행했다.
- 후보 14개에 대해 KIS paper 매수가능조회 shape를 확인했다.
- 실전 1주 테스트용 primary/secondary/excluded 후보와 테스트 순서를 정리했다.

결과:

- 실전 테스트는 소수점 매매보다 국내 1주 저가 종목이 현실적이다.
- 한국투자 공식 미니스탁 안내는 미국주식 천원 단위 소수점 서비스를 말하고, 국내주식 Open API 주문은 국내주식/ETF/ETN 정수 주문 카테고리로 봐야 한다.
- live 후보 중 현금 리스크를 최소화하려면 300~900원대 보통주/리츠 1주가 적합하다.

검증:

- KIS paper/prod 현재가+호가 read-only 후보 조회 -> 14/14 조회 가능.
- KIS paper 매수가능조회 shape -> 14/14 shape OK.

## 증거

- `agents/research_agent/notes/EVIDENCE-2026-06-18-003-prod-minimal-risk-order-candidates.md`

## 리뷰

- Research Agent review: 공식/시장 자료와 live KIS read-only 결과를 분리했다.
- QA review: 후보를 paper-first 절차와 prod 1주 절차로 테스트 케이스화했다.
- KIS API Engineer review: 주문 실행 전 비파괴 조회만 사용했고, 실전 주문/취소는 별도 R3 승인 대상으로 유지했다.

## Independent Audit

판정: 통과

근거:

- 실전 주문은 실행하지 않았다.
- 후보 검증은 read-only 현재가/호가/매수가능 shape만 사용했다.
- 레버리지/2X/ETN/소수점 자동화는 실전 1주 smoke 후보에서 제외했다.
