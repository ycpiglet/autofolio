# VIEW — TASK by Workload (cost & concentration)

> 이 파일은 `scripts/generate_views.py` 가 자동 생성한다. 직접 수정하지 말 것.
> 생성 시각: `2026-06-15T00:37:54+09:00`
> 원본: `agents/lead_engineer/tasks/TASK-*.md` 의 YAML frontmatter

필터링은 `python scripts/query_tasks.py --help` 참조.

---

> 누적 추정 비용 기준. 실측 비용은 TASK 본문 완료 기록에서 별도 추적.
> 자세한 경고(Critical/High 집중, 실측 누락)는 `python scripts/agent_scorecard.py` 참조.

## By Owner

| Owner | TASKs | Hours | Tokens | Critical/High Hours |
|-------|-------|-------|--------|---------------------|
| Backend Engineer | 17 | 117.0 ph | ~892K | 82.0 ph |
| KIS API Engineer | 16 | 64.0 ph | ~830K | 13.0 ph |
| UI/UX Designer | 8 | 44.0 ph | ~342K | 14.0 ph |
| QA | 5 | 18.0 ph | ~190K | 18.0 ph |
| Lead Engineer | 11 | 15.0 ph | ~145K | 2.0 ph |
| Performance Analyst | 3 | 12.0 ph | ~110K | 0.0 ph |
| Quant Researcher | 2 | 10.0 ph | ~100K | 0.0 ph |
| Research Agent | 3 | 6.0 ph | ~90K | 6.0 ph |
| Compliance Officer | 1 | 5.0 ph | ~50K | 5.0 ph |
| Data Engineer | 1 | 5.0 ph | ~45K | 0.0 ph |
| Doc Steward | 1 | 2.0 ph | ~30K | 2.0 ph |

## By Assignee (공동 작업 분할 반영)

| Assignee | TASKs | Hours (share) | Tokens (share) |
|----------|-------|---------------|----------------|
| QA | 40 | 78.5 ph | ~670K |
| Backend Engineer | 23 | 73.8 ph | ~564K |
| KIS API Engineer | 23 | 63.3 ph | ~850K |
| UI/UX Designer | 14 | 36.7 ph | ~300K |
| Lead Engineer | 16 | 15.0 ph | ~154K |
| Compliance Officer | 4 | 13.0 ph | ~103K |
| Performance Analyst | 3 | 4.5 ph | ~40K |
| Quant Researcher | 2 | 3.3 ph | ~33K |
| Research Agent | 5 | 2.8 ph | ~46K |
| Data Engineer | 1 | 2.5 ph | ~22K |
| Doc Steward | 3 | 2.5 ph | ~22K |
| Backtest Engineer | 1 | 2.0 ph | ~18K |
