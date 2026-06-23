/**
 * verify-format.mjs — zero-dependency verification of src/lib/format.ts
 *
 * The `web/` package has no unit-test runner (only Playwright E2E), so this
 * script is a committed, dependency-free correctness check for the currency /
 * PnL / number formatting helpers. It imports the REAL functions from
 * format.ts and asserts each output against a verified oracle.
 *
 * Run it with plain Node 24 (which strips TypeScript types on import and ships
 * a built-in node:assert — no compile step, no test framework, no node_modules):
 *
 *     node scripts/verify-format.mjs
 *
 * (If your Node build does not auto-enable type stripping, run with
 *  `node --experimental-strip-types scripts/verify-format.mjs`.)
 *
 * Native TS import requires the explicit `.ts` extension on the specifier.
 * Each case prints PASS or FAIL; the script exits 1 if any case fails, else 0.
 */

import assert from "node:assert/strict";
import {
  fmtWon,
  fmtUsd,
  fmtPct,
  pnlColorClass,
  pnlColor,
  fmtTabular,
  fmtPnlWon,
  symbolLabel,
  fmtWonShort,
  fmtWonShortSigned,
} from "../src/lib/format.ts";

// [label, actual, expected] — expected values are the verified correctness oracle.
const cases = [
  ["fmtWon(1234567)", fmtWon(1234567), "₩1,234,567"],
  ["fmtWon(1234.6)", fmtWon(1234.6), "₩1,235"],
  ["fmtUsd(1234.5)", fmtUsd(1234.5), "$1,234.50"],
  ["fmtPct(3.14)", fmtPct(3.14), "+3.14%"],
  ["fmtPct(-2)", fmtPct(-2), "-2.00%"],
  ["fmtPct(0)", fmtPct(0), "0.00%"],
  ["fmtTabular(1234567)", fmtTabular(1234567), "1,234,567"],
  ["fmtPnlWon(1000, 1.5)", fmtPnlWon(1000, 1.5), "₩1,000 (+1.50%)"],
  [
    'symbolLabel("005930", { "005930": "삼성전자" })',
    symbolLabel("005930", { "005930": "삼성전자" }),
    "삼성전자 (005930)",
  ],
  ['symbolLabel("005930", {})', symbolLabel("005930", {}), "005930"],
  ["pnlColorClass(5)", pnlColorClass(5), "text-pnl-up"],
  ["pnlColorClass(-5)", pnlColorClass(-5), "text-pnl-down"],
  ["pnlColorClass(0)", pnlColorClass(0), "text-muted-foreground"],
  ["pnlColor(5)", pnlColor(5), "#F04452"],
  ["pnlColor(-5)", pnlColor(-5), "#3182F6"],
  ["pnlColor(0)", pnlColor(0), "#8B95A1"],
  ["fmtWonShort(0)", fmtWonShort(0), "₩0"],
  ["fmtWonShort(5000)", fmtWonShort(5000), "₩5,000"],
  ["fmtWonShort(12345)", fmtWonShort(12345), "₩1.2만"],
  ["fmtWonShort(1234500)", fmtWonShort(1234500), "₩123.5만"],
  ["fmtWonShort(12345678)", fmtWonShort(12345678), "₩1,234.6만"],
  ["fmtWonShort(123456789)", fmtWonShort(123456789), "₩1.2억"],
  ["fmtWonShort(1234567890)", fmtWonShort(1234567890), "₩12.3억"],
  ["fmtWonShort(-98765)", fmtWonShort(-98765), "₩-9.9만"],
  ["fmtWonShortSigned(123456789)", fmtWonShortSigned(123456789), "+₩1.2억"],
  ["fmtWonShortSigned(-98765)", fmtWonShortSigned(-98765), "-₩9.9만"],
  ["fmtWonShortSigned(0)", fmtWonShortSigned(0), "₩0"],
];

let fails = 0;
for (const [label, actual, expected] of cases) {
  try {
    assert.equal(actual, expected);
    console.log(`PASS  ${label} === ${JSON.stringify(expected)}`);
  } catch {
    fails += 1;
    console.log(
      `FAIL  ${label} -> got ${JSON.stringify(actual)}, expected ${JSON.stringify(expected)}`,
    );
  }
}

console.log(`\n${cases.length - fails}/${cases.length} passed, ${fails} failed`);
process.exit(fails ? 1 : 0);
