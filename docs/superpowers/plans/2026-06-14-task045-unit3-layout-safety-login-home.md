# TASK-045 Unit 3 — Core Layout + Safety Components + Login Screen + Home Shell

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the AppShell layout, safety badge/button components, full login screen (§4.4 Phase 1 variant), home shell page, and placeholder pages for all 8 nav routes — all on branch `feat/task-045-web-frontend`.

**Architecture:** New client components under `web/src/components/` (layout/ and safety/ subdirs). Pages live in `web/src/app/` as App Router segments. Login page replaces the Unit 2 placeholder with a real 55:45 split form. Home page wraps AppShell + EmptyState. Seven placeholder routes each render AppShell + EmptyState.

**Tech Stack:** Next.js 16 App Router, TypeScript, Tailwind v4 (CSS-first @theme tokens in globals.css), @base-ui/react (Button, Dialog, Tooltip), TanStack Query v5, lucide-react, shadcn primitives already installed (button, badge, card, dialog, input, label).

---

## File Structure

```
web/src/
  components/
    layout/
      AppShell.tsx          — sidebar + topbar + main content wrapper (client)
      SidebarNav.tsx        — 3-group 8-menu nav, active-route highlight (client)
      TopStatusBar.tsx      — no refresh; StatusCluster + KillSwitchButton always (client)
    safety/
      KillSwitchButton.tsx  — danger button, disabled Phase 1, reads kill state (client)
      ModeBadge.tsx         — L0-L4 + Korean label badge (pure display)
      EnvBadge.tsx          — 데모/목/모의/실전 color-coded badge (pure display)
      AutoTradingToggle.tsx — ON/OFF toggle, disabled Phase 1, wires ConfirmModal (client)
      ConfirmModal.tsx      — reusable confirm dialog (base-ui Dialog based) (client)
      EmptyState.tsx        — reusable empty state for unbuilt screens (pure display)
  app/
    login/
      page.tsx              — 55:45 login with ID/PW + guest (client, replaces placeholder)
    home/
      page.tsx              — AppShell + auth redirect + EmptyState (client, replaces placeholder)
    portfolio/
      page.tsx              — AppShell + EmptyState placeholder
    trade/
      page.tsx              — AppShell + EmptyState placeholder
    history/
      page.tsx              — AppShell + EmptyState placeholder
    analysis/
      page.tsx              — AppShell + EmptyState placeholder
    agents/
      page.tsx              — AppShell + EmptyState placeholder
    alerts/
      page.tsx              — AppShell + EmptyState placeholder
    settings/
      page.tsx              — AppShell + EmptyState placeholder
```

---

## Critical Context

- **Branch**: `feat/task-045-web-frontend` — already checked out
- **Working dir**: `web/` — `npm run lint` and `npm run build` must pass at the end
- **Design tokens** live in `web/src/app/globals.css` — use CSS vars `var(--brand)`, `var(--page)`, etc. and Tailwind utilities like `bg-primary`, `text-destructive`, `shadow-soft`, `kpi`
- **shadcn primitives** available: `@/components/ui/{button,badge,card,dialog,input,label}`; they use `@base-ui/react` underneath (NOT Radix)
- **Tooltip**: `@base-ui/react/tooltip` is available — use it for the "Phase 3에서 활성화" tooltip on disabled buttons
- **TanStack Query**: `useQuery` from `@tanstack/react-query`; `<Providers>` is already in root layout
- **API helpers**: `apiGet`, `apiPost`, `ApiError` from `@/lib/api`
- **No `"use server"` directives** — all interactive components need `"use client"`
- **KillSwitchButton + AutoTradingToggle**: Phase 1 = READ-ONLY. No POST to kill/auto endpoints. They read `/api/engine/status` for display only. Must be `disabled` with tooltip "Phase 3에서 활성화"
- **Login**: NO Google/Kakao/Naver. Only ID/PW + guest. `apiPost('/api/auth/login', {username, password})` for login, `apiPost('/api/auth/login', {guest:true})` for guest. On success → `router.push('/home')`. 401 → inline error.
- **Home**: `useQuery` for `/api/auth/me` — if 401, redirect to `/login`. Body = EmptyState.
- **EngineStatusResponse** shape: `{ env: string, auto_trading_enabled: boolean, kill_switch_active: boolean, circuit_breaker: { triggered: boolean, threshold_pct: number, consecutive_failures: number, today_pnl: number } }`
- **SessionResponse** shape: `{ role: string, username: string | null, data_source: string }`
- **Motion on login**: fade-rise ~240ms with `@keyframes` — honor `prefers-reduced-motion`
- **cn()** available from `@/lib/utils`
- **Next.js 16 + App Router**: use `"use client"` for interactive pages, `useRouter` from `next/navigation`, `Link` from `next/link`, `usePathname` from `next/navigation`

---

## Task 1: EmptyState component

**Files:**
- Create: `web/src/components/safety/EmptyState.tsx`

- [ ] **Step 1: Create EmptyState**

```tsx
// web/src/components/safety/EmptyState.tsx
import { cn } from "@/lib/utils";

interface EmptyStateProps {
  title?: string;
  description?: string;
  phase?: string;
  className?: string;
}

export function EmptyState({
  title = "준비 중",
  description,
  phase,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-border p-12 text-center",
        className
      )}
      role="status"
      aria-label={title}
    >
      <div className="text-4xl" aria-hidden>
        🏗️
      </div>
      <h2 className="text-base font-medium text-foreground">{title}</h2>
      {description && (
        <p className="max-w-sm text-sm text-muted-foreground">{description}</p>
      )}
      {phase && (
        <span className="mt-1 rounded-full bg-muted px-3 py-1 text-xs text-muted-foreground">
          {phase}
        </span>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verify it is pure TSX — no client hooks needed, no "use client" required**

---

## Task 2: ConfirmModal component

**Files:**
- Create: `web/src/components/safety/ConfirmModal.tsx`

- [ ] **Step 1: Create ConfirmModal using base-ui Dialog primitives**

```tsx
// web/src/components/safety/ConfirmModal.tsx
"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface ConfirmModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel?: () => void;
  dangerous?: boolean;
}

export function ConfirmModal({
  open,
  onOpenChange,
  title,
  description,
  confirmLabel = "확인",
  cancelLabel = "취소",
  onConfirm,
  onCancel,
  dangerous = false,
}: ConfirmModalProps) {
  function handleConfirm() {
    onConfirm();
    onOpenChange(false);
  }

  function handleCancel() {
    onCancel?.();
    onOpenChange(false);
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent showCloseButton={false}>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          {description && (
            <DialogDescription>{description}</DialogDescription>
          )}
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={handleCancel}>
            {cancelLabel}
          </Button>
          <Button
            variant={dangerous ? "destructive" : "default"}
            onClick={handleConfirm}
          >
            {confirmLabel}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

---

## Task 3: ModeBadge + EnvBadge

**Files:**
- Create: `web/src/components/safety/ModeBadge.tsx`
- Create: `web/src/components/safety/EnvBadge.tsx`

- [ ] **Step 1: Create ModeBadge**

```tsx
// web/src/components/safety/ModeBadge.tsx
import { cn } from "@/lib/utils";

export type ModeLevel = "L0" | "L1" | "L2" | "L3" | "L4";

const MODE_LABELS: Record<ModeLevel, string> = {
  L0: "L0 모의",
  L1: "L1 보수",
  L2: "L2 균형",
  L3: "L3 적극",
  L4: "L4 공격",
};

const MODE_COLORS: Record<ModeLevel, string> = {
  L0: "bg-muted text-muted-foreground",
  L1: "bg-blue-50 text-blue-700",
  L2: "bg-green-50 text-green-700",
  L3: "bg-orange-50 text-orange-700",
  L4: "bg-red-50 text-red-700",
};

interface ModeBadgeProps {
  mode: ModeLevel;
  className?: string;
}

export function ModeBadge({ mode, className }: ModeBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        MODE_COLORS[mode],
        className
      )}
      aria-label={`운용 모드: ${MODE_LABELS[mode]}`}
    >
      {MODE_LABELS[mode]}
    </span>
  );
}
```

- [ ] **Step 2: Create EnvBadge**

```tsx
// web/src/components/safety/EnvBadge.tsx
import { cn } from "@/lib/utils";

export type EnvType = "demo" | "paper" | "mock" | "live";

const ENV_LABELS: Record<EnvType, string> = {
  demo: "데모",
  paper: "모의",
  mock: "목",
  live: "실전",
};

const ENV_COLORS: Record<EnvType, string> = {
  demo:  "bg-blue-50 text-blue-600",
  paper: "bg-green-50 text-green-700",
  mock:  "bg-muted text-muted-foreground",
  live:  "bg-red-50 text-red-700 font-semibold",
};

// Map backend env strings to typed EnvType
function toEnvType(raw: string): EnvType {
  if (raw === "live" || raw === "실전") return "live";
  if (raw === "paper" || raw === "모의") return "paper";
  if (raw === "mock" || raw === "목") return "mock";
  return "demo";
}

interface EnvBadgeProps {
  env: string;
  className?: string;
}

export function EnvBadge({ env, className }: EnvBadgeProps) {
  const type = toEnvType(env);
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        ENV_COLORS[type],
        className
      )}
      aria-label={`환경: ${ENV_LABELS[type]}`}
    >
      {ENV_LABELS[type]}
    </span>
  );
}
```

---

## Task 4: KillSwitchButton

**Files:**
- Create: `web/src/components/safety/KillSwitchButton.tsx`

- [ ] **Step 1: Create KillSwitchButton**

Phase 1 — always disabled, reads state from props (state is fetched by parent). No POST calls in Phase 1.

```tsx
// web/src/components/safety/KillSwitchButton.tsx
"use client";

import { Tooltip } from "@base-ui/react/tooltip";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface KillSwitchButtonProps {
  /** Whether the kill switch is currently active (from /api/engine/status) */
  isActive?: boolean;
  /** Phase 1: always disabled — no POST until Phase 3 */
  phase1Disabled?: boolean;
  className?: string;
}

export function KillSwitchButton({
  isActive = false,
  phase1Disabled = true,
  className,
}: KillSwitchButtonProps) {
  const label = isActive ? "킬스위치 활성" : "자동매매 중단";
  const disabledReason = phase1Disabled ? "Phase 3에서 활성화" : undefined;

  return (
    <Tooltip.Provider>
      <Tooltip.Root>
        <Tooltip.Trigger
          render={
            <Button
              variant="destructive"
              size="sm"
              disabled={phase1Disabled}
              aria-disabled={phase1Disabled}
              aria-label={label + (disabledReason ? ` (${disabledReason})` : "")}
              className={cn(
                isActive && "opacity-50",
                className
              )}
            >
              {isActive ? "⛔ 중단됨" : "🛑 " + label}
            </Button>
          }
        />
        {disabledReason && (
          <Tooltip.Positioner>
            <Tooltip.Popup className="z-50 rounded-md bg-foreground px-2 py-1 text-xs text-background shadow-md">
              {disabledReason}
            </Tooltip.Popup>
          </Tooltip.Positioner>
        )}
      </Tooltip.Root>
    </Tooltip.Provider>
  );
}
```

---

## Task 5: AutoTradingToggle

**Files:**
- Create: `web/src/components/safety/AutoTradingToggle.tsx`

- [ ] **Step 1: Create AutoTradingToggle**

Phase 1 — always disabled, shows ON/OFF state from props. ConfirmModal is wired but unreachable because the button is disabled.

```tsx
// web/src/components/safety/AutoTradingToggle.tsx
"use client";

import { useState } from "react";
import { Tooltip } from "@base-ui/react/tooltip";
import { Button } from "@/components/ui/button";
import { ConfirmModal } from "./ConfirmModal";
import { cn } from "@/lib/utils";

interface AutoTradingToggleProps {
  /** Current auto-trading state from /api/engine/status */
  enabled?: boolean;
  /** Phase 1: always disabled — no POST until Phase 3 */
  phase1Disabled?: boolean;
  className?: string;
}

export function AutoTradingToggle({
  enabled = false,
  phase1Disabled = true,
  className,
}: AutoTradingToggleProps) {
  const [confirmOpen, setConfirmOpen] = useState(false);

  function handleToggleClick() {
    // Only reachable in Phase 3+ when phase1Disabled = false
    if (!phase1Disabled) {
      setConfirmOpen(true);
    }
  }

  return (
    <>
      <Tooltip.Provider>
        <Tooltip.Root>
          <Tooltip.Trigger
            render={
              <Button
                variant={enabled ? "default" : "outline"}
                size="sm"
                disabled={phase1Disabled}
                aria-disabled={phase1Disabled}
                aria-label={`자동매매 ${enabled ? "ON" : "OFF"}${phase1Disabled ? " (Phase 3에서 활성화)" : ""}`}
                onClick={handleToggleClick}
                className={cn("min-w-[90px]", className)}
              >
                자동매매 {enabled ? "ON" : "OFF"}
              </Button>
            }
          />
          {phase1Disabled && (
            <Tooltip.Positioner>
              <Tooltip.Popup className="z-50 rounded-md bg-foreground px-2 py-1 text-xs text-background shadow-md">
                Phase 3에서 활성화
              </Tooltip.Popup>
            </Tooltip.Positioner>
          )}
        </Tooltip.Root>
      </Tooltip.Provider>

      <ConfirmModal
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        title={enabled ? "자동매매 OFF 확인" : "자동매매 ON 확인"}
        description={
          enabled
            ? "자동매매를 중단합니다. 진행 중인 주문은 취소되지 않습니다."
            : "자동매매를 활성화합니다. 설정된 조건에 따라 자동으로 주문이 실행됩니다."
        }
        confirmLabel={enabled ? "비활성화" : "활성화"}
        onConfirm={() => {
          // Phase 3: call POST /api/engine/auto-trading here
        }}
        dangerous={!enabled}
      />
    </>
  );
}
```

---

## Task 6: TopStatusBar

**Files:**
- Create: `web/src/components/layout/TopStatusBar.tsx`

- [ ] **Step 1: Create TopStatusBar**

Fetches `/api/engine/status` (via TanStack Query from parent or directly). Renders StatusCluster (EnvBadge + ModeBadge) and KillSwitchButton always visible. No refresh button.

```tsx
// web/src/components/layout/TopStatusBar.tsx
"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import { EnvBadge } from "@/components/safety/EnvBadge";
import { ModeBadge, type ModeLevel } from "@/components/safety/ModeBadge";
import { KillSwitchButton } from "@/components/safety/KillSwitchButton";
import { AutoTradingToggle } from "@/components/safety/AutoTradingToggle";
import { cn } from "@/lib/utils";

interface EngineStatus {
  env: string;
  auto_trading_enabled: boolean;
  kill_switch_active: boolean;
  circuit_breaker: {
    triggered: boolean;
    threshold_pct: number;
    consecutive_failures: number;
    today_pnl: number;
  };
}

interface TopStatusBarProps {
  className?: string;
}

export function TopStatusBar({ className }: TopStatusBarProps) {
  const { data: status } = useQuery<EngineStatus>({
    queryKey: ["engine-status"],
    queryFn: () => apiGet<EngineStatus>("/api/engine/status"),
    staleTime: 30_000,
    retry: 1,
  });

  return (
    <header
      className={cn(
        "flex h-12 items-center justify-between border-b border-border bg-surface px-4 shadow-soft",
        className
      )}
      aria-label="상태 표시줄"
    >
      {/* Left spacer — title could go here in Phase 2 */}
      <div className="flex-1" />

      {/* StatusCluster */}
      <div
        className="flex items-center gap-2"
        aria-label="상태 클러스터"
      >
        {status ? (
          <>
            <EnvBadge env={status.env} />
            <AutoTradingToggle
              enabled={status.auto_trading_enabled}
              phase1Disabled={true}
            />
            <KillSwitchButton
              isActive={status.kill_switch_active}
              phase1Disabled={true}
            />
          </>
        ) : (
          <>
            <span className="h-5 w-12 animate-pulse rounded-full bg-muted" />
            <span className="h-7 w-20 animate-pulse rounded-lg bg-muted" />
            <span className="h-7 w-24 animate-pulse rounded-lg bg-muted" />
          </>
        )}
      </div>
    </header>
  );
}
```

Note: `ModeBadge` is included in the component set but is not available from `EngineStatusResponse` (mode/level is not part of the Phase 1 API). Skip it in TopStatusBar for now; it will be added once the API exposes mode in Phase 2.

---

## Task 7: SidebarNav

**Files:**
- Create: `web/src/components/layout/SidebarNav.tsx`

- [ ] **Step 1: Create SidebarNav**

3 groups, 8 menus. Active-route highlight. Brand wordmark at top.

```tsx
// web/src/components/layout/SidebarNav.tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

interface NavItem {
  label: string;
  href: string;
  icon?: string;
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    label: "운용",
    items: [
      { label: "홈", href: "/home", icon: "🏠" },
      { label: "포트폴리오", href: "/portfolio", icon: "📊" },
      { label: "매매", href: "/trade", icon: "💱" },
      { label: "내역", href: "/history", icon: "📋" },
    ],
  },
  {
    label: "인텔리전스",
    items: [
      { label: "분석", href: "/analysis", icon: "🔍" },
      { label: "에이전트", href: "/agents", icon: "🤖" },
      { label: "알림", href: "/alerts", icon: "🔔" },
    ],
  },
  {
    label: "시스템",
    items: [{ label: "설정", href: "/settings", icon: "⚙️" }],
  },
];

interface SidebarNavProps {
  className?: string;
}

export function SidebarNav({ className }: SidebarNavProps) {
  const pathname = usePathname();

  return (
    <nav
      className={cn(
        "flex w-56 shrink-0 flex-col border-r border-border bg-surface",
        className
      )}
      aria-label="사이드바 내비게이션"
    >
      {/* Brand wordmark */}
      <div className="flex h-12 items-center border-b border-border px-4">
        <Link
          href="/home"
          className="text-base font-bold tracking-tight text-brand"
          aria-label="Autofolio 홈으로"
        >
          Autofolio
        </Link>
      </div>

      {/* Nav groups */}
      <div className="flex flex-col gap-4 overflow-y-auto px-2 py-3">
        {NAV_GROUPS.map((group) => (
          <div key={group.label}>
            <p className="mb-1 px-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
              {group.label}
            </p>
            <ul role="list" className="flex flex-col gap-0.5">
              {group.items.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      aria-current={isActive ? "page" : undefined}
                      className={cn(
                        "flex items-center gap-2.5 rounded-lg px-2 py-1.5 text-sm transition-colors",
                        isActive
                          ? "bg-accent font-medium text-brand"
                          : "text-foreground hover:bg-muted"
                      )}
                    >
                      {item.icon && (
                        <span aria-hidden className="text-base">
                          {item.icon}
                        </span>
                      )}
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>
    </nav>
  );
}
```

---

## Task 8: AppShell

**Files:**
- Create: `web/src/components/layout/AppShell.tsx`

- [ ] **Step 1: Create AppShell**

```tsx
// web/src/components/layout/AppShell.tsx
"use client";

import { type ReactNode } from "react";
import { SidebarNav } from "./SidebarNav";
import { TopStatusBar } from "./TopStatusBar";
import { cn } from "@/lib/utils";

interface AppShellProps {
  children: ReactNode;
  className?: string;
}

export function AppShell({ children, className }: AppShellProps) {
  return (
    <div className="flex h-screen overflow-hidden bg-page">
      <SidebarNav />
      <div className="flex flex-1 flex-col overflow-hidden">
        <TopStatusBar />
        <main
          className={cn(
            "flex-1 overflow-y-auto p-6",
            className
          )}
          id="main-content"
          tabIndex={-1}
        >
          {children}
        </main>
      </div>
    </div>
  );
}
```

---

## Task 9: Login page

**Files:**
- Modify: `web/src/app/login/page.tsx`

- [ ] **Step 1: Replace the placeholder login page**

This is a client component (form state, router.push). Desktop 55:45 split. Left: brand zone with headline, mock KPI preview card, safety strip. Right: ID/PW form + guest card. Fade-rise animation honoring `prefers-reduced-motion`.

```tsx
// web/src/app/login/page.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiPost, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";

interface SessionResponse {
  role: string;
  username: string | null;
  data_source: string;
}

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [guestLoading, setGuestLoading] = useState(false);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await apiPost<SessionResponse>("/api/auth/login", { username, password });
      router.push("/home");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError("아이디 또는 비밀번호가 올바르지 않습니다.");
      } else {
        setError("로그인 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleGuest() {
    setError(null);
    setGuestLoading(true);
    try {
      await apiPost<SessionResponse>("/api/auth/login", { guest: true });
      router.push("/home");
    } catch {
      setError("게스트 로그인 중 오류가 발생했습니다.");
    } finally {
      setGuestLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen bg-page">
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

      {/* Left brand zone — 55% */}
      <div className="animate-fade-rise hidden lg:flex lg:w-[55%] flex-col justify-center gap-8 bg-brand/5 px-12 py-16">
        <div className="flex flex-col gap-4 max-w-md">
          <div className="text-3xl font-bold text-foreground leading-tight" style={{ wordBreak: "keep-all" }}>
            투자는 에이전트 팀에게,<br />결정은 나에게.
          </div>
          <p className="text-muted-foreground text-sm leading-relaxed">
            AI 에이전트가 시장을 분석하고 조건을 제안합니다.<br />
            실제 주문은 당신의 확인 후 실행됩니다.
          </p>
        </div>

        {/* Static demo preview card */}
        <div className="max-w-md rounded-xl bg-surface shadow-soft p-5 flex flex-col gap-4">
          <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            포트폴리오 미리보기 (데모)
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col gap-1 rounded-lg bg-page p-3">
              <span className="text-xs text-muted-foreground">총 평가금액</span>
              <span className="kpi text-foreground">₩12,543,000</span>
            </div>
            <div className="flex flex-col gap-1 rounded-lg bg-page p-3">
              <span className="text-xs text-muted-foreground">오늘 손익</span>
              <span className="kpi text-pnl-up">+₩123,400</span>
            </div>
            <div className="flex flex-col gap-1 rounded-lg bg-page p-3">
              <span className="text-xs text-muted-foreground">수익률</span>
              <span className="kpi text-pnl-up">+0.99%</span>
            </div>
            <div className="flex flex-col gap-1 rounded-lg bg-page p-3">
              <span className="text-xs text-muted-foreground">보유 종목</span>
              <span className="kpi text-foreground">4</span>
            </div>
          </div>
          <div className="flex flex-col gap-1.5">
            {[
              { name: "삼성전자", pct: "+1.2%", up: true },
              { name: "SK하이닉스", pct: "+2.8%", up: true },
              { name: "NAVER", pct: "-0.4%", up: false },
            ].map((row) => (
              <div
                key={row.name}
                className="flex items-center justify-between rounded-md px-2 py-1.5 text-sm hover:bg-muted"
              >
                <span className="text-foreground">{row.name}</span>
                <span className={row.up ? "text-pnl-up" : "text-pnl-down"}>
                  {row.pct}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Safety strip */}
        <div className="max-w-md rounded-xl border border-border bg-surface px-4 py-3">
          <p className="text-sm text-muted-foreground">
            🛡️ 모의투자 기본 &middot; 자동매매 기본 OFF &middot; 킬스위치 상시
          </p>
        </div>
      </div>

      {/* Right auth zone — 45% */}
      <div className="animate-fade-rise flex w-full lg:w-[45%] flex-col items-center justify-center px-6 py-12 lg:px-12"
           style={{ animationDelay: "60ms" }}>
        <div className="w-full max-w-sm flex flex-col gap-6">
          {/* Mobile headline */}
          <div className="lg:hidden text-center">
            <div className="text-xl font-bold text-foreground" style={{ wordBreak: "keep-all" }}>
              투자는 에이전트 팀에게,<br />결정은 나에게.
            </div>
          </div>

          {/* ID/PW form */}
          <Card>
            <CardHeader>
              <CardTitle>로그인</CardTitle>
              <CardDescription>Autofolio 계정으로 로그인하세요.</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleLogin} noValidate className="flex flex-col gap-4">
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="username">아이디</Label>
                  <Input
                    id="username"
                    type="text"
                    autoComplete="username"
                    placeholder="아이디 입력"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    aria-required="true"
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="password">비밀번호</Label>
                  <Input
                    id="password"
                    type="password"
                    autoComplete="current-password"
                    placeholder="비밀번호 입력"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    aria-required="true"
                  />
                </div>
                {error && (
                  <p role="alert" className="text-sm text-destructive">
                    {error}
                  </p>
                )}
                <Button
                  type="submit"
                  className="w-full"
                  disabled={loading}
                  aria-busy={loading}
                >
                  {loading ? "로그인 중…" : "로그인"}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Guest card */}
          <Card className="border-dashed">
            <CardContent className="pt-4 pb-4">
              <div className="flex flex-col items-center gap-3 text-center">
                <div className="text-sm font-medium text-foreground">
                  로그인 없이 둘러보기
                </div>
                <p className="text-xs text-muted-foreground">
                  데모 데이터로 Autofolio를 체험해보세요.
                </p>
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={handleGuest}
                  disabled={guestLoading}
                  aria-busy={guestLoading}
                >
                  {guestLoading ? "연결 중…" : "게스트 데모 시작"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}
```

---

## Task 10: Home page

**Files:**
- Modify: `web/src/app/home/page.tsx`

- [ ] **Step 1: Replace placeholder home page**

Fetches `/api/auth/me` via TanStack Query. If 401, redirect to login. Renders AppShell + EmptyState.

```tsx
// web/src/app/home/page.tsx
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { apiGet, ApiError } from "@/lib/api";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";

interface SessionResponse {
  role: string;
  username: string | null;
  data_source: string;
}

export default function HomePage() {
  const router = useRouter();

  const { error, isError, isPending } = useQuery<SessionResponse>({
    queryKey: ["auth-me"],
    queryFn: () => apiGet<SessionResponse>("/api/auth/me"),
    retry: false,
    staleTime: 60_000,
  });

  useEffect(() => {
    if (isError && error instanceof ApiError && error.status === 401) {
      router.replace("/login");
    }
  }, [isError, error, router]);

  if (isPending) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-page">
        <div className="h-8 w-8 animate-pulse rounded-full bg-muted" aria-label="로딩 중" />
      </div>
    );
  }

  return (
    <AppShell>
      <EmptyState
        title="홈 대시보드"
        description="홈 대시보드는 Phase 2에서 구현됩니다."
        phase="Phase 2 예정"
      />
    </AppShell>
  );
}
```

---

## Task 11: Placeholder pages for all remaining routes

**Files:**
- Create: `web/src/app/portfolio/page.tsx`
- Create: `web/src/app/trade/page.tsx`
- Create: `web/src/app/history/page.tsx`
- Create: `web/src/app/analysis/page.tsx`
- Create: `web/src/app/agents/page.tsx`
- Create: `web/src/app/alerts/page.tsx`
- Create: `web/src/app/settings/page.tsx`

- [ ] **Step 1: Create portfolio page**

```tsx
// web/src/app/portfolio/page.tsx
"use client";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";
export default function PortfolioPage() {
  return (
    <AppShell>
      <EmptyState
        title="포트폴리오"
        description="포트폴리오 화면은 Phase 2에서 구현됩니다."
        phase="Phase 2 예정"
      />
    </AppShell>
  );
}
```

- [ ] **Step 2: Create trade page**

```tsx
// web/src/app/trade/page.tsx
"use client";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";
export default function TradePage() {
  return (
    <AppShell>
      <EmptyState
        title="매매"
        description="매매 화면은 Phase 3에서 구현됩니다."
        phase="Phase 3 예정"
      />
    </AppShell>
  );
}
```

- [ ] **Step 3: Create history page**

```tsx
// web/src/app/history/page.tsx
"use client";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";
export default function HistoryPage() {
  return (
    <AppShell>
      <EmptyState
        title="내역"
        description="거래 내역 화면은 Phase 2에서 구현됩니다."
        phase="Phase 2 예정"
      />
    </AppShell>
  );
}
```

- [ ] **Step 4: Create analysis page**

```tsx
// web/src/app/analysis/page.tsx
"use client";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";
export default function AnalysisPage() {
  return (
    <AppShell>
      <EmptyState
        title="분석"
        description="분석 화면은 Phase 5에서 구현됩니다."
        phase="Phase 5 예정"
      />
    </AppShell>
  );
}
```

- [ ] **Step 5: Create agents page**

```tsx
// web/src/app/agents/page.tsx
"use client";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";
export default function AgentsPage() {
  return (
    <AppShell>
      <EmptyState
        title="에이전트"
        description="에이전트 화면은 Phase 4에서 구현됩니다."
        phase="Phase 4 예정"
      />
    </AppShell>
  );
}
```

- [ ] **Step 6: Create alerts page**

```tsx
// web/src/app/alerts/page.tsx
"use client";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";
export default function AlertsPage() {
  return (
    <AppShell>
      <EmptyState
        title="알림"
        description="알림 화면은 Phase 4에서 구현됩니다."
        phase="Phase 4 예정"
      />
    </AppShell>
  );
}
```

- [ ] **Step 7: Create settings page**

```tsx
// web/src/app/settings/page.tsx
"use client";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";
export default function SettingsPage() {
  return (
    <AppShell>
      <EmptyState
        title="설정"
        description="설정 화면은 Phase 3에서 구현됩니다."
        phase="Phase 3 예정"
      />
    </AppShell>
  );
}
```

---

## Task 12: Lint + Build verification

**Files:** none — verification only

- [ ] **Step 1: Run lint from web/ directory**

```powershell
cd C:\Users\ycpig\autofolio\web && npm run lint
```

Expected: Zero errors. If errors, fix them before proceeding.

- [ ] **Step 2: Run build from web/ directory**

```powershell
cd C:\Users\ycpig\autofolio\web && npm run build
```

Expected: `✓ Compiled successfully` with all routes: `/`, `/login`, `/home`, `/portfolio`, `/trade`, `/history`, `/analysis`, `/agents`, `/alerts`, `/settings`.

- [ ] **Step 3: Commit all web/ changes to the feature branch**

```powershell
cd C:\Users\ycpig\autofolio
git add web/src/
git status
git commit -m "$(cat <<'EOF'
feat(web): 코어 레이아웃 + 안전 컴포넌트 + 로그인 화면 + 홈 셸 (TASK-045 Unit3)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review Against Spec

**Spec coverage check:**

| Spec requirement | Covered in task |
|---|---|
| AppShell (sidebar + topbar + main) | Task 8 |
| SidebarNav — 3 groups, 8 menus, active highlight, brand wordmark | Task 7 |
| TopStatusBar — no refresh, StatusCluster, KillSwitch always visible | Task 6 |
| KillSwitchButton — disabled Phase 1, reads state, danger styling | Task 4 |
| ModeBadge L0–L4 Korean | Task 3 |
| EnvBadge color-coded | Task 3 |
| AutoTradingToggle — disabled Phase 1, ConfirmModal wired | Task 5 |
| ConfirmModal — reusable, shadcn dialog | Task 2 |
| EmptyState | Task 1 |
| Login 55:45 split | Task 9 |
| Login: headline, demo preview, safety strip | Task 9 |
| Login: ID/PW → apiPost login, 401 error | Task 9 |
| Login: guest → apiPost guest:true | Task 9 |
| NO Google/Kakao/Naver | Task 9 (confirmed absent) |
| Login: fade-rise 240ms, prefers-reduced-motion | Task 9 |
| Home: useQuery auth/me, redirect 401 → login | Task 10 |
| Home: AppShell + EmptyState | Task 10 |
| Placeholder pages for /portfolio /trade /history /analysis /agents /alerts /settings | Task 11 |
| lint + build green | Task 12 |
| KillSwitch/AutoToggle NO POST in Phase 1 | Tasks 4, 5 (confirmed — no POST call exists) |
| Phase 1 note: no dead Google button | Task 9 (confirmed absent) |

**Placeholder scan:** No TBD, TODO, or placeholder steps found.

**Type consistency check:**
- `EngineStatus` interface defined in Task 6 (TopStatusBar) — shape matches `EngineStatusResponse` schema: `{env, auto_trading_enabled, kill_switch_active, circuit_breaker}`
- `SessionResponse` interface defined in Tasks 9 and 10 — matches backend schema `{role, username, data_source}`
- `ModeLevel` exported from `ModeBadge.tsx` and imported by type in `TopStatusBar.tsx`
- `ConfirmModal` `open/onOpenChange` props match usage in `AutoTradingToggle`
- `EmptyState` `title/description/phase/className` props match all 7 placeholder usages

**Tooltip API note:** `@base-ui/react/tooltip` uses `Tooltip.Provider`, `Tooltip.Root`, `Tooltip.Trigger`, `Tooltip.Positioner`, `Tooltip.Popup` — this is the base-ui v1.x API. The `render` prop on `Tooltip.Trigger` is used to wrap the disabled `Button` so the trigger works even when the inner element is disabled (disabled elements don't receive mouse events — the Trigger wrapper handles it).
