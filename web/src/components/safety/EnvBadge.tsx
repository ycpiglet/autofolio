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
