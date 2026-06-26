# VIEW — TASK by Workload (cost & concentration)

> 이 파일은 `scripts/generate_views.py` 가 자동 생성한다. 직접 수정하지 말 것.
> 생성 시각: `2026-06-26T19:08:56+09:00`
> 원본: `agents/lead_engineer/tasks/TASK-*.md` 의 YAML frontmatter

필터링은 `python scripts/query_tasks.py --help` 참조.

---

> 누적 추정 비용 기준. 실측 비용은 TASK 본문 완료 기록에서 별도 추적.
> 자세한 경고(Critical/High 집중, 실측 누락)는 `python scripts/agent_scorecard.py` 참조.

## By Owner

| Owner | TASKs | Hours | Tokens | Critical/High Hours |
|-------|-------|-------|--------|---------------------|
| Backend Engineer | 39 | 153.0 ph | ~1429K | 100.0 ph |
| Lead Engineer | 25 | 75.5 ph | ~749K | 60.0 ph |
| UI/UX Designer | 11 | 66.0 ph | ~610K | 31.0 ph |
| KIS API Engineer | 16 | 64.0 ph | ~830K | 13.0 ph |
| Marketing Growth | 7 | 24.0 ph | ~280K | 7.0 ph |
| QA | 5 | 18.0 ph | ~190K | 18.0 ph |
| Performance Analyst | 3 | 12.0 ph | ~110K | 0.0 ph |
| Quant Researcher | 2 | 10.0 ph | ~100K | 0.0 ph |
| Business Planner | 3 | 9.0 ph | ~125K | 4.0 ph |
| Compliance Officer | 2 | 6.0 ph | ~68K | 6.0 ph |
| Research Agent | 3 | 6.0 ph | ~90K | 6.0 ph |
| Finance Accounting | 2 | 6.0 ph | ~90K | 6.0 ph |
| Data Engineer | 1 | 5.0 ph | ~45K | 0.0 ph |
| Doc Steward | 2 | 5.0 ph | ~65K | 2.0 ph |
| Regulatory Admin | 2 | 3.0 ph | ~53K | 0.0 ph |
| CI/CD Engineer | 2 | 3.0 ph | ~41K | 0.0 ph |

## By Assignee (공동 작업 분할 반영)

| Assignee | TASKs | Hours (share) | Tokens (share) |
|----------|-------|---------------|----------------|
| QA | 89 | 106.9 ph | ~1055K |
| Backend Engineer | 60 | 96.1 ph | ~852K |
| KIS API Engineer | 23 | 63.3 ph | ~850K |
| UI/UX Designer | 30 | 53.8 ph | ~502K |
| Lead Engineer | 55 | 43.5 ph | ~483K |
| Compliance Officer | 34 | 38.3 ph | ~388K |
| Doc Steward | 20 | 12.0 ph | ~146K |
| Marketing Growth | 17 | 9.5 ph | ~117K |
| Research Agent | 9 | 9.2 ph | ~101K |
| CI/CD Engineer | 5 | 6.1 ph | ~60K |
| Business Planner | 12 | 5.4 ph | ~74K |
| Performance Analyst | 3 | 4.5 ph | ~40K |
| Quant Researcher | 2 | 3.3 ph | ~33K |
| Finance Accounting | 4 | 3.3 ph | ~47K |
| Regulatory Admin | 8 | 2.7 ph | ~42K |
| Data Engineer | 1 | 2.5 ph | ~22K |
| Backtest Engineer | 1 | 2.0 ph | ~18K |
| Managing Partner | 2 | 1.0 ph | ~13K |
| Beta Tester | 1 | 1.0 ph | ~14K |
| Requirements Interviewer | 1 | 0.8 ph | ~12K |
| Scribe | 1 | 0.3 ph | ~4K |
