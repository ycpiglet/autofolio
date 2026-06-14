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
