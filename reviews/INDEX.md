---
type: evidence_index
id: EVIDENCE-INDEX-agent-runtime
audience: owner
status: pass
signal: pass
score: 100
priority: High
tags: [evidence, traceability, generated-index]
generated_at: 2026-06-21T17:09:37+09:00
record_count: 3
---

# Evidence Index

## Bottom Line
- Summary: indexed `3` review and evidence records under `reviews/`.
- Result: task closeout evidence is searchable by path, id, status, signal, and title.

## Signal
| Metric | State | Evidence |
| --- | --- | --- |
| Reviews covered | pass | `3` files |
| Source | pass | `reviews/` |

## Insight
- Manual review browsing does not scale; this generated file gives agents a stable entrypoint.
- The generator excludes itself from coverage to avoid self-referential churn.

## Decision
- Decision: regenerate this index after adding closeout reviews or evidence reports.
- Decision: use `scripts/evidence_index_generator.py --check` as the stale index gate.

## Action Board
| Path | ID | Kind | Status | Signal | Title |
| --- | --- | --- | --- | --- | --- |
| `reviews/DIAGNOSTIC-2026-06-18-ui-design-system-maturity.md` | `DIAGNOSTIC-2026-06-18-ui-design-system-maturity` | diagnostic | pass | watch | Autofolio UI Design System Maturity Diagnostic |
| `reviews/REVIEW-2026-06-19-marketing-growth-taskset-registration.md` | `REVIEW-2026-06-19-marketing-growth-taskset-registration` | review | pass | pass | Marketing Growth Taskset Registration Review |
| `reviews/REVIEW-2026-06-19-membership-prod-readiness-taskset.md` | `REVIEW-2026-06-19-membership-prod-readiness-taskset` | review | pass | pass | Membership Production Readiness Taskset Review |

## Risks / Blockers
- Risk: this index proves coverage, not semantic correctness of each evidence file.

## Next Steps
- Run `python scripts/evidence_index_generator.py --write` after adding new reviews.
- Run `python scripts/evidence_index_generator.py --check` before closeout.
