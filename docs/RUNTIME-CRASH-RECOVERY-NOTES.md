# Runtime crash-recovery notes

This documents the outcome of the crash-recovery + handoff hardening audit and
the one item deliberately deferred. Crash recovery and cross-session handoff are
now hardened on several fronts: a report-only resume-check
(`scripts/session_resume_check.py`) that prints a single `RESUME HERE` block and
flags zombie state, atomic session-record writes, ralph-loop reconciliation
against the authoritative pointer/STATUS, SessionStart hooks on both platforms,
and per-sub-step append-only checkpoints so a sudden shutdown surfaces the exact
in-task stopping point — not just which task was open.

## Known limitation: no in-flight claim heartbeat (LOW severity)

The worker uses the vendored `message_queue` claim system with
`CLAIM_TTL_SECONDS = 30 * 60` (30 minutes) and has **no lease-refresh / heartbeat
API**. A task that runs longer than 30 minutes under a still-alive worker can have
its claim expire mid-flight, after which the resume-check or `--fix` may treat the
message as recoverable.

Why this is **LOW** severity — the dangerous outcome (double-processing) is
already prevented:

- After `provider.run(...)`, the worker **re-checks `has_active_claim`** and
  returns WITHOUT writing a duplicate reply if the claim was lost
  (`scripts/agent_worker.py` lines 587-590, `claim_lost` event).
- Reply-writing is **idempotent**: `_has_reply` short-circuits before writing and
  `mark_answered` is claim-gated (`scripts/agent_worker.py` lines 592-599; see
  also `mark_answered` ~line 440).
- Worst case is therefore that a long task's result is **discarded and retried**,
  not corrupted or double-executed.
- These are **research / proposal** agents; live order execution sits behind its
  own separate safety gate (whitelist, caps, kill switch), so an expired research
  claim cannot reach the market.

## Proper fix (upstream)

Add a `refresh_claim(message_id)` / heartbeat API to agent_runtime's
`message_queue` that bumps `expires_at = now + TTL` with an atomic write, then
call it on a background interval inside `scripts/agent_worker.py` while
`provider.run()` executes. This must **NOT** be done by forking the vendored
`scripts/message_queue.py` locally: that file is identical to the agent_runtime
template and a local fork would be clobbered on the next upgrade. The fix belongs
upstream, then re-vendored.

## Detection already exists

`session_resume_check.py` already flags stale `*.claim` files and inbox messages
stuck in `claimed` with a stale/missing claim, and `--fix` recovers them back to
`open` on the real repo root.
