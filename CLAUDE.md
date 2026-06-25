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

0. Run `python scripts/session_resume_check.py` and resume from its `RESUME HERE` output (crash-recovery + pointer/loop consistency).
1. Read `AGENTS.md`.
2. Read `README.md`.
3. Read `AGENT_RUNTIME.md`.
4. Read `agents/lead_engineer/STATUS.md`.
5. Read `agents/roles.yml`.
6. Read the relevant role `SKILL.md`.
7. Read the active task or backlog item.

### Long-task checkpoints (crash recovery)

다단계·장시간 작업은 서브스텝마다 진행을 기록한다. 그러면 PC가 갑자기 꺼져도
`session_resume_check.py`가 중단된 정확한 서브스텝과 다음 행동을 즉시 보여준다.

```
python scripts/session_resume_check.py checkpoint --task TASK-XXX --step "무엇을 끝냈는가" --status started|done|blocked --next "다음 행동"
```

기록은 `agents/runtime/checkpoints/<TASK>.jsonl`(append-only)에 쌓이고, 다음 세션의
Start Checklist step 0에서 자동 노출된다.

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

### Role Directory

Authoritative shared role definitions live under `agents/`:

- [Owner](agents/owner/SKILL.md)
- [CEO](agents/ceo/SKILL.md)
- [Managing Partner](agents/managing_partner/SKILL.md)
- [Lead Engineer](agents/lead_engineer/SKILL.md)
- [Independent Auditor](agents/independent_auditor/SKILL.md)
- [Doc Steward](agents/doc_steward/SKILL.md)
- [Scribe](agents/scribe/SKILL.md)
- [Research Agent](agents/research_agent/SKILL.md)
- [Timeline Agent](agents/timeline_agent/SKILL.md)
- [Requirements Interviewer](agents/requirements_interviewer/SKILL.md)
- [Secretary](agents/secretary/SKILL.md)
- [Backend Engineer](agents/backend_engineer/SKILL.md)
- [UI/UX Designer](agents/uiux_designer/SKILL.md)
- [CI/CD Engineer](agents/cicd_engineer/SKILL.md)
- [QA](agents/qa/SKILL.md)
- [Beta Tester](agents/beta_tester/SKILL.md)
- [KIS API Engineer](agents/kis_api_engineer/SKILL.md)
- [Execution Trader](agents/execution_trader/SKILL.md)
- [Compliance Officer](agents/compliance_officer/SKILL.md)
- [Performance Analyst](agents/performance_analyst/SKILL.md)
- [Quant Researcher](agents/quant_researcher/SKILL.md)
- [Backtest Engineer](agents/backtest_engineer/SKILL.md)
- [Data Engineer](agents/data_engineer/SKILL.md)
- [Optimization Quant](agents/optimization_quant/SKILL.md)

## Multi-Agent Execution (MANDATORY)

**모든 실질적 작업은 반드시 멀티에이전트로 수행한다. 이 규칙은 예외 없이 강제된다.**

1. **플랜이 있으면** `superpowers:subagent-driven-development` 스킬로 실행한다.
   - Task당 implementer 서브에이전트 1개 → spec reviewer → code quality reviewer 순서.
   - 리뷰가 이슈를 찾으면 implementer가 수정 → 재리뷰. 이슈가 없어야 다음 Task로 넘어간다.
2. **독립적인 작업 2개 이상이면** `superpowers:dispatching-parallel-agents`로 병렬 처리한다.
3. **백로그 자동화 사이클은** Ralph Loop(`/ralph-loop`)로 구동한다. 세션 시작 시 먼저 `python scripts/session_resume_check.py`로 상태를 확인하고, `.claude/ralph-loop.local.md`가 `active: true`이며 **신선하고** `agents/project/NEXT-SESSION-POINTER.yml`와 **일치할 때에만** 재개한다. 스테일·모순이면 재개하지 말고 포인터/STATUS를 권위로 삼아 reconcile한다.
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
