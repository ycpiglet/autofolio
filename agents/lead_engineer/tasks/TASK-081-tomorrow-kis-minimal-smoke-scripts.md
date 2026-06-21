---
type: task
id: TASK-081
display_id: TASK-081
task_uid: ada2ecad-0ded-4646-8cff-da463247155f
registered_at: 2026-06-18T15:05:34+09:00
created_at: 2026-06-18T15:05:34+09:00
started_at: 2026-06-18T15:05:34+09:00
updated_at: 2026-06-18T15:05:34+09:00
completed_at: 2026-06-18T15:05:34+09:00
status: 완료
owner: Lead Engineer
assignees: [Lead Engineer, QA, KIS API Engineer]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 12000
tags: [kis, paper, prod, live-smoke, tomorrow-runbook]
gate: code/write records only; no live order executed in this task; prod runner requires same-day paper pass and explicit real-order flag
trigger_meeting: Owner direct request 2026-06-18
audit_log: AUDIT-2026-06-18-007
created: 2026-06-18
---

# TASK-081 Tomorrow KIS minimal smoke scripts

작업 ID: TASK-081
상태: 완료
Owner: Lead Engineer
요청 시각: 2026-06-18T14:56:07+09:00
기록 시각: 2026-06-18T15:05:34+09:00
완료 시각: 2026-06-18T15:05:34+09:00
요청자: Owner
수행자: Lead Engineer, QA, KIS API Engineer
검토자: Lead Engineer self-review + QA perspective + KIS API Engineer perspective
협업 waiver(사유): 내일 정규장 전 실행 준비를 위한 단일 세션 scoped script 작업. 실주문은 실행하지 않고 unit/dry-run으로 검증했다.
협업 waiver: single-session scope with no live-order execution.
실측 비용 (시간): 약 20분
실측 비용 (LLM 토큰): Codex session local meter unavailable
의도: 내일 정규장 시작 직후 paper 먼저, 그 결과를 기반으로 prod 최소 스모크를 바로 실행할 수 있게 한다.
대상: `scripts/kis_minimal_order_smoke.py`, paper/prod wrapper, unit tests, README, handoff pointer
방법: 공통 runner + env-locked paper/prod entrypoints + same-day paper evidence gate + explicit prod real-order flag
감사 로그: AUDIT-2026-06-18-007
routing_ref: direct-owner-request / TASK-081
selected_model: Codex coding agent
policy_model: AGENTS.md §16 Autofolio R3 Surface, no live order in this task

## 범위

포함:

- paper 버전: `scripts/kis_paper_minimal_live_smoke.py`
- prod 버전: `scripts/kis_prod_minimal_live_smoke.py`
- 공통 로직: 후보선정, 정규장/날짜 guard, 매수→매도→지정가취소, open-like 잔여 확인, local result 저장
- prod guard: same-day paper pass evidence, env lock, explicit `--i-understand-this-places-real-orders`
- README 주요 스크립트 갱신

제외:

- 오늘 live 주문 실행.
- 자동매매 ON.
- risk gate 약화, secret/account/cash/raw broker payload 기록.
- 레버리지/인버스/ETN/ELW/신용/공매도/해외/FX/소수점 주문.

## 완료 조건

- [x] paper 전용 스크립트가 직접 실행 가능한 entrypoint로 존재한다.
- [x] prod 전용 스크립트가 paper pass 증거 없이는 실주문하지 않는다.
- [x] prod 실행은 명시 플래그 없이는 막힌다.
- [x] 실패한 paper dry-run은 `latest_paper.json`으로 승격되지 않는다.
- [x] 내일 실행 명령이 evidence에 남는다.

## 완료 내용

수행:

- `scripts/kis_minimal_order_smoke.py` 공통 runner를 추가했다.
- `scripts/kis_paper_minimal_live_smoke.py`와 `scripts/kis_prod_minimal_live_smoke.py`를 env-locked wrapper로 추가했다.
- paper pass+execute 결과만 `.autofolio/kis_smoke/latest_paper.json`으로 승격되게 했다.
- prod는 기본적으로 latest paper evidence를 요구하고, `--execute --i-understand-this-places-real-orders` 없이는 실주문하지 않는다.
- `tests/unit/test_kis_minimal_order_smoke.py`를 추가했다.
- README와 NEXT-SESSION-POINTER를 내일 실행 순서에 맞게 갱신했다.

결과:

- 내일 2026-06-19 정규장에는 paper 실행 후 같은 종목 기반 prod dry-run, 그다음 prod execute 순서로 진행하면 된다.
- 현재 시간대 paper endpoint는 timeout이 반복되어 read-only dry-run이 blocked였지만, blocked/dry-run 결과는 latest paper evidence로 승격되지 않는다.
- prod read-only dry-run은 `004870` 후보선정까지 통과했다.

검증:

- `.venv\Scripts\python.exe -m pytest tests\unit\test_kis_minimal_order_smoke.py -q` -> 7 passed.
- `.venv\Scripts\python.exe -m py_compile scripts\kis_minimal_order_smoke.py scripts\kis_paper_minimal_live_smoke.py scripts\kis_prod_minimal_live_smoke.py tests\unit\test_kis_minimal_order_smoke.py` -> pass.
- paper/prod wrapper `--help` -> pass.
- prod read-only dry-run with `--no-require-paper-evidence` -> dry-run, selected `004870`, no order.
- paper read-only dry-run after 15:00 with short timeout -> blocked due KIS paper endpoint timeouts; diagnostic candidate list printed; no latest paper promotion.

## 내일 실행 순서

1. Paper 실행:

```powershell
.venv\Scripts\python.exe scripts\kis_paper_minimal_live_smoke.py --expected-date 2026-06-19 --execute --request-timeout 15 --max-retries 1
```

2. Prod read-only plan 확인:

```powershell
.venv\Scripts\python.exe scripts\kis_prod_minimal_live_smoke.py --expected-date 2026-06-19
```

3. Prod 최소 실주문 실행:

```powershell
.venv\Scripts\python.exe scripts\kis_prod_minimal_live_smoke.py --expected-date 2026-06-19 --execute --i-understand-this-places-real-orders
```

## 증거

- `agents/research_agent/notes/EVIDENCE-2026-06-18-005-tomorrow-kis-minimal-smoke-scripts.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-18-005.md`

## 리뷰

- Lead Engineer review: prod script는 같은 날 paper pass와 명시 플래그가 있어야 실주문한다.
- QA review: unit tests가 날짜 guard, whitelist, qty/notional cap, prod confirmation, latest promotion 조건을 고정했다.
- KIS API Engineer review: today-orders open-like probe와 position delta cleanup을 공통화했다.

## Independent Audit

판정: 통과

근거:

- 이 TASK에서는 실주문을 실행하지 않았다.
- prod 실행은 paper evidence와 명시 플래그 없이는 막힌다.
- 실패한 paper 실행은 prod 근거 파일로 승격되지 않는다.
