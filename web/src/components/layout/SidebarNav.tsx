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
    items: [
      { label: "성향 진단", href: "/onboarding/investor-profile", icon: "🧭" },
      { label: "설정", href: "/settings", icon: "⚙️" },
      { label: "매뉴얼", href: "/manuals", icon: "📖" },
    ],
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
