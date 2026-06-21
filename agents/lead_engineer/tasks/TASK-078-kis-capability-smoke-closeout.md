---
type: task
id: TASK-078
display_id: TASK-078
task_uid: f19095da-c858-4eed-8497-b5a10b5ae0f5
registered_at: 2026-06-18T12:45:44+09:00
created_at: 2026-06-18T12:45:44+09:00
started_at: 2026-06-18T12:45:44+09:00
updated_at: 2026-06-18T13:04:27+09:00
completed_at: 2026-06-18T13:04:27+09:00
status: 완료
owner: QA
assignees: [QA, KIS API Engineer, Lead Engineer]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 20000
tags: [qa, kis, paper, prod-readonly, smoke]
gate: prod limited to redacted read-only capability checks; paper order lifecycle optional and paper-only
trigger_meeting: Owner direct request 2026-06-18
audit_log: AUDIT-2026-06-18-004
created: 2026-06-18
---

# TASK-078 KIS capability smoke closeout

작업 ID: TASK-078
상태: 완료
Owner: QA
요청 시각: 2026-06-18T12:45:44+09:00
기록 시각: 2026-06-18T12:45:44+09:00
완료 시각: 2026-06-18T13:04:27+09:00
요청자: Owner
수행자: QA, KIS API Engineer, Lead Engineer
검토자: QA self-review + KIS API Engineer perspective + Lead Engineer self-review
협업 waiver(사유): 단일 세션 범위. 단일 Codex 세션에서 QA/KIS API/Lead Engineer 관점을 순차 적용했다. 외부 모델/인간 reviewer는 호출하지 않았고, High-priority self-review 한계는 evidence/BRIEF와 live KIS paper/prod-read-only smoke, focused unit tests로 보완했다.
실측 비용 (시간): 약 1시간
실측 비용 (LLM 토큰): Codex session local meter unavailable
의도: TASK-075에서 통과한 KIS paper/prod-read-only 검증을 한 번에 재실행 가능한 redacted capability smoke로 보강하고, paper cancel 확인의 즉시 재조회 흔들림을 줄인다.
대상: `scripts/kis_capability_smoke.py`, `scripts/kis_paper_order_smoke.py`, focused unit tests, evidence/BRIEF 기록
방법: prod는 읽기 전용으로만 검사하고, paper 주문 생애주기는 paper endpoint 가드와 계좌 masking을 유지한 채 cancel confirmation을 강화한다.
감사 로그: AUDIT-2026-06-18-004
routing_ref: direct-owner-request / TASK-078
selected_model: Codex coding agent
policy_model: AGENTS.md §16 Autofolio R3 Surface

## 범위

포함:

- KIS paper/prod-read-only capability smoke 스크립트 추가.
- secret/token/account/cash/raw response를 출력하지 않는 redacted JSON/콘솔 결과.
- paper 주문 취소 이후 direct status와 today-orders open-like 잔존 확인.
- focused unit tests와 live smoke evidence 기록.

제외:

- prod 주문, prod 취소, prod 자동매매 ON.
- 레버리지, 신용, 공매도, 해외/FX/환전, 실전 주문 실사용.
- secret, token, account, cash amount, raw broker response 기록.
- DB schema/migration, CI workflow, production deployment.

## 완료 조건

- [x] redacted KIS capability smoke가 paper/prod-read-only를 한 명령으로 확인한다.
- [x] paper cancel smoke가 direct status와 today-orders open-like 잔존 여부를 함께 보고한다.
- [x] focused unit tests와 가능한 live smoke가 통과한다.
- [x] TASK/evidence/BRIEF/STATUS/AUDIT/뷰가 갱신된다.

## 완료 기록

원 요청:

- KIS/KSI 기능 테스트 결과 중 더 추가하거나 개선해야 할 것이 남았는지 확인.
- 가능한 남은 개선을 전부 진행하고 마무리.

## 완료 내용

수행:

- `scripts/kis_capability_smoke.py` 추가. paper/prod read-only core/deep capability를 redacted JSON 또는 text로 확인한다.
- `scripts/kis_paper_order_smoke.py`에 cancel confirmation 추가. 직접 status와 same-ODNO today-orders open-like count를 함께 본다.
- `README.md` 스크립트 목록 갱신.
- focused unit tests 추가/보강.
- evidence/BRIEF 작성.

변경 파일:

- `README.md`
- `scripts/kis_capability_smoke.py`
- `scripts/kis_paper_order_smoke.py`
- `tests/unit/test_kis_capability_smoke.py`
- `tests/unit/test_kis_paper_order_smoke.py`
- `agents/research_agent/notes/EVIDENCE-2026-06-18-002-kis-capability-smoke-closeout.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-18-002.md`
- `agents/lead_engineer/tasks/TASK-078-kis-capability-smoke-closeout.md`

검증:

- `.venv\Scripts\python.exe -m pytest tests\unit\test_kis_paper_order_smoke.py tests\unit\test_kis_capability_smoke.py -q` -> 10 passed.
- `.venv\Scripts\python.exe -m py_compile scripts\kis_capability_smoke.py scripts\kis_paper_order_smoke.py` -> pass.
- `.venv\Scripts\python.exe scripts\kis_capability_smoke.py --env both --json --request-timeout 10 --max-retries 1` -> pass.
- `.venv\Scripts\python.exe scripts\kis_capability_smoke.py --env both --deep --json --request-timeout 10 --max-retries 1` -> pass.
- `.venv\Scripts\python.exe scripts\kis_paper_order_smoke.py --symbol 005930 --qty 1 --cancel-poll-attempts 3 --cancel-poll-sleep 1` -> pass.

결과:

- TASK-078 완료. KIS paper/prod-read-only 기능은 core/deep smoke 기준 통과했다.
- prod 주문/취소/자동매매/레버리지/신용/해외/FX/파생은 실행하지 않았다.
- paper cancel direct status lag는 remaining open-like count 0 확인으로 closeout했다.

남은 watch:

- KIS paper endpoint는 5초 timeout 조건에서 일시 실패했으므로, 기본 smoke는 10초 timeout과 1회 retry를 사용한다.
- prod 실주문 readiness는 이번 범위 밖이며 별도 R3 Owner 승인 전에는 실행하지 않는다.

## 증거

- `agents/research_agent/notes/EVIDENCE-2026-06-18-002-kis-capability-smoke-closeout.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-18-002.md`

## 리뷰

- QA review: focused unit tests와 live KIS core/deep smoke를 실행했고, prod는 read-only 경계로 제한했다.
- KIS API Engineer review: paper/prod capability 표면을 redacted shape/count/boolean 출력으로 검증했고, token/account/cash/raw payload는 기록하지 않았다.
- Lead Engineer review: TASK-075 watch였던 paper cancel direct-status lag를 same-ODNO open-like count 확인으로 닫았고, prod 실주문 readiness는 R3 후속으로 분리했다.

## Independent Audit

판정: 통과

근거:

- core/deep capability smoke가 paper/prod-read-only에서 통과했다.
- paper order lifecycle은 paper endpoint guard와 account masking을 유지했고, cancel 확인은 open-like 0으로 보강됐다.
- prod 주문/취소/자동매매/레버리지/신용/해외/FX/파생 경로는 실행하지 않았다.
- evidence/BRIEF/STATUS/AUDIT와 generated views가 갱신됐다.
