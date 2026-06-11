# Autofolio UI Control Desk Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a safety-first Streamlit UI refresh that turns Autofolio into an operational control desk for mock/paper trading supervision.

**Architecture:** Keep the current Streamlit multipage shell and introduce a small design-token/component layer before page-level changes. Safety-critical UI state flows from existing backend/system_state and must mirror existing trading guard policy instead of creating new order logic.

**Tech Stack:** Python 3.10, Streamlit, pandas, Plotly/Streamlit charts, pytest, `streamlit.testing` where practical, existing `app/ui` modules.

---

## File Structure

- Create `docs/design/autofolio/DESIGN.md`: canonical Autofolio UI direction based on `docs/design` research.
- Create `docs/design/autofolio/COMPONENT-MATRIX.md`: maps design roles to Streamlit components and files.
- Modify `app/ui/theme.py`: token constants, semantic colors, number typography helpers, environment labels.
- Modify `app/ui/components/ui.py`: status badge, safety rail, KPI panel, alert/message helpers, guarded action panels.
- Modify `app/ui/views/home.py`: control-desk dashboard layout.
- Modify `app/ui/views/portfolio.py`: holdings table and portfolio risk presentation.
- Modify `app/ui/views/trade.py`: order intent, guard checklist, source/environment display, confirmation flow.
- Modify `app/ui/views/agents.py`, `app/ui/views/alerts.py`, `app/ui/views/settings.py`: console/log/status surfaces using shared components.
- Add/modify tests under `tests/unit/`: theme/component helpers and backend-derived display contract tests.

## Design Guardrails

- Primary direction: Coinbase-style calm finance shell + IBM/Carbon operational density + Binance market table semantics + Linear/Raycast console surfaces.
- Default UI is light. Dark surfaces are limited to agent/log/incident console panels.
- Use Korean PnL convention: up red, down blue. Do not reuse PnL colors for buttons.
- Every order-capable screen must show environment, source, mode, auto flag, kill switch, whitelist/budget/duplicate/cooldown state, and latest guard decision when available.
- Danger actions require a spatially isolated panel and confirmation copy. Color alone is not sufficient.

---

### Task 1: Design Tokens and Autofolio Design Canon

**Files:**
- Create: `docs/design/autofolio/DESIGN.md`
- Create: `docs/design/autofolio/COMPONENT-MATRIX.md`
- Modify: `app/ui/theme.py`
- Test: `tests/unit/test_ui_theme_tokens.py`

- [ ] **Step 1: Write the failing token tests**

Create `tests/unit/test_ui_theme_tokens.py`:

```python
from app.ui import theme


def test_design_tokens_include_required_semantic_roles():
    assert theme.COLORS["action"] == "#0052ff"
    assert theme.COLORS["danger"] == "#da1e28"
    assert theme.COLORS["warning"] == "#f1c21b"
    assert theme.COLORS["success"] == "#24a148"
    assert theme.COLORS["surface"] == "#ffffff"
    assert theme.COLORS["surface_muted"] == "#f4f4f4"


def test_environment_label_is_explicit_and_human_readable():
    assert theme.env_label("mock") == "MOCK - no broker order"
    assert theme.env_label("paper") == "PAPER - KIS simulated"
    assert theme.env_label("prod") == "PROD - real account"
    assert theme.env_label("unknown") == "UNKNOWN - verify before action"


def test_pnl_color_keeps_korean_market_convention():
    assert theme.pnl_color(1, kr=True) == "red"
    assert theme.pnl_color(-1, kr=True) == "blue"
    assert theme.pnl_color(0, kr=True) == "gray"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_ui_theme_tokens.py -v`

Expected: FAIL because `COLORS` and `env_label` do not exist yet.

- [ ] **Step 3: Add the theme tokens**

Modify `app/ui/theme.py` by adding this block after `MODE_LABELS`:

```python
COLORS = {
    "canvas": "#f7f8fa",
    "surface": "#ffffff",
    "surface_muted": "#f4f4f4",
    "surface_strong": "#e0e0e0",
    "ink": "#161616",
    "ink_muted": "#525252",
    "hairline": "#e0e0e0",
    "action": "#0052ff",
    "info": "#0f62fe",
    "success": "#24a148",
    "warning": "#f1c21b",
    "danger": "#da1e28",
    "pnl_up_kr": "red",
    "pnl_down_kr": "blue",
}

ENV_LABELS = {
    "mock": "MOCK - no broker order",
    "paper": "PAPER - KIS simulated",
    "prod": "PROD - real account",
}


def env_label(env: str | None) -> str:
    return ENV_LABELS.get((env or "").lower(), "UNKNOWN - verify before action")
```

- [ ] **Step 4: Write the design canon**

Create `docs/design/autofolio/DESIGN.md`:

```markdown
# Autofolio UI Design Direction

Autofolio uses a safety-first operational control desk design. The visual source mix is Coinbase for calm financial trust, IBM/Carbon for dense enterprise data, Binance only for market-table semantics, and Linear/Raycast for agent/log console surfaces.

## Principles

1. Safety state is always visible before trading action.
2. Environment labels are explicit: MOCK, PAPER, PROD, UNKNOWN.
3. Default UI is light; dark panels are limited to console/log/incident review.
4. Korean PnL convention is preserved: up red, down blue.
5. Red is reserved for danger, kill, blocked, and destructive states.
6. Status never relies on color alone.

## Page Personality

| Page | Design Role |
|------|-------------|
| Home | Control desk summary |
| Portfolio | Financial position table |
| Trade | Guarded order-intent workflow |
| History | Audit and fill chronology |
| Analysis | Research and attribution workspace |
| Agents | Dark command-console surface |
| Alerts | Incident and notification center |
| Settings | Integration and safety configuration |
```

- [ ] **Step 5: Write the component matrix**

Create `docs/design/autofolio/COMPONENT-MATRIX.md`:

```markdown
# Autofolio Component Matrix

| Component | File | Source Inspiration | Required State |
|-----------|------|--------------------|----------------|
| Safety rail | `app/ui/components/ui.py` | Carbon message bar + Coinbase finance shell | env, mode, auto, kill, circuit breaker |
| Status badge | `app/ui/components/ui.py` | Carbon status + Fluent badge | label, tone, icon/text |
| KPI panel | `app/ui/components/ui.py` | Coinbase financial summary | value, delta, help |
| Guard checklist | `app/ui/views/trade.py` | WCAG financial confirmation | pass/fail, reason |
| Console panel | `app/ui/components/ui.py` | Linear/Raycast dark surface | title, rows |
| Data table | page views | Carbon data table | stable columns, empty state |
```

- [ ] **Step 6: Run focused tests**

Run: `pytest tests/unit/test_ui_theme_tokens.py -v`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add docs/design/autofolio/DESIGN.md docs/design/autofolio/COMPONENT-MATRIX.md app/ui/theme.py tests/unit/test_ui_theme_tokens.py
git commit -m "feat(ui): define Autofolio control desk design tokens"
```

---

### Task 2: Safety Rail and Shared Control Components

**Files:**
- Modify: `app/ui/components/ui.py`
- Modify: `app/ui/autofolio_app.py`
- Test: `tests/unit/test_ui_components_contract.py`

- [ ] **Step 1: Write helper-contract tests**

Create `tests/unit/test_ui_components_contract.py`:

```python
from app.ui.components import ui


def test_status_tone_maps_known_states():
    assert ui.status_tone("연결") == "success"
    assert ui.status_tone("주의") == "warning"
    assert ui.status_tone("위험") == "danger"
    assert ui.status_tone("OFF") == "neutral"


def test_status_badge_contains_text_not_color_only():
    rendered = ui.status_badge("위험")
    assert "위험" in rendered
    assert "BLOCK" in rendered or "위험" in rendered


def test_safety_summary_preserves_explicit_environment():
    summary = ui.build_safety_summary(
        env="paper",
        mode="L1",
        auto=False,
        kill=True,
        circuit_breaker=False,
    )
    assert summary["env"] == "PAPER - KIS simulated"
    assert summary["mode"] == "L1"
    assert summary["auto"] == "OFF"
    assert summary["kill"] == "ACTIVE"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_ui_components_contract.py -v`

Expected: FAIL because the helper functions do not exist.

- [ ] **Step 3: Add pure helper functions**

Add to `app/ui/components/ui.py` above `top_bar()`:

```python
STATUS_TONES = {
    "연결": "success",
    "연동": "success",
    "활성": "success",
    "정상": "success",
    "주의": "warning",
    "대기": "warning",
    "경고": "danger",
    "위험": "danger",
    "BLOCK": "danger",
    "미연결": "neutral",
    "미연동": "neutral",
    "OFF": "neutral",
}

TONE_MARKERS = {
    "success": "[OK]",
    "warning": "[CHECK]",
    "danger": "[BLOCK]",
    "neutral": "[OFF]",
}


def status_tone(status: str) -> str:
    return STATUS_TONES.get(status, "neutral")


def status_badge(status: str) -> str:
    tone = status_tone(status)
    marker = TONE_MARKERS[tone]
    color = {
        "success": "green",
        "warning": "orange",
        "danger": "red",
        "neutral": "gray",
    }[tone]
    return f":{color}[{marker}] {status}"


def build_safety_summary(env: str, mode: str, auto: bool, kill: bool, circuit_breaker: bool) -> dict[str, str]:
    return {
        "env": theme.env_label(env),
        "mode": mode,
        "auto": "ON" if auto else "OFF",
        "kill": "ACTIVE" if kill else "CLEAR",
        "circuit_breaker": "TRIGGERED" if circuit_breaker else "CLEAR",
    }
```

- [ ] **Step 4: Update badge compatibility**

Change `badge(status: str)` in `app/ui/components/ui.py` to:

```python
def badge(status: str) -> str:
    return status_badge(status)
```

- [ ] **Step 5: Refactor top bar into safety rail**

Update `top_bar()` to show environment text from `build_safety_summary`. Use `st.session_state.get("data_source", "demo")` and map `demo` to `mock`, `backend` to `paper` until backend exposes a richer environment value.

- [ ] **Step 6: Run focused tests**

Run: `pytest tests/unit/test_ui_components_contract.py tests/unit/test_ui_theme_tokens.py -v`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add app/ui/components/ui.py app/ui/autofolio_app.py tests/unit/test_ui_components_contract.py
git commit -m "feat(ui): add safety rail component contracts"
```

---

### Task 3: Home and Portfolio Control Desk Refresh

**Files:**
- Modify: `app/ui/views/home.py`
- Modify: `app/ui/views/portfolio.py`
- Modify: `app/ui/backend.py` only if a display contract needs a pure helper
- Test: `tests/unit/test_backend_kpis.py`

- [ ] **Step 1: Extend backend KPI contract if needed**

Add tests to `tests/unit/test_backend_kpis.py` only for pure data contracts. Example:

```python
def test_kpis_support_control_desk_required_keys():
    from app.ui import backend

    required = {"총자산", "일손익률", "누적손익률", "현금비중", "평가손익"}
    assert required <= set(backend.kpis().keys())
```

- [ ] **Step 2: Run existing KPI tests**

Run: `pytest tests/unit/test_backend_kpis.py -v`

Expected: PASS before layout changes.

- [ ] **Step 3: Update Home layout**

In `app/ui/views/home.py`, organize the page in this order:

```text
1. Safety/market state row
2. KPI strip
3. Portfolio curve and allocation/holdings summary
4. Guarded proposals or latest fills
5. Alerts/agent decisions
```

Use shared `ui.kpi_cards`, `ui.badge`, and `ui.empty_state`. Do not add trading actions to Home.

- [ ] **Step 4: Update Portfolio layout**

In `app/ui/views/portfolio.py`, make holdings the protagonist:

```text
1. Holdings table
2. Allocation/risk summary
3. Cash and concentration notes
4. Empty state when no holdings
```

Keep table columns stable so screenshots and tests remain predictable.

- [ ] **Step 5: Run focused checks**

Run: `pytest tests/unit/test_backend_kpis.py tests/unit/test_backend_holdings.py -v`

Expected: PASS.

- [ ] **Step 6: Manual UI verification**

Run: `run_ui.bat` or `streamlit run app/ui/autofolio_app.py`, then verify:

```text
Home shows safety state before financial charts.
Portfolio shows holdings table without horizontal text overlap.
Demo mode works without KIS credentials.
```

- [ ] **Step 7: Commit**

```bash
git add app/ui/views/home.py app/ui/views/portfolio.py tests/unit/test_backend_kpis.py
git commit -m "feat(ui): refresh home and portfolio control desk"
```

---

### Task 4: Trade Page Guarded Order Workflow

**Files:**
- Modify: `app/ui/views/trade.py`
- Modify: `app/ui/components/ui.py` if a reusable guard panel is needed
- Test: `tests/unit/test_trading_safety_guard.py`

- [ ] **Step 1: Preserve backend guard behavior**

Run: `pytest tests/unit/test_trading_safety_guard.py tests/unit/test_kis_order_script_guards.py -v`

Expected: PASS before UI changes.

- [ ] **Step 2: Reorder Trade page**

In `app/ui/views/trade.py`, put these sections before any order action:

```text
1. Environment and account source
2. Kill switch and auto state
3. Whitelist state
4. Budget/order limit state
5. Circuit breaker state
6. Duplicate/cooldown/audit reason state
7. Order intent form
8. Confirmation/action panel
```

- [ ] **Step 3: Make failed guards non-actionable**

Disable or hide action buttons when the visible checklist is not all pass. The page may still allow saving a condition, but must not present execution as available when kill switch, auto OFF, whitelist, circuit breaker, or source state blocks it.

- [ ] **Step 4: Add explicit confirmation copy**

Every order-capable control must show:

```text
Environment:
Symbol:
Side:
Quantity:
Estimated notional:
Source:
Guard status:
Audit reason:
```

- [ ] **Step 5: Run safety tests**

Run: `pytest tests/unit/test_trading_safety_guard.py tests/unit/test_kis_order_script_guards.py tests/integration/test_engine_e2e.py -v`

Expected: PASS.

- [ ] **Step 6: Manual UI verification**

Run the UI and verify:

```text
Trade page cannot suggest execution when kill switch is active.
Trade page shows PAPER/MOCK/UNKNOWN clearly.
Guard checklist is readable without relying on color.
```

- [ ] **Step 7: Commit**

```bash
git add app/ui/views/trade.py app/ui/components/ui.py
git commit -m "feat(ui): make trade workflow guard-first"
```

---

### Task 5: Console Surfaces, Accessibility, and Regression Gate

**Files:**
- Modify: `app/ui/views/agents.py`
- Modify: `app/ui/views/alerts.py`
- Modify: `app/ui/views/settings.py`
- Modify: `app/ui/components/ui.py`
- Test: `tests/unit/test_ui_components_contract.py`

- [ ] **Step 1: Add console helper tests**

Extend `tests/unit/test_ui_components_contract.py`:

```python
def test_console_row_requires_timestamp_source_and_message():
    row = ui.console_row("12:01", "guard", "BLOCK unknown source")
    assert "12:01" in row
    assert "guard" in row
    assert "BLOCK unknown source" in row
```

- [ ] **Step 2: Add console helper**

Add to `app/ui/components/ui.py`:

```python
def console_row(timestamp: str, source: str, message: str) -> str:
    return f"`{timestamp}` **{source}** - {message}"
```

- [ ] **Step 3: Refresh Agents page**

Use a dark, bordered console section for agent decisions/logs. Keep actions secondary; the page is for observability first.

- [ ] **Step 4: Refresh Alerts page**

Group alerts by severity and source. Critical alerts must show a plain-language next action and timestamp.

- [ ] **Step 5: Refresh Settings page**

Keep credentials/secret fields visually separated from mode/risk settings. Do not display secrets. Danger-zone actions must be spatially isolated.

- [ ] **Step 6: Run checks**

Run:

```powershell
pytest tests/unit/test_ui_components_contract.py -v
pytest tests/unit/test_backend_kpis.py tests/unit/test_backend_holdings.py -v
python scripts/check_agent_docs.py
```

Expected: pytest PASS. `check_agent_docs.py` should report 0 errors; existing warnings are acceptable if unchanged.

- [ ] **Step 7: Commit**

```bash
git add app/ui/views/agents.py app/ui/views/alerts.py app/ui/views/settings.py app/ui/components/ui.py tests/unit/test_ui_components_contract.py
git commit -m "feat(ui): polish console alerts and settings surfaces"
```

---

## Self-Review

- Spec coverage: design canon, safety rail, dashboard pages, guarded trade workflow, console/settings/accessibility are each mapped to one task.
- Placeholder scan: no `TBD`, `TODO`, or undefined implementation owner remains.
- Type consistency: helper names are `env_label`, `status_tone`, `status_badge`, `build_safety_summary`, and `console_row` across all tasks.
- R3 boundary: no KIS order implementation, secret handling, schema migration, prod activation, or safety-gate weakening is included.
