# VIEW — TASK by Workload (cost & concentration)

> 이 파일은 `scripts/generate_views.py` 가 자동 생성한다. 직접 수정하지 말 것.
> 생성 시각: `2026-06-21T17:10:46+09:00`
> 원본: `agents/lead_engineer/tasks/TASK-*.md` 의 YAML frontmatter

필터링은 `python scripts/query_tasks.py --help` 참조.

---

> 누적 추정 비용 기준. 실측 비용은 TASK 본문 완료 기록에서 별도 추적.
> 자세한 경고(Critical/High 집중, 실측 누락)는 `python scripts/agent_scorecard.py` 참조.

## By Owner

| Owner | TASKs | Hours | Tokens | Critical/High Hours |
|-------|-------|-------|--------|---------------------|
| Backend Engineer | 40 | 155.0 ph | ~1453K | 102.0 ph |
| Lead Engineer | 30 | 86.5 ph | ~868K | 69.0 ph |
| QA | 22 | 68.0 ph | ~815K | 23.0 ph |
| KIS API Engineer | 16 | 64.0 ph | ~830K | 13.0 ph |
| UI/UX Designer | 15 | 58.7 ph | ~519K | 21.7 ph |
| Compliance Officer | 12 | 36.0 ph | ~418K | 6.0 ph |
| Doc Steward | 9 | 26.0 ph | ~310K | 2.0 ph |
| Marketing Growth | 7 | 24.0 ph | ~280K | 7.0 ph |
| Performance Analyst | 3 | 12.0 ph | ~110K | 0.0 ph |
| Regulatory Admin | 3 | 11.0 ph | ~143K | 0.0 ph |
| Quant Researcher | 2 | 10.0 ph | ~100K | 0.0 ph |
| Business Planner | 3 | 9.0 ph | ~125K | 4.0 ph |
| Research Agent | 4 | 7.0 ph | ~105K | 7.0 ph |
| Finance Accounting | 2 | 6.0 ph | ~90K | 6.0 ph |
| Data Engineer | 1 | 5.0 ph | ~45K | 0.0 ph |
| CI/CD Engineer | 2 | 3.0 ph | ~41K | 0.0 ph |

## By Assignee (공동 작업 분할 반영)

| Assignee | TASKs | Hours (share) | Tokens (share) |
|----------|-------|---------------|----------------|
| QA | 135 | 133.7 ph | ~1374K |
| Backend Engineer | 66 | 100.6 ph | ~897K |
| KIS API Engineer | 28 | 65.4 ph | ~884K |
| Compliance Officer | 66 | 62.3 ph | ~668K |
| UI/UX Designer | 39 | 53.7 ph | ~505K |
| Lead Engineer | 64 | 43.0 ph | ~486K |
| Doc Steward | 61 | 41.5 ph | ~485K |
| Marketing Growth | 49 | 33.5 ph | ~397K |
| Research Agent | 11 | 9.7 ph | ~110K |
| Business Planner | 13 | 7.0 ph | ~92K |
| CI/CD Engineer | 5 | 6.1 ph | ~60K |
| Performance Analyst | 3 | 4.5 ph | ~40K |
| Regulatory Admin | 9 | 4.3 ph | ~60K |
| Quant Researcher | 2 | 3.3 ph | ~33K |
| Finance Accounting | 4 | 3.3 ph | ~47K |
| Data Engineer | 1 | 2.5 ph | ~22K |
| Backtest Engineer | 1 | 2.0 ph | ~18K |
| Beta Tester | 2 | 1.8 ph | ~30K |
| Managing Partner | 2 | 1.0 ph | ~13K |
| Lead Designer | 2 | 0.8 ph | ~12K |
| Requirements Interviewer | 1 | 0.8 ph | ~12K |
| Scribe | 1 | 0.3 ph | ~4K |
