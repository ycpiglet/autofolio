// web/src/components/domain/AgentMessage.tsx
import { cn } from "@/lib/utils";

export interface AgentMessageData {
  /** The agent name / role label shown in the badge */
  agent: string;
  /** Message text content */
  content: string;
  /** Optional: "user" | "agent" | "system" — controls bubble alignment */
  kind?: "user" | "agent" | "system";
}

interface AgentMessageProps {
  message: AgentMessageData;
  className?: string;
}

/**
 * AgentMessage — single chat-style bubble.
 * - agent: right-aligned, brand-accented badge
 * - user: left-aligned, muted badge
 * - system: full-width, italic muted text
 */
export function AgentMessage({ message, className }: AgentMessageProps) {
  const { agent, content, kind = "agent" } = message;

  if (kind === "system") {
    return (
      <div
        className={cn(
          "px-3 py-1.5 text-xs italic text-muted-foreground",
          className,
        )}
        role="note"
        aria-label={`시스템: ${content}`}
      >
        {content}
      </div>
    );
  }

  const isUser = kind === "user";

  return (
    <div
      className={cn(
        "flex flex-col gap-1",
        isUser ? "items-start" : "items-end",
        className,
      )}
    >
      <span
        className={cn(
          "rounded-full px-2 py-0.5 text-xs font-semibold",
          isUser
            ? "bg-muted text-muted-foreground"
            : "bg-brand/10 text-brand",
        )}
        aria-hidden
      >
        {agent}
      </span>
      <div
        className={cn(
          "max-w-prose rounded-xl px-3 py-2 text-sm",
          isUser
            ? "bg-muted text-foreground"
            : "bg-card text-foreground ring-1 ring-foreground/10",
        )}
        role="article"
        aria-label={`${agent}: ${content}`}
      >
        {content}
      </div>
    </div>
  );
}
