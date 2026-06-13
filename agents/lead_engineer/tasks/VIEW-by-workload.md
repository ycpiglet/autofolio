# VIEW — TASK by Workload (cost & concentration)

> 이 파일은 `scripts/generate_views.py` 가 자동 생성한다. 직접 수정하지 말 것.
> 생성 시각: `2026-06-14T04:00:18+09:00`
> 원본: `agents/lead_engineer/tasks/TASK-*.md` 의 YAML frontmatter

필터링은 `python scripts/query_tasks.py --help` 참조.

---

> 누적 추정 비용 기준. 실측 비용은 TASK 본문 완료 기록에서 별도 추적.
> 자세한 경고(Critical/High 집중, 실측 누락)는 `python scripts/agent_scorecard.py` 참조.

## By Owner

| Owner | TASKs | Hours | Tokens | Critical/High Hours |
|-------|-------|-------|--------|---------------------|
| Backend Engineer | 8 | 75.0 ph | ~600K | 47.0 ph |
| KIS API Engineer | 16 | 64.0 ph | ~830K | 13.0 ph |
| UI/UX Designer | 4 | 34.0 ph | ~270K | 4.0 ph |
| Lead Engineer | 9 | 11.0 ph | ~115K | 0.0 ph |
| Quant Researcher | 2 | 10.0 ph | ~100K | 0.0 ph |
| Performance Analyst | 2 | 9.0 ph | ~90K | 0.0 ph |
| QA | 4 | 6.0 ph | ~110K | 6.0 ph |
| Research Agent | 3 | 6.0 ph | ~90K | 6.0 ph |
| Compliance Officer | 1 | 5.0 ph | ~50K | 5.0 ph |
| Data Engineer | 1 | 5.0 ph | ~45K | 0.0 ph |
| Doc Steward | 1 | 2.0 ph | ~30K | 2.0 ph |

## By Assignee (공동 작업 분할 반영)

| Assignee | TASKs | Hours (share) | Tokens (share) |
|----------|-------|---------------|----------------|
| KIS API Engineer | 23 | 63.3 ph | ~850K |
| Backend Engineer | 13 | 46.8 ph | ~378K |
| QA | 26 | 46.5 ph | ~448K |
| UI/UX Designer | 10 | 31.7 ph | ~264K |
| Compliance Officer | 4 | 13.0 ph | ~103K |
| Lead Engineer | 13 | 11.5 ph | ~129K |
| Quant Researcher | 2 | 3.3 ph | ~33K |
| Performance Analyst | 2 | 3.0 ph | ~30K |
| Research Agent | 5 | 2.8 ph | ~46K |
| Data Engineer | 1 | 2.5 ph | ~22K |
| Backtest Engineer | 1 | 2.0 ph | ~18K |
| Doc Steward | 1 | 0.5 ph | ~8K |
