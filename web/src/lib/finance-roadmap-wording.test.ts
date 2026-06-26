/**
 * Compliance wording check for the FinanceRoadmapPanel (TASK-174).
 *
 * Asserts that every static display label exported from finance-roadmap-labels.ts
 * contains none of the forbidden advice/action phrases.
 *
 * Forbidden phrase list mirrors:
 *   - app/services/finance_roadmap.py :: _FORBIDDEN_OUTPUT_PHRASES (backend)
 *   - TASK-174 gate (UI-level Korean and English action terms)
 *
 * Running: cd web && npm run test:unit
 */
import { describe, it, expect } from "vitest";
import { ROADMAP_LABELS } from "./finance-roadmap-labels";

// Must stay in sync with app/services/finance_roadmap.py::_FORBIDDEN_OUTPUT_PHRASES
// plus UI-level action/advice terms from the TASK-174 compliance gate.
const FORBIDDEN_PHRASES = [
  // Backend-level forbidden (English)
  "you should buy",
  "you should sell",
  "guaranteed return",
  "execute order",
  "place order",
  "tax advice",
  "accounting advice",
  "investment advice",
  "trade recommendation",
  // UI-level action/advice terms
  "buy",
  "sell",
  "사세요",
  "추천",
  "매수",
  "매도",
  "주문",
  "발주",
] as const;

const LABEL_ENTRIES = Object.entries(ROADMAP_LABELS) as [string, string][];

describe("FinanceRoadmapPanel — compliance wording check (TASK-174)", () => {
  for (const phrase of FORBIDDEN_PHRASES) {
    it(`no label contains forbidden phrase: "${phrase}"`, () => {
      for (const [key, value] of LABEL_ENTRIES) {
        const lowered = value.toLowerCase();
        expect(
          lowered,
          `Label "${key}" = "${value}" contains forbidden phrase "${phrase}"`,
        ).not.toContain(phrase.toLowerCase());
      }
    });
  }
});
