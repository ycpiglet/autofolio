# VIEW — TASK by Workload (cost & concentration)

> 이 파일은 `scripts/generate_views.py` 가 자동 생성한다. 직접 수정하지 말 것.
> 생성 시각: `2026-06-13T00:06:48+09:00`
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
| Lead Engineer | 8 | 8.0 ph | ~80K | 0.0 ph |
| QA | 4 | 6.0 ph | ~110K | 6.0 ph |
| Quant Researcher | 1 | 6.0 ph | ~55K | 0.0 ph |
| Compliance Officer | 1 | 5.0 ph | ~50K | 5.0 ph |
| Data Engineer | 1 | 5.0 ph | ~45K | 0.0 ph |
| Performance Analyst | 1 | 5.0 ph | ~45K | 0.0 ph |

## By Assignee (공동 작업 분할 반영)

| Assignee | TASKs | Hours (share) | Tokens (share) |
|----------|-------|---------------|----------------|
| KIS API Engineer | 22 | 62.3 ph | ~838K |
| QA | 13 | 23.2 ph | ~233K |
| Backend Engineer | 5 | 10.7 ph | ~101K |
| Lead Engineer | 8 | 8.0 ph | ~80K |
| Compliance Officer | 2 | 5.0 ph | ~43K |
| Data Engineer | 1 | 2.5 ph | ~22K |
| Quant Researcher | 1 | 2.0 ph | ~18K |
| Backtest Engineer | 1 | 2.0 ph | ~18K |
| Performance Analyst | 1 | 1.7 ph | ~15K |
| UI/UX Designer | 2 | 1.3 ph | ~22K |
| Research Agent | 1 | 0.3 ph | ~8K |
