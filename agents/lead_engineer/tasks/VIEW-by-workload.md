# VIEW — TASK by Workload (cost & concentration)

> 이 파일은 `scripts/generate_views.py` 가 자동 생성한다. 직접 수정하지 말 것.
> 생성 시각: `2026-06-11T19:38:32+09:00`
> 원본: `agents/lead_engineer/tasks/TASK-*.md` 의 YAML frontmatter

필터링은 `python scripts/query_tasks.py --help` 참조.

---

> 누적 추정 비용 기준. 실측 비용은 TASK 본문 완료 기록에서 별도 추적.
> 자세한 경고(Critical/High 집중, 실측 누락)는 `python scripts/agent_scorecard.py` 참조.

## By Owner

| Owner | TASKs | Hours | Tokens | Critical/High Hours |
|-------|-------|-------|--------|---------------------|
| KIS API Engineer | 14 | 49.0 ph | ~700K | 13.0 ph |
| UI/UX Designer | 3 | 10.0 ph | ~115K | 7.0 ph |
| Lead Engineer | 1 | 3.0 ph | ~35K | 3.0 ph |
| QA | 1 | 3.0 ph | ~30K | 0.0 ph |

## By Assignee (공동 작업 분할 반영)

| Assignee | TASKs | Hours (share) | Tokens (share) |
|----------|-------|---------------|----------------|
| KIS API Engineer | 14 | 49.0 ph | ~700K |
| UI/UX Designer | 5 | 9.0 ph | ~102K |
| QA | 3 | 4.5 ph | ~50K |
| Lead Engineer | 1 | 1.5 ph | ~18K |
| Doc Steward | 1 | 1.0 ph | ~10K |
