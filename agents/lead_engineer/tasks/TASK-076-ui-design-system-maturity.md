---
type: task
id: TASK-076
display_id: TASK-076
task_uid: d8ac2ce2-8b1d-4eba-938f-f28b1c30bd55
registered_at: 2026-06-18T10:25:30+09:00
created_at: 2026-06-18T10:25:30+09:00
started_at: 2026-06-18T10:25:30+09:00
updated_at: 2026-06-18T10:56:31+09:00
completed_at: 2026-06-18T10:25:30+09:00
status: 완료
owner: Lead Engineer
assignees: [Lead Engineer, Lead Designer, UI/UX Designer, Research Agent, Doc Steward, QA]
priority: Medium
difficulty: 중
est_hours: 2
est_tokens: 30000
tags: [ui, design-system, governance, diagnostic, lead-designer, qa, token-budget]
gate: docs and advisory tooling only; no product UI, KIS, order, risk, DB schema, secret, prod, or CI workflow changes
trigger_meeting: Owner direct request 2026-06-18
audit_log: AUDIT-2026-06-18-002
created: 2026-06-18
---

# TASK-076 UI design system maturity and Lead Designer governance

작업 ID: TASK-076
상태: 완료
Owner: Lead Engineer
요청 시각: 2026-06-18T10:25:30+09:00
기록 시각: 2026-06-18T10:25:30+09:00
요청자: Owner
수행자: Lead Engineer, Lead Designer, UI/UX Designer, Research Agent, Doc Steward, QA
의도: Autofolio UI가 반복적으로 page-local 디자인을 만들지 않도록 진단 리포트, design-system rulebook, Lead Designer 역할, advisory gate를 도입한다.
대상: root `reviews/`, `docs/design-system.md`, `agents/lead_designer/SKILL.md`, `agents/roles.yml`, design-system gate script/tests, TASK/AUDIT 기록
방법: 현재 Next.js UI 구조 계측, 외부 design-system 사례 조사, rulebook 작성, role registry와 orchestrator alias 보강, warning-first static gate 추가
감사 로그: AUDIT-2026-06-18-002

## 범위

포함:

- UI design-system maturity diagnostic 작성.
- `docs/design-system.md` rulebook 작성.
- Lead Designer 역할 정의 및 registry/orchestrator 연결.
- token/component/pattern/one-off assetization 기준 정의.
- warning-first design-system static gate와 unit test 추가.
- root `reviews/INDEX.md` evidence index 갱신.

제외:

- 실제 제품 UI refactor.
- KIS, order, risk, database schema, secrets, prod, CI workflow 변경.
- Storybook 설치 또는 Figma asset 생성.
- 기존 TASK-075 live KIS beta lane 변경/종료.

## 완료 내용

- `reviews/DIAGNOSTIC-2026-06-18-ui-design-system-maturity.md`에 현재 Autofolio UI 성숙도, repo evidence, assetization 후보, 외부 methodology, role/gate 진단을 기록했다.
- `docs/design-system.md`에 token, `components/ui`, pattern/domain component, page composition 규칙과 새 디자인 proposal flow를 정의했다.
- `agents/lead_designer/SKILL.md`를 추가하고 `agents/roles.yml` 및 `scripts/agent_orchestrator.py`에 `lead-designer` alias를 등록했다.
- `scripts/design_system_gate.py`를 추가해 raw color literal, page bare controls, oversized page, repeated class cluster를 warning-first로 감지한다.
- `scripts/test_design_system_gate.py`로 gate behavior를 고정했다.
- `scripts/check_agent_docs.py`에 advisory design-system gate hook을 연결했다.

## 후속 보강: Light / Standard / Heavy-Council mode

보강 시각: 2026-06-18T10:56:31+09:00

Owner 피드백: council 형태의 제안/비판/의논 구조는 좋지만, light user와
heavy user를 나누지 않으면 토큰이 부족한 사용자의 생산성이 떨어질 수 있다.

반영:

- `docs/design-system.md`에 Adaptive Proposal Modes를 추가했다.
- Council을 기본값이 아니라 Heavy escalation으로 정의했다.
- Light mode는 한 화면/한 컴포넌트의 명확한 refactor에서 Assetization Note만
  남기고 진행하도록 했다.
- Standard mode는 보통의 재사용 UI 변경, Heavy/Council mode는 새 시각 언어,
  큰 workflow/IA 변경, 고모호도, 고가시성, 명시적 Owner 요청에만 사용하도록 했다.
- Lead Designer/UIUX/roles registry가 같은 mode 계약을 공유하게 갱신했다.
- 토큰 비용 근거는 `agents/lead_engineer/TOKEN-BUDGET.md`의 council 3-agent
  150-200K 추정치를 참조한다.

## 변경 파일

- `reviews/DIAGNOSTIC-2026-06-18-ui-design-system-maturity.md`
- `reviews/INDEX.md`
- `docs/design-system.md`
- `agents/lead_designer/SKILL.md`
- `agents/uiux_designer/SKILL.md`
- `agents/roles.yml`
- `scripts/agent_orchestrator.py`
- `scripts/check_agent_docs.py`
- `scripts/design_system_gate.py`
- `scripts/test_design_system_gate.py`
- `agents/lead_engineer/tasks/TASK-076-ui-design-system-maturity.md`
- `agents/lead_engineer/AUDIT-LOG.md`
- generated task views/index

## 완료 기록

완료 시각: 2026-06-18T10:25:30+09:00
검토자: Lead Engineer perspective + Doc Steward perspective + QA perspective + same-session self-review
실측 비용 (시간): 약 1.0h
실측 비용 (LLM 토큰): Codex session local meter unavailable
routing waiver: main-session scope. selected_model/policy_model telemetry는 Codex harness에서 노출되지 않아 focused tests와 governance gates로 대체했다.

## 검증

- `python -m pytest scripts/test_design_system_gate.py -q`
- `python scripts/design_system_gate.py --check`
- `python scripts/evidence_index_generator.py --write`
- `python scripts/evidence_index_generator.py --check`
- `python scripts/validate_task_schema.py`
- `python scripts/build_task_index.py --check`
- `python scripts/generate_views.py --check`
- `python scripts/check_agent_docs.py`
- `python scripts/owner_governance_gate.py --allow-empty-owner-docs`
- `git diff --check`

## 증거

- `reviews/DIAGNOSTIC-2026-06-18-ui-design-system-maturity.md`: maturity baseline and external references.
- `docs/design-system.md`: canonical design-system rules and proposal flow.
- `scripts/design_system_gate.py`: warning-first drift detection.
- `scripts/test_design_system_gate.py`: gate regression tests.

## 남은 이슈 / 한계

- Gate는 의도적으로 advisory다. 현재 UI에 기존 raw color literal, bare controls, oversized page가 있어 즉시 blocking하면 기존 worktree를 불필요하게 막는다.
- 실제 UI refactor는 후속 TASK로 분리해야 한다. 우선 후보는 chart palette token bridge, `agents/page.tsx` 패널 분리, `settings/page.tsx` tabs/form pattern extraction이다.
- Storybook 같은 isolated component workshop은 설치하지 않았다. 필요하면 별도 TASK로 다룬다.

## 리뷰

- Lead Engineer review: Owner 요청의 핵심인 진단 기록, design-system rulebook, Lead Designer role split, advisory gate를 모두 repo artifact로 남겼다.
- Lead Designer review: 새 디자인을 제안하는 flow를 reuse/extend/create decision으로 분리해 "기존 시스템만 반복" 문제를 줄였다.
- UI/UX Designer review: 구현자는 `docs/design-system.md`의 assetization checklist와 gate warning을 기준으로 refactor 단위를 고를 수 있다.
- Doc Steward review: root `reviews/`는 `reviews/INDEX.md`로 인덱싱하고 canonical 운영 record는 TASK/AUDIT에 연결했다.
- QA review: static gate는 focused unit tests로 고정했다.
