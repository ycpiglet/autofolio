---
type: diagnostic
id: DIAGNOSTIC-2026-06-18-ui-design-system-maturity
status: pass
signal: watch
score: 52
priority: Medium
tags: [ui, design-system, governance, refactor, lead-designer]
created_at: 2026-06-18T10:25:30+09:00
task: TASK-076
---

# Autofolio UI Design System Maturity Diagnostic

## Bottom Line

Autofolio의 현재 UI design-system 성숙도는 **2.6 / 5**로 판단한다.
색상/테마와 shadcn 기반 primitive는 이미 일부 asset화되어 있지만, page 파일이
아직 많은 UI 결정을 직접 들고 있고, design rule을 강제하는 gate가 없었다.

중요한 보정: Owner가 제시한 `ui_console.py` 13,343줄 단일 파일 진단은
agent_runtime 쪽 증거로는 유효하지만, 현재 Autofolio UI 정본은
`web/`의 Next.js/FastAPI 표면이다. 현재 Autofolio에는
`web/src/components/{ui,domain,layout,safety}` 레이어가 이미 존재한다.
따라서 문제는 "컴포넌트 레이어가 전무"가 아니라 **컴포넌트/패턴 분리와
강제 규칙이 아직 부족하다**로 재정의해야 한다.

## Signal

| Area | Score | Evidence | Diagnosis |
|------|-------|----------|-----------|
| Tokens | 3.0 / 5 | `web/src/app/globals.css`에 Tailwind v4 `@theme`와 semantic CSS vars 존재 | 색상/radius/type 일부는 토큰화됨. spacing/type scale은 Tailwind 기본 의존이 크고 chart palette는 반복 literal |
| UI primitives | 2.5 / 5 | `components/ui` 6개: badge/button/card/dialog/input/label | Button/Card 등 기초는 있으나 select/tabs/table/form field 등 반복 primitive가 부족 |
| Domain/pattern components | 2.5 / 5 | `components/domain` 17개, `layout` 4개, `safety` 7개 | 도메인 컴포넌트는 존재하지만 page 내부 반복 패턴 추출 기준이 없음 |
| Page composition | 1.5 / 5 | `agents/page.tsx` 29,885 bytes, `settings/page.tsx` 25,226, `login/page.tsx` 16,670 | page가 data wiring만이 아니라 layout, modal, form, setup shell을 많이 직접 소유 |
| Enforcement | 0.5 / 5 | 구현 전 별도 design-system gate 없음 | 다음 UI 변경이 raw color/bare control/oversized page를 추가해도 차단되지 않음 |
| Design novelty | 1.0 / 5 | Lead Designer 역할 없음, UIUX가 제안/구현/검증을 겸함 | 새 디자인 방향 제안과 기존 시스템 준수 구현이 같은 역할에 섞임 |

## Current Repo Measurements

2026-06-18 로컬 계측:

- `web/src/components`: 34 TSX files.
- Component split: `ui=6`, `domain=17`, `layout=4`, `safety=7`.
- Raw color matches under `web/src`: 80. 토큰 파일 외 주요 위치는 `web/src/lib/format.ts`,
  `AllocationChart.tsx`, `AttributionSankey.tsx`, `CandleChart.tsx`,
  `EquityChart.tsx`.
- App page bare controls: 17 matches across `<button>`, `<input>`, `<select>`,
  `<textarea>`.
- Largest page files:
  - `web/src/app/agents/page.tsx`: 29,885 bytes.
  - `web/src/app/settings/page.tsx`: 25,226 bytes.
  - `web/src/app/login/page.tsx`: 16,670 bytes.
  - `web/src/app/history/page.tsx`: 10,778 bytes.
  - `web/src/app/onboarding/investor-profile/page.tsx`: 10,466 bytes.

## Assetization Findings

### 1. Design Token Candidates

- Chart palette: allocation/sankey colors currently repeat literal hex arrays.
- Chart frame colors: grid, border, text colors repeat in candle/equity charts.
- PnL colors: `format.ts` returns literal hex values instead of CSS var or token names.
- Status colors: amber/destructive/muted combinations repeat in page alert blocks.
- Motion and skeleton sizing: page-level loading blocks repeat literal dimensions.

Recommended target: keep source tokens in `globals.css` for now, then expose
stable TypeScript helpers for chart libraries that cannot consume CSS vars directly.

### 2. `components/ui` Candidates

- `Select` / `SegmentedControl`: settings tabs, profile choices, chart symbol selectors.
- `FormField`: label + input/select + hint/error pattern appears repeatedly.
- `Tabs`: settings page has custom tab buttons.
- `Tooltip` wrapper: safety tooltips should not be hand-assembled per component.
- `TableShell`: current `DataTable` is domain-oriented; generic table chrome could live lower.

### 3. Pattern / Domain Component Candidates

- Provider setup shell: login/settings SSO setup guidance repeats domain-specific structure.
- Profile question card: onboarding answer selection should be extracted from page.
- Metric grid / KPI section: home/login/analysis cards repeat similar grid pattern.
- Data state panel: loading, empty, error, stale-data, and retry states should be reusable.
- Safety action group: kill switch, auto toggle, run-once, profile-gate warning.
- Agent roster panels: `agents/page.tsx` size indicates several panel-level patterns.

### 4. One-Off For Now

- Top-level page route selection and query composition.
- Single-use Korean explanatory copy tied to a specific page.
- One-time modal copy for external provider setup until it appears in a second surface.
- Highly domain-specific chart layout if it appears only once and has no second caller.

## External Methodology

- W3C / DTCG frames design tokens as a tool-neutral way to share stylistic
  decisions across tools and platforms. This supports moving repeated hex/radius/type
  decisions out of page/component bodies and into named tokens.
- Atlassian separates foundations/tokens, reusable components, and higher-level
  product/platform patterns. That maps well to Autofolio's `components/ui`,
  `components/domain`, and page composition split.
- Carbon requires component and pattern docs to cover usage, style, code, and
  accessibility. This is the missing standard for Autofolio pattern promotion.
- Storybook's model is useful even if Storybook is not installed immediately:
  build, test, and document components in isolation from app state.
- USWDS maturity guidance argues for incremental adoption. Autofolio should start
  warning-first and promote to blocking gates after cleanup.

Sources:

- W3C Design Tokens Community Group: https://www.w3.org/community/design-tokens/
- Design Tokens Format Module: https://www.designtokens.org/tr/drafts/format/
- Atlassian design tokens: https://atlassian.design/tokens/design-tokens
- Atlassian components: https://atlassian.design/components
- Carbon docs contribution guidance: https://carbondesignsystem.com/contributing/documentation/
- Storybook: https://storybook.js.org/
- USWDS maturity model: https://designsystem.digital.gov/maturity-model/

## Role Diagnosis

Current `uiux` owns design direction, frontend implementation, a11y, responsive behavior,
backend wiring, and browser verification. That is too broad for repeated redesign work.
The failure mode is predictable:

- New design proposals are under-specified because the implementer role optimizes for
  completion and consistency.
- Refactors tend to preserve the existing look because the role is told to reuse
  existing tokens/components.
- Design-system quality depends on individual taste, not a gate.

Recommended split:

- **Lead Designer**: proposes new visual/workflow directions, decides whether a change
  reuses, extends, or creates system assets, and owns design-system rule changes.
- **UI/UX Designer**: implements scoped UI changes, extracts components, verifies
  a11y/responsive/browser behavior, and follows `docs/design-system.md`.

Do not create a full Design Council yet. For this repo size, Lead Designer + UIUX +
QA/Doc Steward review is enough.

## Gate Diagnosis

The right first gate is advisory:

- Warn on raw color literals outside token files.
- Warn on native controls in `web/src/app/**/page.tsx` when `components/ui` exists.
- Warn on oversized page files that should extract patterns.
- Warn on repeated Tailwind class clusters.

Promotion path:

1. Warning-only now.
2. Clean the highest-value pages.
3. Make newly introduced violations blocking.
4. Later make all violations blocking after a tracked cleanup task.

## Decision

1. Add `docs/design-system.md` as the design-system rulebook.
2. Add `agents/lead_designer/SKILL.md` and register `lead-designer`.
3. Add `scripts/design_system_gate.py` with warning-first behavior.
4. Use `reviews/DIAGNOSTIC-2026-06-18-ui-design-system-maturity.md` as the first
   baseline report.
5. Do not refactor UI pages in this task. The diagnostic and gate should make the next
   UI refactor measurable.

## Next

| Step | Owner | Trigger |
|------|-------|---------|
| Extract token-backed chart palette helpers | UI/UX Designer | Next chart touch |
| Split `agents/page.tsx` into panels/patterns | UI/UX Designer | Next agents page change |
| Add `Select`, `Tabs`, and `FormField` primitives | UI/UX Designer | Next form-heavy change |
| Promote design gate to fail on new violations | Lead Engineer + Lead Designer | After first cleanup pass |
| Produce Design Direction Proposal before major UI redesign | Lead Designer | Any new visual direction request |
