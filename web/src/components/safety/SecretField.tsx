// web/src/components/safety/SecretField.tsx
"use client";

import { useState } from "react";
import { EyeIcon, EyeOffIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface SecretFieldProps {
  id: string;
  label?: string;
  /** Placeholder shown as masked text — never an actual secret value */
  maskedPlaceholder?: string;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  className?: string;
}

/**
 * SecretField — masked input for sensitive settings (API keys etc).
 * IMPORTANT: never pre-fill with server-side secret values.
 * The maskedPlaceholder is display-only (e.g. "••••••••1234").
 */
export function SecretField({
  id,
  label,
  maskedPlaceholder = "••••••••",
  value,
  onChange,
  disabled = false,
  className,
}: SecretFieldProps) {
  const [revealed, setRevealed] = useState(false);

  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      {label && (
        <label htmlFor={id} className="text-sm font-medium text-foreground">
          {label}
        </label>
      )}
      <div className="relative flex items-center">
        <Input
          id={id}
          type={revealed ? "text" : "password"}
          value={value}
          placeholder={maskedPlaceholder}
          onChange={(e) => onChange((e.target as HTMLInputElement).value)}
          disabled={disabled}
          autoComplete="off"
          className="pr-9"
          aria-label={label}
        />
        <Button
          type="button"
          variant="ghost"
          size="icon-sm"
          className="absolute right-1 text-muted-foreground"
          aria-label={revealed ? "숨기기" : "보기"}
          onClick={() => setRevealed((v) => !v)}
          disabled={disabled}
        >
          {revealed ? <EyeOffIcon /> : <EyeIcon />}
        </Button>
      </div>
    </div>
  );
}
