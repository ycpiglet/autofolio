---
type: evidence
id: EVIDENCE-2026-06-19-006
created_at: 2026-06-19T20:29:20+09:00
owner: Lead Engineer
scope: Autofolio local bug
related_task: TASK-116
audit_log: AUDIT-2026-06-19-027
---

# check_agent_docs missing directory walk failure

## Classification

Local Autofolio bug. The stack trace did not include `site-packages/agent_runtime`
or upstream `agent_runtime.*` modules.

## 6W1H

Who: Lead Engineer / QA perspective during TASK-116 closeout verification.

What: `python scripts/check_agent_docs.py` crashed before reporting findings.

When: 2026-06-19T20:27:46+09:00.

Where: `scripts/check_agent_docs.py`, `markdown_files()`.

Why: `Path.glob("**/*.md")` raised `FileNotFoundError` while traversing a
missing or disappearing `docs/research` path, so the gate failed on filesystem
walk fragility instead of doc consistency findings.

How: Replace the Markdown collector with `os.walk(..., onerror=...)`, keep the
existing ignore rules, and add focused unit coverage for ignored directories and
walk errors.

Impact: TASK-116 closeout could not use `check_agent_docs.py` until the local
gate traversal was made tolerant of missing/inaccessible directories.

## Evidence

Observed failure:

```text
FileNotFoundError: [WinError 3] 지정된 경로를 찾을 수 없습니다: 'C:\\Users\\ycpig\\autofolio\\docs\\research'
```

Fix targets:

- `scripts/check_agent_docs.py`
- `tests/unit/test_check_agent_docs_markdown_files.py`

Verification:

- `.venv\Scripts\python.exe -m pytest tests\unit\test_check_agent_docs_markdown_files.py -q` -> 2 passed.
- `python scripts\check_agent_docs.py` -> 0 errors / 130 existing warnings.
- `git diff --check` -> no whitespace errors; CRLF warnings only.

No SQL migration, Supabase project mutation, deploy, secret, payment, bank API,
KIS/order/risk/prod surface, or destructive filesystem action was involved.
