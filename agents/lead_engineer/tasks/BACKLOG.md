# BACKLOG — 의사결정 보드 (repo-canonical)

> **이것이 "지금 무엇이 열려 있고 다음에 무엇을 하나"의 단일 출처다.**
> 어느 세션/PC/OS/에이전트/사용자든 작업 시작 시 `git pull` 후 이 파일과
> `python scripts/backlog_sweep.py`(due-check 등 런타임 신호 포함)를 본다.
> `scripts/generate_views.py` 가 TASK frontmatter 에서 생성 → 드리프트 불가. **직접 수정 금지.**
> **규칙(COMPOUND-032): 열린 작업은 전부 TASK 로 존재해야 한다** — 메모리·프로세 "다음:" 한 줄에만 두지 말 것
> (로컬 메모리는 PC/사용자별이라 공유 불가 → 다른 세션이 못 봐서 중복작업이 생긴다).
> 생성 시각: `2026-06-11T08:04:33+09:00` · 열린 작업 14건

---

## 표시 원칙

- `ACT`: 가역(R1/R2)이라 승인 없이 진행 가능.
- `REVIEW`: 일부는 자율 가능하지만 R3/Owner 경계가 있어 마무리 전 확인 필요.
- `ASK`: Owner 승인, 외부 계정/결제/secret 등 없이는 진행 불가.
- `DEFER`: 지금은 일부러 미루는 것이 안전하거나 가치가 낮음.
- `score`: 우선순위, 실행 가능성, 예상 시간을 섞은 정렬용 휴리스틱이다. 절대값이 아니라 줄세우기 기준이다.

## 한눈에 보기

| 지표 | 값 | 해석 |
|------|----|------|
| 열린 작업 | 14건 / 49 ph | frontmatter 기준 |
| 진행 중 WIP | 0건 | WIP 적정 |
| 대기 | 14건 | 최상위 자율 후보: TASK-023 (kis engine E2E validation) |
| 보류 | 0건 | Owner/외부 조건 또는 의도적 defer |
| 실행성 | ACT 14 / REVIEW 0 / ASK 0 / DEFER 0 | ACT는 승인 없이 진행 가능, ASK/DEFER는 멈춤 |

**빠른 판단:** 새로 하나를 고른다면 **TASK-023**. 다만 현재 WIP가 0건이라, 먼저 진행 중 항목을 줄이는 편이 흐름에 유리하다.

## 결정 레인

### ACT — 자율 진행

| Rank | Task | 결정 | 상태 | 중요도 | 시간 | 가치/이유 | 다음 행동 |
|------|------|------|------|--------|------|-----------|-----------|
| 1 | [TASK-023](TASK-023-kis-engine-e2e-validation.md) kis engine E2E validation | ACT | 대기 | High / score 40 | S · 2 ph | 회귀 리스크 감소 | 바로 착수 후보 |
| 2 | [TASK-011](TASK-011-kis-intraday-chart.md) kis intraday chart | ACT | 대기 | High / score 39 | M · 3 ph | 높은 가치 | 바로 착수 후보 |
| 3 | [TASK-010](TASK-010-kis-websocket-realtime.md) kis websocket realtime | ACT | 대기 | High / score 34 | L · 8 ph | 높은 가치 | 바로 착수 후보 |
| 4 | [TASK-012](TASK-012-kis-long-term-order-history.md) kis long term order history | ACT | 대기 | Medium / score 30 | S · 2 ph | 중간 가치 | 바로 착수 후보 |
| 5 | [TASK-013](TASK-013-kis-batch-price.md) kis batch price | ACT | 대기 | Medium / score 30 | S · 2 ph | 중간 가치 | 바로 착수 후보 |
| 6 | [TASK-014](TASK-014-kis-after-hours-order.md) kis after hours order | ACT | 대기 | Medium / score 29 | M · 3 ph | 중간 가치 | 바로 착수 후보 |
| 7 | [TASK-015](TASK-015-kis-index-price.md) kis index price | ACT | 대기 | Low / score 21 | XS · 1 ph | 낮은/위생 | 바로 착수 후보 |
| 8 | [TASK-017](TASK-017-kis-dividend-info.md) kis dividend info | ACT | 대기 | Low / score 20 | S · 2 ph | 낮은/위생 | 바로 착수 후보 |
| 9 | [TASK-019](TASK-019-kis-sector-price.md) kis sector price | ACT | 대기 | Low / score 20 | S · 2 ph | 낮은/위생 | 바로 착수 후보 |
| 10 | [TASK-018](TASK-018-kis-order-book.md) kis order book | ACT | 대기 | Low / score 19 | M · 3 ph | 낮은/위생 | 바로 착수 후보 |
| 11 | [TASK-020](TASK-020-kis-disclosure.md) kis disclosure | ACT | 대기 | Low / score 19 | M · 3 ph | 낮은/위생 | 바로 착수 후보 |
| 12 | [TASK-016](TASK-016-kis-fundamental-data.md) kis fundamental data | ACT | 대기 | Low / score 18 | M · 4 ph | 낮은/위생 | 바로 착수 후보 |
| 13 | [TASK-021](TASK-021-kis-margin-short.md) kis margin short | ACT | 대기 | Low / score 16 | L · 6 ph | 낮은/위생 | 바로 착수 후보 |
| 14 | [TASK-022](TASK-022-kis-overseas-order.md) kis overseas order | ACT | 대기 | Low / score 14 | L · 8 ph | 낮은/위생 | 바로 착수 후보 |

## 흐름 보드

### 대기 (next)

| ID | 우선순위 | Owner | 예상 | 게이트 / 태그 |
|----|----------|-------|------|----------------|
| [TASK-010](TASK-010-kis-websocket-realtime.md) | High | KIS API Engineer | 8 ph / ~50000 tok | kis,websocket,realtime |
| [TASK-011](TASK-011-kis-intraday-chart.md) | High | KIS API Engineer | 3 ph / ~50000 tok | kis,chart,intraday |
| [TASK-023](TASK-023-kis-engine-e2e-validation.md) | High | KIS API Engineer | 2 ph / ~50000 tok | kis,engine,e2e,validation |
| [TASK-012](TASK-012-kis-long-term-order-history.md) | Medium | KIS API Engineer | 2 ph / ~50000 tok | kis,history |
| [TASK-013](TASK-013-kis-batch-price.md) | Medium | KIS API Engineer | 2 ph / ~50000 tok | kis,price,performance |
| [TASK-014](TASK-014-kis-after-hours-order.md) | Medium | KIS API Engineer | 3 ph / ~50000 tok | kis,order,after-hours |
| [TASK-015](TASK-015-kis-index-price.md) | Low | KIS API Engineer | 1 ph / ~50000 tok | kis,index |
| [TASK-016](TASK-016-kis-fundamental-data.md) | Low | KIS API Engineer | 4 ph / ~50000 tok | kis,fundamental,research |
| [TASK-017](TASK-017-kis-dividend-info.md) | Low | KIS API Engineer | 2 ph / ~50000 tok | kis,dividend |
| [TASK-018](TASK-018-kis-order-book.md) | Low | KIS API Engineer | 3 ph / ~50000 tok | kis,orderbook,realtime |
| [TASK-019](TASK-019-kis-sector-price.md) | Low | KIS API Engineer | 2 ph / ~50000 tok | kis,sector |
| [TASK-020](TASK-020-kis-disclosure.md) | Low | KIS API Engineer | 3 ph / ~50000 tok | kis,disclosure,compliance |
| [TASK-021](TASK-021-kis-margin-short.md) | Low | KIS API Engineer | 6 ph / ~50000 tok | kis,margin,short |
| [TASK-022](TASK-022-kis-overseas-order.md) | Low | KIS API Engineer | 8 ph / ~50000 tok | kis,overseas,us-stocks |

