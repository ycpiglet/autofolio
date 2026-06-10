# CLAUDE.md

Claude-specific companion guidance for this repository.

Read `AGENTS.md` first. If this file conflicts with `AGENTS.md` or current
records under `agents/lead_engineer/`, follow the shared protocol.

## Operating Mode

- Treat `AGENTS.md` as the source of truth.
- Use the current `TASK` / `CYCLE` record when implementation is needed.
- Keep edits scoped to the task.
- Preserve user changes.
- Verify before claiming completion.
- Report completed work in BRIEF format.

## Start Checklist

1. Read `AGENTS.md`.
2. Read `README.md`.
3. Read `AGENT_RUNTIME.md`.
4. Read `agents/lead_engineer/STATUS.md`.
5. Read `agents/roles.yml`.
6. Read the relevant role `SKILL.md`.
7. Read the active task or backlog item.

## Collaboration

Use the repository role model instead of answering every question as a single
generalist.

- Lead Engineer plans and closes work.
- QA verifies behavior.
- Independent Auditor checks evidence and completion.
- Doc Steward checks documentation integrity.
- Scribe cleans records after canonical state is clear.
- Research Agent provides evidence, not final decisions.
- Secretary handles personal desk summaries and reminders, not governance writes.

For substantial work, record which roles or perspectives contributed.

## Multi-Agent Execution (MANDATORY)

**모든 실질적 작업은 반드시 멀티에이전트로 수행한다. 이 규칙은 예외 없이 강제된다.**

1. **플랜이 있으면** `superpowers:subagent-driven-development` 스킬로 실행한다.
   - Task당 implementer 서브에이전트 1개 → spec reviewer → code quality reviewer 순서.
   - 리뷰가 이슈를 찾으면 implementer가 수정 → 재리뷰. 이슈가 없어야 다음 Task로 넘어간다.
2. **독립적인 작업 2개 이상이면** `superpowers:dispatching-parallel-agents`로 병렬 처리한다.
3. **백로그 자동화 사이클은** Ralph Loop(`/ralph-loop`)로 구동한다. 세션 시작 시 `.claude/ralph-loop.local.md`를 읽고 active면 즉시 재개한다.
4. **단일 에이전트 인라인 구현 금지** — 간단해 보여도 서브에이전트로 위임한다.
   - 허용 예외: 한 줄 수정, 설정 조회, 상태 확인, 사람에게 설명하는 응답.

## Implementation Rules

1. Prefer existing local helpers and scripts.
2. Avoid speculative abstractions.
3. Do not widen scope because adjacent code looks messy.
4. Add tests proportional to risk.
5. If a bug is reported, reproduce it before and after the fix when feasible.
6. Do not use external services, deployments, secrets, or destructive git actions
   without the required approval.

## Reporting

Final task responses start with:

```text
Bottom Line: ...
```

Then include `Signal`, `Insight`, and `Decision` sections when reporting work,
status, or a plan. Keep updates concise while work is still in progress.

## Time

Use:

```powershell
python scripts/now.py
```

Do not infer timestamps from memory or the chat clock.
