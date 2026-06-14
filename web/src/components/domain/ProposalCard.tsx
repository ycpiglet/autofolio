// web/src/components/domain/ProposalCard.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export interface Proposal {
  symbol: string;
  side: "BUY" | "SELL";
  target: number;
  reason: string;
}

interface ProposalCardProps {
  proposal: Proposal;
  className?: string;
}

const SIDE_STYLES: Record<Proposal["side"], string> = {
  BUY: "bg-pnl-up/10 text-pnl-up",
  SELL: "bg-pnl-down/10 text-pnl-down",
};

const SIDE_LABELS: Record<Proposal["side"], string> = {
  BUY: "매수",
  SELL: "매도",
};

/**
 * ProposalCard — presentational card for a single trade condition proposal.
 * Phase 2: no backend endpoint; caller passes props or shows EmptyState.
 */
export function ProposalCard({ proposal, className }: ProposalCardProps) {
  return (
    <Card className={cn("shadow-soft", className)}>
      <CardHeader>
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "rounded-md px-2 py-0.5 text-xs font-semibold",
              SIDE_STYLES[proposal.side],
            )}
          >
            {SIDE_LABELS[proposal.side]}
          </span>
          <CardTitle className="text-base">{proposal.symbol}</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-1 text-sm">
        <div className="flex justify-between text-muted-foreground">
          <span>목표가</span>
          <span className="font-mono tabular-nums text-foreground">
            ₩{Math.round(proposal.target).toLocaleString("ko-KR")}
          </span>
        </div>
        <p className="text-muted-foreground">{proposal.reason}</p>
      </CardContent>
    </Card>
  );
}
