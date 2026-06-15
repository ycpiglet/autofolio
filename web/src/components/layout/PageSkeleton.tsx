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
