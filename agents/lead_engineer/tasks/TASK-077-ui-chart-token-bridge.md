---
type: task
id: TASK-077
display_id: TASK-077
task_uid: a33fdc2e-124a-4599-97c9-b0c66f04c7ba
registered_at: 2026-06-18T11:52:39+09:00
created_at: 2026-06-18T11:52:39+09:00
started_at: 2026-06-18T11:52:39+09:00
updated_at: 2026-06-18T11:56:19+09:00
completed_at: 2026-06-18T11:56:19+09:00
status: 완료
owner: UI/UX Designer
assignees: [UI/UX Designer, Lead Designer, QA, Doc Steward]
priority: Medium
difficulty: 중
est_hours: 2
est_tokens: 30000
tags: [ui, refactor, design-system, frontend, token-bridge, qa]
gate: web UI refactor only; no KIS, order, risk, DB schema, secret, prod, or CI workflow changes
trigger_meeting: Owner direct request 2026-06-18
audit_log: AUDIT-2026-06-18-003
created: 2026-06-18
---

# TASK-077 UI chart token bridge refactor

작업 ID: TASK-077
상태: 완료
Owner: UI/UX Designer
요청 시각: 2026-06-18T11:52:39+09:00
기록 시각: 2026-06-18T11:52:39+09:00
요청자: Owner
수행자: UI/UX Designer, Lead Designer, QA, Doc Steward
의도: TASK-076 이후 실제 UI 개선/리팩토링 첫 단위로 차트 색상 raw literal을 design token bridge로 승격하고 design-system gate debt를 줄인다.
대상: `web/src/components/domain/*Chart*.tsx`, `web/src/lib/format.ts`, chart/design token helper, TASK/AUDIT/STATUS 기록
방법: Standard mode refactor. 기존 시각 언어는 유지하되 반복 차트 팔레트와 semantic chart/status 색상을 named token bridge로 분리한다.
감사 로그: AUDIT-2026-06-18-003

## Standard Design Direction Proposal

Mode: Standard

Problem:
차트 컴포넌트와 format helper가 raw hex/rgb 색상을 직접 보유해 `design_system_gate.py` raw-color warning을 만든다. 색상 의미도 페이지/컴포넌트별로 재결정되어 chart palette 변경이 분산된다.

Audience:
Autofolio Owner와 UI/UX 구현자. 사용자는 시각 변화보다 일관된 차트 의미, 유지보수성, 회귀 방지를 얻어야 한다.

Design direction:
현재 미니멀 라이트 UI와 기존 차트 색은 유지한다. 색상 값을 새로 디자인하지 않고, 반복되는 값만 token bridge로 이름 붙인다.

Reuse:
기존 chart colors, `components/domain` chart components, `web/src/lib/format.ts` semantics.

Extend:
`web/src/lib/design-tokens.ts` 또는 동등한 helper에 chart/status palette를 추가한다.

Create:
새 시각 언어 없음. 새 token bridge helper만 생성한다.

Token impact:
차트 primary/positive/negative/muted/grid/accent 및 allocation palette를 named token으로 분리한다.

Component impact:
`AllocationChart`, `AttributionSankey`, `CandleChart`, `EquityChart`가 token bridge를 import한다.

Pattern impact:
후속 chart/pattern 컴포넌트가 같은 token bridge를 재사용할 수 있다.

Accessibility risks:
기존 색 대비를 유지하므로 리스크는 낮다. 색상 의미만으로 상태를 전달하는 UI는 후속 개선 대상으로 남긴다.

Responsive risks:
레이아웃 변경 없음.

Acceptance:
`python scripts/design_system_gate.py --check`에서 raw-color warning 수가 감소하고, `npm run lint`, `npm run build`, 관련 Playwright smoke가 통과한다.

## 범위

포함:

- chart/status 색상 token bridge helper 추가.
- 차트 컴포넌트 raw color literal 제거.
- `web/src/lib/format.ts`의 status color raw literal 제거.
- design-system gate warning 감소 확인.
- TASK/AUDIT/STATUS/NEXT pointer 기록.

제외:

- 새 시각 언어 또는 대규모 UI redesign.
- `agents/page.tsx` 또는 `settings/page.tsx` 대형 페이지 분해.
- bare native control 전면 교체.
- KIS, order, risk, database schema, secrets, prod, CI workflow 변경.

## 진행 기록

- 2026-06-18T11:52:39+09:00: Owner 직접 요청으로 TASK 등록. Standard mode로 시작.
- 2026-06-18T11:56:19+09:00: chart/status color token bridge 구현과 focused verification 완료.

## 완료 내용

- `web/src/lib/design-tokens.ts`를 추가해 chart palette, lightweight chart theme, candle colors, equity area fill, PnL status colors를 한곳에 모았다.
- `AllocationChart`, `AttributionSankey`, `CandleChart`, `EquityChart`가 raw color literal 대신 token bridge를 사용하도록 변경했다.
- `web/src/lib/format.ts`의 `pnlColor()` browser/SSR raw color fallback을 `pnlColorTokens`로 교체했다.
- `scripts/design_system_gate.py`가 token bridge helper를 allowlist하도록 변경했다.
- `scripts/test_design_system_gate.py`에 token bridge allowlist regression을 추가했다.
- `python scripts/design_system_gate.py --check` 기준 raw-color-literal warning 5건이 제거되어 전체 warning이 16개에서 11개로 감소했다.

## 변경 파일

- `web/src/lib/design-tokens.ts`
- `web/src/components/domain/AllocationChart.tsx`
- `web/src/components/domain/AttributionSankey.tsx`
- `web/src/components/domain/CandleChart.tsx`
- `web/src/components/domain/EquityChart.tsx`
- `web/src/lib/format.ts`
- `scripts/design_system_gate.py`
- `scripts/test_design_system_gate.py`
- `agents/lead_engineer/tasks/TASK-077-ui-chart-token-bridge.md`
- `agents/lead_engineer/STATUS.md`
- `agents/project/NEXT-SESSION-POINTER.yml`
- generated task views/index

## 완료 기록

완료 시각: 2026-06-18T11:56:19+09:00
검토자: UI/UX Designer perspective + Lead Designer perspective + QA perspective + Doc Steward perspective + same-session self-review
실측 비용 (시간): 약 0.3h
실측 비용 (LLM 토큰): Codex session local meter unavailable

## 검증

- `rg -n "#(?:[0-9A-Fa-f]{3,8})\b|rgba?\(" web/src/components web/src/lib -g "!design-tokens.ts"` -> no matches.
- `python scripts/design_system_gate.py --check` -> watch, findings 0, warnings 11.
- `python -m pytest scripts/test_design_system_gate.py -q` -> 3 passed.
- `npm run lint` (web) -> pass.
- `npm run build` (web) -> pass.
- `npm run test:e2e -- e2e/demo-walkthrough.spec.ts --reporter=line` (web) -> 1 passed.
- `npm run start -- -p 3100` (web) -> production server started; `http://127.0.0.1:3100/login` returned HTTP 200.

## 증거

- `web/src/lib/design-tokens.ts`: chart/status color token bridge.
- `web/src/components/domain/AllocationChart.tsx`: allocation palette now uses token bridge.
- `web/src/components/domain/AttributionSankey.tsx`: attribution fallback bar palette now uses token bridge.
- `web/src/components/domain/CandleChart.tsx`: lightweight chart theme and candle colors now use token bridge.
- `web/src/components/domain/EquityChart.tsx`: lightweight chart theme and area fill colors now use token bridge.
- `web/src/lib/format.ts`: PnL raw color fallback now uses `pnlColorTokens`.
- `scripts/design_system_gate.py` and `scripts/test_design_system_gate.py`: token bridge helper allowlist and regression.

## 추가 closeout 검증

- `python scripts/validate_task_schema.py` -> OK.
- `python scripts/build_task_index.py --check` -> OK.
- `python scripts/generate_views.py --check` -> OK.
- `python scripts/owner_governance_gate.py --allow-empty-owner-docs` -> pass.
- `git diff --check` -> CRLF normalization warnings only.
- `python scripts/check_agent_docs.py` -> first run found missing TASK-077 registry row and missing `## 증거`; both were corrected.
- `python scripts/check_agent_docs.py` -> final OK, 0 errors / 132 warnings.

## 남은 이슈 / 한계

- Oversized page와 bare native control warning은 후속 TASK로 분리한다.

## 리뷰

- Lead Designer review: 새 시각 언어를 만들지 않고 기존 chart color를 token bridge로 승격했다. Standard mode 범위에 맞다.
- UI/UX Designer review: 차트 컴포넌트의 렌더링 API는 유지했고, 색상 의미만 중앙화했다.
- QA review: lint/build/E2E 8화면 walkthrough가 통과했다.
- Doc Steward review: TASK-076의 후속 후보였던 chart palette token bridge를 별도 TASK-077로 기록했다.
