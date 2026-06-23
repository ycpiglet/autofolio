# VIEW — TASK by Workload (cost & concentration)

> 이 파일은 `scripts/generate_views.py` 가 자동 생성한다. 직접 수정하지 말 것.
> 생성 시각: `2026-06-23T18:24:44+09:00`
> 원본: `agents/lead_engineer/tasks/TASK-*.md` 의 YAML frontmatter

필터링은 `python scripts/query_tasks.py --help` 참조.

---

> 누적 추정 비용 기준. 실측 비용은 TASK 본문 완료 기록에서 별도 추적.
> 자세한 경고(Critical/High 집중, 실측 누락)는 `python scripts/agent_scorecard.py` 참조.

## By Owner

| Owner | TASKs | Hours | Tokens | Critical/High Hours |
|-------|-------|-------|--------|---------------------|
| Backend Engineer | 36 | 141.0 ph | ~1274K | 100.0 ph |
| KIS API Engineer | 16 | 64.0 ph | ~830K | 13.0 ph |
| UI/UX Designer | 10 | 61.0 ph | ~540K | 31.0 ph |
| Lead Engineer | 21 | 54.5 ph | ~562K | 39.0 ph |
| QA | 5 | 18.0 ph | ~190K | 18.0 ph |
| Performance Analyst | 3 | 12.0 ph | ~110K | 0.0 ph |
| Quant Researcher | 2 | 10.0 ph | ~100K | 0.0 ph |
| Compliance Officer | 2 | 6.0 ph | ~68K | 6.0 ph |
| Research Agent | 3 | 6.0 ph | ~90K | 6.0 ph |
| Data Engineer | 1 | 5.0 ph | ~45K | 0.0 ph |
| CI/CD Engineer | 2 | 3.0 ph | ~41K | 0.0 ph |
| Doc Steward | 1 | 2.0 ph | ~30K | 2.0 ph |
| Regulatory Admin | 1 | 2.0 ph | ~35K | 0.0 ph |

## By Assignee (공동 작업 분할 반영)

| Assignee | TASKs | Hours (share) | Tokens (share) |
|----------|-------|---------------|----------------|
| QA | 72 | 96.2 ph | ~918K |
| Backend Engineer | 52 | 90.0 ph | ~779K |
| KIS API Engineer | 23 | 63.3 ph | ~850K |
| UI/UX Designer | 26 | 51.3 ph | ~469K |
| Lead Engineer | 48 | 36.1 ph | ~414K |
| Compliance Officer | 14 | 20.7 ph | ~192K |
| CI/CD Engineer | 5 | 6.1 ph | ~60K |
| Performance Analyst | 3 | 4.5 ph | ~40K |
| Doc Steward | 6 | 4.1 ph | ~50K |
| Quant Researcher | 2 | 3.3 ph | ~33K |
| Research Agent | 6 | 3.1 ph | ~50K |
| Data Engineer | 1 | 2.5 ph | ~22K |
| Backtest Engineer | 1 | 2.0 ph | ~18K |
| Regulatory Admin | 3 | 0.9 ph | ~14K |
| Business Planner | 1 | 0.2 ph | ~2K |
| Marketing Growth | 1 | 0.2 ph | ~2K |
