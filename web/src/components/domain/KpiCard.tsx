import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PnlText } from "./PnlText";
import { cn } from "@/lib/utils";

interface KpiCardProps {
  label: string;
  value: string;
  /** Optional PnL delta value (numeric) */
  delta?: number;
  /** Display mode for the delta */
  deltaMode?: "pct" | "won" | "raw";
  className?: string;
}

/**
 * KpiCard — shows a label, a big KPI number, and an optional colored delta.
 * Uses `.kpi` utility class (26px / 700 / tabular-nums) from globals.css.
 */
export function KpiCard({
  label,
  value,
  delta,
  deltaMode = "pct",
  className,
}: KpiCardProps) {
  return (
    <Card className={cn("shadow-soft", className)}>
      <CardHeader>
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {label}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-1">
        <div className="kpi text-foreground" aria-label={`${label}: ${value}`}>
          {value}
        </div>
        {delta !== undefined && (
          <PnlText value={delta} mode={deltaMode} className="text-sm" />
        )}
      </CardContent>
    </Card>
  );
}
