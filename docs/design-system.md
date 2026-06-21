# Autofolio Design System

Status: canonical design-system rulebook for new Autofolio UI work.
Created: 2026-06-18T10:25:30+09:00
Related: `reviews/DIAGNOSTIC-2026-06-18-ui-design-system-maturity.md`, `docs/UI_SPEC.md`,
`docs/superpowers/specs/2026-06-13-ui-overhaul-design.md`, `TASK-076`.

## Purpose

Autofolio UI work must be both reusable and capable of new design direction.
This document separates those concerns:

- **Design direction**: Lead Designer proposes the new experience, visual rhythm,
  and system impact.
- **Implementation**: UI/UX Designer builds with existing tokens/components first,
  then extends the system only when the proposal justifies it.
- **Gate**: automated checks catch drift so the next page does not re-invent color,
  controls, and layout rules.

## Layer Model

Use this order when adding or refactoring UI:

1. **Design tokens**: named visual decisions such as color, type, spacing, radius,
   shadow, chart palette, motion duration, and semantic status colors.
2. **`components/ui` primitives**: generic interaction building blocks with prop APIs.
   Examples: `Button`, `Input`, `Dialog`, `Card`, future `Select`, `Tabs`,
   `FormField`, `TableShell`.
3. **Pattern/domain components**: reusable Autofolio workflows or repeated page
   sections. Examples: `KpiCard`, `HoldingsTable`, `OrderForm`, provider setup
   shell, profile question card, safety action group, data state panel.
4. **Page files**: route composition, data fetching, and layout only.

Page files should not own durable design decisions. If a page grows repeated UI
logic or large class clusters, extract a pattern component.

## Assetization Rules

Classify every new UI decision before implementation.

| Bucket | Use when | Required action |
|--------|----------|-----------------|
| Design token | A visual value can recur or encode product meaning | Add or reuse a token; do not scatter raw literals |
| UI component | Generic primitive behavior repeats across domains | Add/extend `components/ui` with variants and a clear prop API |
| Pattern/domain component | A repeated Autofolio workflow or section appears | Add/extend `components/domain`, `components/safety`, or `components/layout` |
| One-off | It is route-specific and has no second caller yet | Keep it in the page, but do not add new raw design literals |

Promotion rule: the second repeated occurrence must trigger extraction unless
there is a written reason in the TASK record.

## Hard Rules

- Use existing design tokens and `components/ui` first.
- Keep page files focused on layout and data connection.
- Prefer `Button`, `Input`, `Dialog`, `Card`, and future primitives over bare
  native controls in page files.
- Repeatable product areas become pattern/domain components.
- Do not add raw hex/rgb colors outside token files or token bridge helpers.
- Do not create a new visual style by only writing Tailwind class strings in a page.
- Use `lucide-react` icons for common actions when an icon exists.
- Loading, empty, error, and gated states are part of the pattern, not afterthoughts.
- A11y states and labels are mandatory for controls and icon buttons.

## Adaptive Proposal Modes

Council-style design debate is an escalation path, not the default operating
mode. Every UI/design task must name the smallest sufficient proposal mode in
its TASK, proposal, or completion note.

| Mode | Use when | Participants | Output | Token posture |
|------|----------|--------------|--------|---------------|
| Light | One route, one component, a clear refactor, low novelty, or explicit low-token/user-light context | UI/UX Designer, or Lead Designer alone if direction is needed | 5-8 line Assetization Note | Keep under a small TASK budget; no live council or external research by default |
| Standard | A reusable pattern, 2-3 related surfaces, moderate ambiguity, or a new component variant | Lead Designer + UI/UX Designer, optional QA/Doc Steward review | Compact Design Direction Proposal | Normal Medium TASK posture |
| Heavy / Council | New visual language, major workflow or IA shift, high ambiguity, high visibility, explicit Owner request for council, or sufficient budget for deep critique | Lead Designer + UI/UX Designer + QA, with Research/Skeptic/Auditor as needed | Full Design Council Packet with alternatives, critique, risks, and rollback | Treat as high-cost; live 3-agent council can be 150-200K tokens per `agents/lead_engineer/TOKEN-BUDGET.md` |

Mode rules:

- Default to **Light** when the user mentions limited tokens, asks for a small
  iteration, or the change has one local owner and no new visual language.
- Default to **Standard** for normal product UI changes that introduce reusable
  assets or affect multiple pages.
- Use **Heavy / Council** only when one of its triggers is present. If token
  budget is low, write a council stub with risks and deferred questions instead
  of running a live council.
- Escalate from Light to Standard or Heavy only when implementation reveals
  broader reuse, accessibility, workflow, or product-risk impact.
- Downgrade from Heavy to Standard or Light when the decision is already clear
  and additional debate would mostly repeat known constraints.

## New Design Proposal Flow

New design should not mean ignoring the system. It should mean evolving it deliberately.

For any major visual or workflow change, Lead Designer first selects the proposal
mode, then creates the matching artifact before implementation.

Light mode uses an **Assetization Note**:

```text
Mode: Light
Decision:
Token:
UI component:
Pattern/domain component:
One-off:
Gate impact:
Acceptance:
```

Standard mode uses a **Design Direction Proposal**:

```text
Mode: Standard
Title:
Problem:
Audience:
Reference / prior art:
Design direction:
Reuse:
Extend:
Create:
Token impact:
Component impact:
Pattern impact:
Accessibility risks:
Responsive risks:
Acceptance:
```

Heavy mode uses a **Design Council Packet**:

```text
Mode: Heavy / Council
Problem:
Decision needed:
Options:
Lead Designer proposal:
UI/UX implementation critique:
QA/accessibility critique:
Research or prior-art evidence:
Risks:
Rollback:
Acceptance:
Deferred questions:
```

The artifact must choose one of three asset lanes:

- **Reuse**: existing tokens/components cover the change.
- **Extend**: add variants or pattern components while keeping the visual language.
- **Create**: introduce a new direction or token family. This requires rationale,
  examples, and a rollback path.

Novelty budget: each proposal may introduce at most two intentional new visual
ideas unless Owner explicitly asks for a larger redesign. Everything else must
reuse the existing system.

## Role Contract

### Lead Designer

- Owns design direction, system evolution, and proposal quality.
- Decides whether a UI change reuses, extends, or creates system assets.
- Selects Light, Standard, or Heavy/Council mode using the smallest sufficient
  process.
- Produces design direction proposals and component impact maps.
- Does not implement product code by default.

### UI/UX Designer

- Implements the approved UI plan.
- Extracts components and patterns.
- Verifies accessibility, responsive behavior, and browser behavior.
- Records Playwright or browser verification evidence.
- In Light mode, may proceed with an Assetization Note without a separate
  council when the change is local, reversible, and low-novelty.

### QA

- Verifies user flows, regressions, and edge cases.
- Converts user-perspective failures into BTC/BUG/TASK records.

### Doc Steward

- Checks this rulebook, TASK records, reviews, and evidence index for drift.

## Gate Policy

`python scripts/design_system_gate.py --check` is the design-system drift gate.

Initial policy:

- Raw color literals outside token files are warnings.
- Bare native controls inside `web/src/app/**/page.tsx` are warnings.
- Oversized page files are warnings.
- Repeated Tailwind class clusters are warnings.
- Missing proposal mode on new design tasks is a documentation warning, not a
  product-code blocker during baseline.

Promotion policy:

1. Warning-only during baseline.
2. After cleanup, block newly introduced violations.
3. After system coverage is high, block all violations unless a TASK records an
   explicit waiver.

Use `--strict` locally when preparing a cleanup branch.

## Refactor Checklist

Before editing a page:

- Search existing `components/ui`, `components/domain`, `components/layout`,
  and `components/safety`.
- Select Light, Standard, or Heavy/Council mode.
- Identify token, primitive, pattern, and one-off candidates.
- Confirm whether the change needs Lead Designer proposal.
- Run `python scripts/design_system_gate.py --check`.

Before closing:

- Page files should primarily connect data and arrange components.
- New repeated elements should have a named component.
- New literals should be tokenized or justified.
- Loading, empty, error, and gated states should be covered.
- Run frontend lint/build and relevant Playwright checks if UI code changed.

## References

- W3C Design Tokens Community Group: https://www.w3.org/community/design-tokens/
- Design Tokens Format Module: https://www.designtokens.org/tr/drafts/format/
- Atlassian design tokens: https://atlassian.design/tokens/design-tokens
- Atlassian components: https://atlassian.design/components
- Carbon documentation guidance: https://carbondesignsystem.com/contributing/documentation/
- Storybook: https://storybook.js.org/
- USWDS maturity model: https://designsystem.digital.gov/maturity-model/
