# UI Feedback Round 1 — Crashes / Charts / Perf Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix four owner-reported UI bugs (hydration crash + guest button, CandleChart date crash, chart bottom clipping, tab-switch latency) and commit everything to branch `fix/ui-feedback-round1`.

**Architecture:** All changes are confined to `web/` (Next.js 16 App Router, React 19) plus the already-modified `scripts/run_api.py`. Bug fixes are surgical — no component restructuring. Loading skeletons use Next.js `loading.tsx` file convention (automatically wraps `page.tsx` in Suspense). The inline `<style>` causing the React 19 hydration mismatch is moved to `globals.css`. CandleChart converts ISO datetime strings to UTC epoch seconds before passing them to lightweight-charts v5. Chart containers get explicit height values and `overflow-visible` so the time-axis labels are not clipped.

**Tech Stack:** Next.js 16.2.9, React 19, lightweight-charts 5.2, Tailwind v4, Playwright 1.60, Node v24, TypeScript 5

---

## Pre-flight: branch + read current state

- [ ] **Create branch from main**

```powershell
cd C:\Users\ycpig\autofolio
git switch -c fix/ui-feedback-round1
```

Expected: `Switched to a new branch 'fix/ui-feedback-round1'`

- [ ] **Verify the uncommitted change to scripts/run_api.py is present**

```powershell
git diff HEAD -- scripts/run_api.py
```

Expected: diff shows the PYTHONPATH block added.

---

## Task 1 — Fix hydration error (BUG 1)

**Files:**
- Modify: `web/src/app/login/page.tsx` (remove inline `<style>` block, lines 64-74)
- Modify: `web/src/app/globals.css` (add `@keyframes fadeRise` + `.animate-fade-rise`)

**Background:** React 19 with the Next.js App Router hoists `<style>` tags to `<head>` during server render, but on the client the same `<style>` ends up inside the component tree. This server/client tree structure mismatch triggers React's "Hydration failed because the server rendered HTML didn't match the client" error. The inline `<style>` block in `login/page.tsx` (lines 64-74) is the culprit.

The fix is to move the CSS into `globals.css` and delete the `<style>` tag. The `login/page.tsx` is already `"use client"` so there is no SSR concern for the component itself, but the `<style>` hoist still occurs.

- [ ] **Step 1: Add the animation CSS to globals.css**

Open `web/src/app/globals.css`. Append BEFORE the final closing `}` of `@layer utilities` (after the `.bg-pnl-down` rule):

```css
/* Login page entrance animation (moved from login/page.tsx <style> tag) */
@keyframes fadeRise {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

@media (prefers-reduced-motion: no-preference) {
  .animate-fade-rise {
    animation: fadeRise 240ms cubic-bezier(0.16, 1, 0.3, 1) both;
  }
}
```

Place it at the end of `@layer utilities { ... }`, just before that block's closing `}`.

- [ ] **Step 2: Remove the inline `<style>` tag from login/page.tsx**

In `web/src/app/login/page.tsx`, delete lines 64-74 (the entire `<style>{``...``}</style>` element):

```tsx
// DELETE these lines:
      <style>{`
        @keyframes fadeRise {
          from { opacity: 0; transform: translateY(16px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @media (prefers-reduced-motion: no-preference) {
          .animate-fade-rise {
            animation: fadeRise 240ms cubic-bezier(0.16, 1, 0.3, 1) both;
          }
        }
      `}</style>
```

The `.animate-fade-rise` className references in the JSX (`line 77` and `line 139`) stay unchanged — they now resolve from `globals.css`.

- [ ] **Step 3: Build to confirm no compile errors**

```powershell
cd C:\Users\ycpig\autofolio\web
npm run build 2>&1 | Select-Object -Last 30
```

Expected: build completes, zero TypeScript errors.

- [ ] **Step 4: Commit Task 1**

```powershell
cd C:\Users\ycpig\autofolio
git add web/src/app/login/page.tsx web/src/app/globals.css scripts/run_api.py
git commit -m "fix(web): 하이드레이션 — inline <style> → globals.css, run_api.py PYTHONPATH"
```

---

## Task 2 — Fix CandleChart datetime crash (BUG 7)

**Files:**
- Modify: `web/src/components/domain/CandleChart.tsx` (time conversion in the `candles` map, lines 96-105)

**Background:** The KIS intraday API returns `time` values like `"2026-06-15T21:25:00"` or `"2026-06-12 09:00"`. lightweight-charts v5 only accepts two formats for the `time` field of a candlestick series:
1. A string in strict `"yyyy-mm-dd"` format (BusinessDay)
2. A number — UTC epoch seconds (UTCTimestamp)

Any other string (ISO datetime, space-separated datetime) throws `"Invalid date string"`. The fix is: if the value is exactly 10 chars and matches `YYYY-MM-DD`, pass it as-is; otherwise convert to epoch seconds with `Math.floor(new Date(value).getTime() / 1000)`.

The chart must also keep `timeVisible: true` (already set) so intraday times render on the x-axis. Sorting must happen on the **converted** values so order is preserved for numeric timestamps.

- [ ] **Step 1: Update the time conversion logic in CandleChart.tsx**

Find this block (lines 96-106 in CandleChart.tsx):

```tsx
    const candles = data.rows
      .map((row) => ({
        time: String(row[timeCol] ?? ""),
        open: Number(row[openCol] ?? 0),
        high: Number(row[highCol] ?? 0),
        low: Number(row[lowCol] ?? 0),
        close: Number(row[closeCol] ?? 0),
      }))
      .filter((c) => c.time.length > 0)
      .sort((a, b) => (a.time < b.time ? -1 : 1));
```

Replace with:

```tsx
    // Convert time to lightweight-charts accepted format:
    // "yyyy-mm-dd" strings stay as BusinessDay; everything else → UTCTimestamp (epoch seconds).
    function toChartTime(raw: string): string | number {
      if (raw.length === 10 && /^\d{4}-\d{2}-\d{2}$/.test(raw)) {
        return raw; // already YYYY-MM-DD — pass as BusinessDay string
      }
      // ISO datetime or "YYYY-MM-DD HH:mm" → epoch seconds (UTCTimestamp)
      const ms = new Date(raw.replace(" ", "T")).getTime();
      return Number.isFinite(ms) ? Math.floor(ms / 1000) : 0;
    }

    const candles = data.rows
      .map((row) => ({
        time: toChartTime(String(row[timeCol] ?? "")),
        open: Number(row[openCol] ?? 0),
        high: Number(row[highCol] ?? 0),
        low: Number(row[lowCol] ?? 0),
        close: Number(row[closeCol] ?? 0),
      }))
      .filter((c) => c.time !== 0 && c.time !== "")
      .sort((a, b) => {
        // Both types (string or number) are comparable with < >
        return a.time < b.time ? -1 : a.time > b.time ? 1 : 0;
      });
```

- [ ] **Step 2: Build to confirm no TypeScript errors**

```powershell
cd C:\Users\ycpig\autofolio\web
npm run build 2>&1 | Select-Object -Last 20
```

Expected: clean build, no type errors.

- [ ] **Step 3: Commit Task 2**

```powershell
cd C:\Users\ycpig\autofolio
git add web/src/components/domain/CandleChart.tsx
git commit -m "fix(web): CandleChart — ISO datetime → UTCTimestamp epoch seconds (BUG 7)"
```

---

## Task 3 — Fix chart bottom clipping (BUG 2)

**Files:**
- Modify: `web/src/components/domain/CandleChart.tsx` (chart wrapper div + height)
- Modify: `web/src/components/domain/EquityChart.tsx` (chart wrapper div)

**Background:** Both charts use `overflow-hidden` on their wrapper div, which clips the bottom border and the x-axis/time label row that lightweight-charts renders below the chart area. The fix is to change `overflow-hidden` to `overflow-visible` on the wrapper and ensure the parent card gives enough vertical space. The explicit `height` passed to `createChart()` already controls the canvas height; we just need the DOM wrapper to not clip it.

For CandleChart the wrapper has class `h-[280px] w-full overflow-hidden rounded-xl`. For EquityChart it has `h-60 w-full rounded-xl overflow-hidden`.

The time-axis labels are rendered by lightweight-charts inside the canvas, so `overflow-hidden` on the wrapper cuts them off when the canvas bleeds even 1px. Changing to `overflow-visible` fixes this without changing any height values.

- [ ] **Step 1: Fix CandleChart wrapper**

In `web/src/components/domain/CandleChart.tsx`, change the chart container div (currently around line 164):

```tsx
// BEFORE:
        <div
          ref={containerRef}
          className="h-[280px] w-full overflow-hidden rounded-xl"
          aria-label="캔들차트"
          data-testid="candle-chart"
        />

// AFTER:
        <div
          ref={containerRef}
          className="h-[280px] w-full overflow-visible rounded-xl"
          aria-label="캔들차트"
          data-testid="candle-chart"
        />
```

- [ ] **Step 2: Fix EquityChart wrapper**

In `web/src/components/domain/EquityChart.tsx`, change the chart container div (currently around line 120):

```tsx
// BEFORE:
    <div
      ref={containerRef}
      className={cn("h-60 w-full rounded-xl overflow-hidden", className)}
      aria-label="자산 추이 차트"
      data-testid="equity-chart"
    />

// AFTER:
    <div
      ref={containerRef}
      className={cn("h-60 w-full rounded-xl overflow-visible", className)}
      aria-label="자산 추이 차트"
      data-testid="equity-chart"
    />
```

- [ ] **Step 3: Build**

```powershell
cd C:\Users\ycpig\autofolio\web
npm run build 2>&1 | Select-Object -Last 20
```

Expected: clean build.

- [ ] **Step 4: Commit Task 3**

```powershell
cd C:\Users\ycpig\autofolio
git add web/src/components/domain/CandleChart.tsx web/src/components/domain/EquityChart.tsx
git commit -m "fix(web): 차트 잘림 — overflow-hidden → overflow-visible (CandleChart, EquityChart)"
```

---

## Task 4 — Add loading.tsx skeletons for tab routes (BUG 4)

**Files:**
- Create: `web/src/app/home/loading.tsx`
- Create: `web/src/app/portfolio/loading.tsx`
- Create: `web/src/app/trade/loading.tsx`
- Create: `web/src/app/history/loading.tsx`
- Create: `web/src/app/analysis/loading.tsx`
- Create: `web/src/app/agents/loading.tsx`
- Create: `web/src/app/alerts/loading.tsx`
- Create: `web/src/app/settings/loading.tsx`

**Background:** In production, Next.js App Router shows the `loading.tsx` Suspense fallback instantly on navigation, before the page's data fetches complete. Without `loading.tsx`, the old page stays frozen until the new page is ready. The `loading.tsx` file is a Server Component by default; it wraps the route's `page.tsx` in a `<Suspense>` boundary automatically.

Each skeleton should render an AppShell frame (so the sidebar and topbar remain visible and interactive) with pulse placeholder blocks where the page content will appear. We render the AppShell in the skeleton so the layout does not jump.

**Note about AppShell in loading.tsx:** `AppShell` is `"use client"` but that is fine — `loading.tsx` can import client components. However, `loading.tsx` itself must NOT have `"use client"` at the top, since it should be a Server Component to benefit from instant streaming.

- [ ] **Step 1: Create a shared skeleton layout helper**

Create `web/src/components/layout/PageSkeleton.tsx`:

```tsx
// web/src/components/layout/PageSkeleton.tsx
// Server-compatible skeleton used by loading.tsx files.
// Does NOT import AppShell (client) — renders a structurally equivalent shell
// so the layout does not shift when page content loads.

export function PageSkeleton() {
  return (
    <div className="flex h-screen overflow-hidden bg-page">
      {/* Sidebar placeholder */}
      <div className="flex w-56 shrink-0 flex-col border-r border-border bg-surface">
        <div className="flex h-12 items-center border-b border-border px-4">
          <div className="h-4 w-24 animate-pulse rounded bg-muted" />
        </div>
        <div className="flex flex-col gap-3 px-3 py-4">
          {[...Array(7)].map((_, i) => (
            <div key={i} className="h-8 animate-pulse rounded-lg bg-muted" />
          ))}
        </div>
      </div>
      {/* Main content placeholder */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Topbar placeholder */}
        <div className="flex h-10 items-center border-b border-border bg-surface px-4">
          <div className="h-4 w-32 animate-pulse rounded bg-muted" />
        </div>
        {/* Content area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          <div className="h-6 w-24 animate-pulse rounded bg-muted" />
          <div className="grid grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 animate-pulse rounded-xl bg-muted" />
            ))}
          </div>
          <div className="h-60 animate-pulse rounded-xl bg-muted" />
          <div className="h-40 animate-pulse rounded-xl bg-muted" />
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create loading.tsx for each route**

Create `web/src/app/home/loading.tsx`:

```tsx
import { PageSkeleton } from "@/components/layout/PageSkeleton";

export default function Loading() {
  return <PageSkeleton />;
}
```

Create `web/src/app/portfolio/loading.tsx`:

```tsx
import { PageSkeleton } from "@/components/layout/PageSkeleton";

export default function Loading() {
  return <PageSkeleton />;
}
```

Create `web/src/app/trade/loading.tsx`:

```tsx
import { PageSkeleton } from "@/components/layout/PageSkeleton";

export default function Loading() {
  return <PageSkeleton />;
}
```

Create `web/src/app/history/loading.tsx`:

```tsx
import { PageSkeleton } from "@/components/layout/PageSkeleton";

export default function Loading() {
  return <PageSkeleton />;
}
```

Create `web/src/app/analysis/loading.tsx`:

```tsx
import { PageSkeleton } from "@/components/layout/PageSkeleton";

export default function Loading() {
  return <PageSkeleton />;
}
```

Create `web/src/app/agents/loading.tsx`:

```tsx
import { PageSkeleton } from "@/components/layout/PageSkeleton";

export default function Loading() {
  return <PageSkeleton />;
}
```

Create `web/src/app/alerts/loading.tsx`:

```tsx
import { PageSkeleton } from "@/components/layout/PageSkeleton";

export default function Loading() {
  return <PageSkeleton />;
}
```

Create `web/src/app/settings/loading.tsx`:

```tsx
import { PageSkeleton } from "@/components/layout/PageSkeleton";

export default function Loading() {
  return <PageSkeleton />;
}
```

- [ ] **Step 3: Build**

```powershell
cd C:\Users\ycpig\autofolio\web
npm run build 2>&1 | Select-Object -Last 30
```

Expected: all 8 routes listed in the build output, zero errors.

- [ ] **Step 4: Commit Task 4**

```powershell
cd C:\Users\ycpig\autofolio
git add web/src/components/layout/PageSkeleton.tsx
git add web/src/app/home/loading.tsx web/src/app/portfolio/loading.tsx web/src/app/trade/loading.tsx
git add web/src/app/history/loading.tsx web/src/app/analysis/loading.tsx web/src/app/agents/loading.tsx
git add web/src/app/alerts/loading.tsx web/src/app/settings/loading.tsx
git commit -m "feat(web): loading.tsx 스켈레톤 — 8개 라우트 탭 전환 즉시 응답 (BUG 4)"
```

---

## Task 5 — Lint + full Playwright suite verification (HARD GATE)

**Background:** The spec requires `npm run lint` clean, `npm run build` green, and `CI=1 npx playwright test` (whole suite) passing twice. Playwright config at `web/playwright.config.ts` runs `npm run build && npm run start -- -p 3100` as the webServer so production mode is used automatically. The suite covers: `login.spec.ts`, `dashboard.spec.ts`, `phase3.spec.ts`, `phase4.spec.ts`, `analysis.spec.ts`.

`login.spec.ts` covers the guest button (BUG 1 regression check). `analysis.spec.ts` covers the candle chart container (BUG 7 regression check).

- [ ] **Step 1: Lint**

```powershell
cd C:\Users\ycpig\autofolio\web
npm run lint 2>&1
```

Expected: `No ESLint warnings or errors.` (or an empty output / exit code 0).

If lint fails on the new `PageSkeleton.tsx`, fix the specific error — usually a missing import or unused variable — then re-run.

- [ ] **Step 2: Build (final)**

```powershell
cd C:\Users\ycpig\autofolio\web
npm run build 2>&1 | Select-Object -Last 40
```

Expected: clean build, exit 0. Note all route sizes listed.

- [ ] **Step 3: Run full Playwright suite (pass 1)**

```powershell
cd C:\Users\ycpig\autofolio\web
$env:CI = "1"
npx playwright test 2>&1
```

Expected: all tests pass. Record the per-file count (X passed, 0 failed).

If any test fails:
- For `login.spec.ts` guest button test: hydration error is likely still present — re-check that the `<style>` tag is completely removed from `login/page.tsx`.
- For `analysis.spec.ts` candle chart test: the chart may not render if the mock returns data but lightweight-charts throws — check the browser console output in the Playwright trace.

- [ ] **Step 4: Run full Playwright suite (pass 2)**

```powershell
cd C:\Users\ycpig\autofolio\web
$env:CI = "1"
npx playwright test 2>&1
```

Expected: identical results, all pass. This confirms no flakiness.

- [ ] **Step 5: Squash-verify commit SHAs**

```powershell
cd C:\Users\ycpig\autofolio
git log --oneline fix/ui-feedback-round1 ^main
```

Expected: 4 commits visible (Tasks 1-4). Note the SHAs.

---

## Task 6 — Final commit with canonical message

**Background:** The spec requires a single commit (or the branch can have separate commits — but the spec asks for the full commit message with Co-Authored-By). We already committed each task individually; this final step is to verify the branch looks correct and produce the closing commit with the canonical trailer if any loose files remain.

- [ ] **Step 1: Check git status**

```powershell
cd C:\Users\ycpig\autofolio
git status
```

Expected: `nothing to commit, working tree clean` (all changes already committed).

If there are uncommitted changes, stage and commit them now.

- [ ] **Step 2: Verify branch log**

```powershell
git log --oneline fix/ui-feedback-round1 ^main
```

Expected output (4 commits, newest first):

```
<sha4>  feat(web): loading.tsx 스켈레톤 — 8개 라우트 탭 전환 즉시 응답 (BUG 4)
<sha3>  fix(web): 차트 잘림 — overflow-hidden → overflow-visible (CandleChart, EquityChart)
<sha2>  fix(web): CandleChart — ISO datetime → UTCTimestamp epoch seconds (BUG 7)
<sha1>  fix(web): 하이드레이션 — inline <style> → globals.css, run_api.py PYTHONPATH
```

- [ ] **Step 3: If a closing consolidation commit is needed, create it now**

Only create this commit if the above `git status` showed unstaged changes. Otherwise skip.

```powershell
cd C:\Users\ycpig\autofolio
git add -A
git commit -m "$(cat <<'EOF'
fix(web): 하이드레이션/게스트 버튼 + 분석 차트 날짜 크래시 + 차트 잘림 + 탭 로딩 (UI 피드백 1)

- BUG 1: inline <style>@keyframes → globals.css (React 19 hydration mismatch fix)
- BUG 7: CandleChart ISO datetime → UTCTimestamp epoch seconds (lightweight-charts 5)
- BUG 2: overflow-hidden → overflow-visible on CandleChart + EquityChart wrappers
- BUG 4: loading.tsx skeleton for 8 app routes (instant tab feedback)
- run_api.py: PYTHONPATH fix for uvicorn reload subprocess

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
EOF
)"
```

---

## Self-review checklist

### Spec coverage

| Requirement | Task that covers it |
|---|---|
| BUG 1: hydration error fix (inline `<style>` → globals.css) | Task 1 |
| BUG 1: guest button works after fix | Task 1 + login.spec.ts passes |
| BUG 7: CandleChart ISO datetime → epoch seconds | Task 2 |
| BUG 7: /analysis no longer crashes | Task 2 + analysis.spec.ts passes |
| BUG 2: chart bottom not clipped (CandleChart, EquityChart) | Task 3 |
| BUG 4: loading.tsx for /home, /portfolio, /trade, /history, /analysis, /agents, /alerts, /settings | Task 4 |
| SidebarNav uses next/link | Already the case — no change needed |
| scripts/run_api.py PYTHONPATH fix committed | Task 1 commit |
| npm run lint clean | Task 5 Step 1 |
| npm run build green | Task 5 Step 2 |
| CI=1 npx playwright test ×2 | Task 5 Steps 3-4 |
| Commit to branch, NOT push/merge | Throughout — no push command used |

### Placeholder scan

No TBD, TODO, or placeholder text in this plan. All code blocks contain the actual replacement code.

### Type consistency

- `toChartTime` returns `string | number` — matches the lightweight-charts `Time` type which is `string | number`
- `series.setData(candles as Parameters<typeof series.setData>[0])` cast is already in the original code and retained — the cast covers both BusinessDay (string) and UTCTimestamp (number)
- `PageSkeleton` is a named export, imported by name in all `loading.tsx` files — consistent
