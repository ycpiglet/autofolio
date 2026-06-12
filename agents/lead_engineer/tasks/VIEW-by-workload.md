# VIEW — TASK by Workload (cost & concentration)

> 이 파일은 `scripts/generate_views.py` 가 자동 생성한다. 직접 수정하지 말 것.
> 생성 시각: `2026-06-13T02:13:21+09:00`
> 원본: `agents/lead_engineer/tasks/TASK-*.md` 의 YAML frontmatter

필터링은 `python scripts/query_tasks.py --help` 참조.

---

> 누적 추정 비용 기준. 실측 비용은 TASK 본문 완료 기록에서 별도 추적.
> 자세한 경고(Critical/High 집중, 실측 누락)는 `python scripts/agent_scorecard.py` 참조.

## By Owner

| Owner | TASKs | Hours | Tokens | Critical/High Hours |
|-------|-------|-------|--------|---------------------|
| KIS API Engineer | 16 | 64.0 ph | ~830K | 13.0 ph |
| Backend Engineer | 3 | 20.0 ph | ~185K | 4.0 ph |
| Lead Engineer | 9 | 11.0 ph | ~115K | 0.0 ph |
| Quant Researcher | 2 | 10.0 ph | ~100K | 0.0 ph |
| Performance Analyst | 2 | 9.0 ph | ~90K | 0.0 ph |
| QA | 4 | 6.0 ph | ~110K | 6.0 ph |
| Research Agent | 3 | 6.0 ph | ~90K | 6.0 ph |
| Compliance Officer | 1 | 5.0 ph | ~50K | 5.0 ph |
| Data Engineer | 1 | 5.0 ph | ~45K | 0.0 ph |
| UI/UX Designer | 1 | 4.0 ph | ~45K | 4.0 ph |

## By Assignee (공동 작업 분할 반영)

| Assignee | TASKs | Hours (share) | Tokens (share) |
|----------|-------|---------------|----------------|
| KIS API Engineer | 23 | 63.3 ph | ~850K |
| QA | 20 | 30.2 ph | ~320K |
| Backend Engineer | 6 | 12.0 ph | ~116K |
| Lead Engineer | 12 | 11.0 ph | ~122K |
| UI/UX Designer | 5 | 5.3 ph | ~67K |
| Compliance Officer | 2 | 5.0 ph | ~43K |
| Quant Researcher | 2 | 3.3 ph | ~33K |
| Performance Analyst | 2 | 3.0 ph | ~30K |
| Data Engineer | 1 | 2.5 ph | ~22K |
| Research Agent | 4 | 2.3 ph | ~38K |
| Backtest Engineer | 1 | 2.0 ph | ~18K |
