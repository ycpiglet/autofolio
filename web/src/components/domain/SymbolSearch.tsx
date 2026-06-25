// web/src/components/domain/SymbolSearch.tsx
"use client";

import { useState, useRef, useId, useMemo, useEffect } from "react";
import { useSymbols } from "@/hooks/useSymbols";
import { symbolLabel } from "@/lib/format";

interface SymbolSearchProps {
  value: string;
  onChange: (code: string) => void;
  disabled?: boolean;
  id?: string;
  placeholder?: string;
}

const MAX_OPTIONS = 15;

export function SymbolSearch({
  value,
  onChange,
  disabled = false,
  id,
  placeholder = "종목명 또는 코드",
}: SymbolSearchProps) {
  const map = useSymbols();
  const [open, setOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const listboxId = useId();
  const closeTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close the dropdown on an outside pointer-down so it never traps clicks on
  // the form below (e.g. 매수/매도). Mousedown (not click) so the closing
  // happens before the same gesture's mouseup lands on the outside target.
  useEffect(() => {
    if (!open) return;
    function onOutsidePointerDown(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
        setHighlightedIndex(-1);
      }
    }
    document.addEventListener("mousedown", onOutsidePointerDown);
    return () => document.removeEventListener("mousedown", onOutsidePointerDown);
  }, [open]);

  // Filtered options based on current input value
  const options = useMemo<string[]>(() => {
    // Guard against a malformed symbol map (e.g. an API/mocks shape like
    // {columns:[],rows:[]}): only treat entries whose value is a string as
    // real symbols, so `name.toLowerCase()` below can never throw and crash
    // the page render.
    const entries = Object.keys(map).filter((code) => typeof map[code] === "string");
    if (!entries.length) return [];
    const query = value.toLowerCase();
    if (!query) return entries.slice(0, MAX_OPTIONS);
    const matched = entries.filter((code) => {
      const name = map[code] ?? "";
      return (
        code.toLowerCase().includes(query) ||
        name.toLowerCase().includes(query)
      );
    });
    return matched.slice(0, MAX_OPTIONS);
  }, [map, value]);

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const typed = e.target.value;
    onChange(typed);
    setOpen(true);
    setHighlightedIndex(-1);
  }

  function handleFocus() {
    setOpen(true);
  }

  function handleBlur() {
    // Delay close to allow click on option to register first
    if (closeTimerRef.current) {
      clearTimeout(closeTimerRef.current);
    }
    closeTimerRef.current = setTimeout(() => {
      setOpen(false);
      setHighlightedIndex(-1);
    }, 150);
  }

  function handleSelect(code: string) {
    if (closeTimerRef.current) {
      clearTimeout(closeTimerRef.current);
    }
    onChange(code);
    setOpen(false);
    setHighlightedIndex(-1);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    // Ignore keys fired while a Korean (or other) IME composition is active,
    // so Enter commits the in-progress syllable instead of selecting an option.
    if (e.nativeEvent.isComposing) return;
    if (!open || !options.length) {
      if (e.key === "ArrowDown" && options.length > 0) {
        setOpen(true);
        setHighlightedIndex(0);
        e.preventDefault();
      }
      return;
    }

    switch (e.key) {
      case "ArrowDown": {
        e.preventDefault();
        setHighlightedIndex((prev) =>
          prev < options.length - 1 ? prev + 1 : 0
        );
        break;
      }
      case "ArrowUp": {
        e.preventDefault();
        setHighlightedIndex((prev) =>
          prev > 0 ? prev - 1 : options.length - 1
        );
        break;
      }
      case "Enter": {
        if (highlightedIndex >= 0 && highlightedIndex < options.length) {
          e.preventDefault();
          handleSelect(options[highlightedIndex]);
        }
        break;
      }
      case "Escape": {
        setOpen(false);
        setHighlightedIndex(-1);
        break;
      }
    }
  }

  const showDropdown = open && options.length > 0;

  return (
    <div ref={containerRef} className="relative w-full">
      <input
        id={id}
        role="combobox"
        aria-expanded={showDropdown}
        aria-controls={listboxId}
        aria-autocomplete="list"
        aria-activedescendant={
          highlightedIndex >= 0
            ? `${listboxId}-option-${highlightedIndex}`
            : undefined
        }
        autoComplete="off"
        className="h-8 w-full rounded-lg border border-input bg-transparent px-2.5 py-1 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50"
        placeholder={placeholder}
        value={value}
        disabled={disabled}
        onChange={handleInputChange}
        onFocus={handleFocus}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
      />

      {showDropdown && (
        <ul
          id={listboxId}
          role="listbox"
          aria-label="종목 검색 결과"
          className="absolute left-0 right-0 top-full z-50 mt-1 max-h-60 overflow-y-auto rounded-lg border border-border bg-popover text-popover-foreground shadow-md"
        >
          {options.map((code, index) => {
            const isHighlighted = index === highlightedIndex;
            return (
              <li
                key={code}
                id={`${listboxId}-option-${index}`}
                role="option"
                aria-selected={isHighlighted}
                className={`cursor-pointer px-2.5 py-1.5 text-sm ${
                  isHighlighted
                    ? "bg-accent text-accent-foreground"
                    : "hover:bg-accent hover:text-accent-foreground"
                }`}
                onMouseDown={(e) => {
                  // Prevent blur from firing before click
                  e.preventDefault();
                  handleSelect(code);
                }}
              >
                {symbolLabel(code, map)}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
