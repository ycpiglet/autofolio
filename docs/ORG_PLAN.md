# Autofolio 조직 기획서 (ORG_PLAN)

> 상태: **기획 확정 / 구현 단계별 진행**
> 본 문서는 Autofolio의 *에이전트 조직(누가)* 을 정의한다. *무엇을·어떻게(제품/시스템)* 는 [PRODUCT_BLUEPRINT.md](PRODUCT_BLUEPRINT.md), 현재 구현된 두 팀의 상세는 [AGENT_TEAMS.md](AGENT_TEAMS.md) 참고.

---

## 1. 요약 — 4축 조직

Autofolio는 **4개의 축**으로 운영한다. 각 축은 목적·지식·산출물이 다르다.

```
① 개발팀 (Engineering)         — 시스템·인프라를 만든다             [부분 구현]
② 자산운용팀 (Discretionary)   — 재량적 뷰/판단 (한국·미국·글로벌)   [구현 완료]   ← 정성적 엣지(depth)
③ 퀀트 리서치팀 (Systematic)   — 시그널·백테스트·데이터·최적화       [설계 완료]   ← 정량적 엣지(breadth)
④ 의사결정·운영·통제 (Gov/Ops) — IC·Devil's Advocate·회고·컴플라이언스 [설계 완료]  ← 거버넌스
```

핵심 명제: **Autofolio는 Quantamental(퀀트+펀더멘털) + Agentic(멀티에이전트) 하이브리드다.** 엔진(`app/engine`)은 룰베이스 = 시스템적이고, 자산팀은 재량적 = 펀더멘털이다. 둘을 잇는 게 ③퀀트팀, 그 결정을 통제하는 게 ④거버넌스다.

---

## 2. 왜 4축인가 (근거)

- **전통 자산운용 ≠ 퀀트트레이딩.** 전자는 *깊이(depth)·판단*, 후자는 *폭(breadth)·규율*. 근본법칙 `IR ≈ IC × √Breadth` 에서 서로 다른 레버를 당긴다. ([SSGA](https://www.ssga.com/library-content/pdfs/insights/Quant-Investing-Comparing-and-Contrasting-Part-1-of-3.pdf) · [AQR](https://www.aqr.com/-/media/AQR/Documents/Insights/Alternative-Thinking/AQR-Alternative-Thinking--3Q17.pdf))
- **AI가 둘의 경계를 녹인다(Quantamental).** LLM이 정성·정량을 결합 → "best of both worlds". ([Modulor](https://modulorcapital.com/what-is-quantamental-investing/) · [RavenPack](https://www.ravenpack.com/blog/quant-fundamental-convergence))
- **2026 업계 표준이 멀티에이전트.** 헤지펀드 95%가 agentic 구조로 전환, Valuation·Sentiment·Fundamentals·Risk·PM 에이전트가 분업 — *Autofolio 자산팀 구조와 동일*. ([Two Sigma](https://www.twosigma.com/articles/ai-in-investment-management-2026-outlook-part-i/) · [TradingAgents](https://arxiv.org/html/2412.20138v5) · [AI in Hedge Funds](https://digiqt.com/blog/ai-agents-in-hedge-funds/))

---

## 3. 각 축 상세

### ① 개발팀 (Engineering) — [부분 구현]
시스템을 만든다. 상세: [AGENT_TEAMS.md](AGENT_TEAMS.md) §3.
**17 에이전트** — `ycpiglet/agent_runtime` 16종 이식(ceo·owner·managing-partner·lead-engineer·backend-engineer·cicd-engineer·uiux-designer·qa·beta-tester·independent-auditor·requirements-interviewer·research-agent·doc-steward·scribe·secretary·timeline-agent) + Autofolio 전용 `kis-api-engineer`.

> 향후 보강 후보: **Data Engineer**(데이터 파이프라인 — ③과 인접), **DevOps/Release**(스케줄러·배포 — auto 모드 운영).

### ② 자산운용팀 (Discretionary Research) — [구현 완료]
재량적 뷰/판단. 상세: [AGENT_TEAMS.md](AGENT_TEAMS.md) §2 (leadership / korea-desk / us-desk / global-desk, 15 에이전트).

### ③ 퀀트 리서치팀 (Systematic / Quant) — [설계 완료, 구현 대기]
자산팀(판단)과 개발팀(엔진)의 **교집합**에 사는 다리. 정성적 뷰를 *정량적으로 검증·코드화*한다. **엔진이 룰베이스인 이상 반드시 채워야 할 빈칸.**

| 제안 에이전트 | 직책 | 책임 | 전담 스킬(예정) |
|---|---|---|---|
| `autofolio-quant-researcher` | 퀀트 리서처 | 팩터·시그널 리서치(모멘텀·밸류·퀄리티·로우볼), 가설 수립 | `quant-signal-research` |
| `autofolio-backtest-engineer` | 백테스트 엔지니어 | 가설 검증, **look-ahead bias·과최적화·생존편향 방어**, point-in-time | `backtesting-methodology` |
| `autofolio-data-engineer` | 데이터 엔지니어 | 시장·대체데이터 파이프라인·품질 (개발팀과 공유 가능) | `market-data-pipeline` |
| `autofolio-optimization-quant` | 최적화·리스크 퀀트 | 팩터노출·공분산·포지션 최적화 (기존 risk-manager 정량 확장) | `portfolio-optimization` |

> ⚠️ 핵심 가드레일: 백테스트는 **look-ahead bias** 로 오염되기 쉽다. point-in-time 데이터·아웃오브샘플 검증·실거래 전 페이퍼 검증을 의무화한다. ([Look-Ahead-Bench](https://arxiv.org/pdf/2601.13770))

### ④ 의사결정·운영·통제 (Governance & Ops) — [설계 완료, 구현 대기]
뷰가 *결정*이 되는 과정과 사후 통제. 에이전트(역할) + 프로세스(워크플로) + 기록(아티팩트) 3겹.

**에이전트(역할)**
| 제안 에이전트 | 직책 | 책임 |
|---|---|---|
| `autofolio-devils-advocate` | 악마의 변호인 | 모든 제안에 반대 케이스·pre-mortem·반증 강제 (집단사고 차단) |
| `autofolio-performance-analyst` | 성과·회고 분석가 | SQLite 로그 기반 손익 기여(attribution)·패자 부검·교훈 추출 |
| `autofolio-execution-trader` | 실행 트레이더 | 승인된 결정의 주문 타이밍·지정/시장·분할 전략 자문 |
| `autofolio-compliance-officer` | 컴플라이언스 | IPS·mandate·화이트리스트·킬스위치 *규정 준수* 점검 (시장리스크와 별개) |

**프로세스(워크플로 = 의사결정 로직)** → 슬래시 커맨드/스킬로 구현
- **`/ic` 투자위원회**: 전문가 뷰 수집 → Devil's Advocate 반박 → 리스크·컴플라이언스 게이트 → PM 종합 → CIO 결정 → **결정 로그 기록(반대의견 포함)**.
- **장전 체크리스트 / pre-trade gate**: 제안이 라이브 되기 전 통과 관문.
- **`/retro` 정기 회고**: 거래별 등급·이유 기록, 주/월 승률·R·규율 리뷰.

**기록(아티팩트)** = 조직의 기억 → `docs/decisions/`(결정 로그), 트레이드 저널(DB 테이블/마크다운). "자가개선" 루프의 연료.

> 근거: 기관은 devil's advocate·pre-mortem·결정문서화로 groupthink를 막는다. ([CFA](https://blogs.cfainstitute.org/investor/2015/04/29/investment-decisions-how-to-avoid-groupthink/) · [거버넌스 심리](https://ioandc.com/the-psychology-of-investment-governance-how-committees-overcome-behavioral-bias/)). 개인 손실의 대부분은 전략이 아니라 *프로세스 붕괴*에서 온다. ([트레이딩 저널](https://wealthbee.io/learn/trading-journal-emotional-discipline-checklist/))

---

## 4. Quantamental 의사결정 워크플로 (핵심 로직)

```
자산팀 정성 뷰  ─┐
                ├─→ 퀀트팀 정량 검증 ─→ IC 토론 ─→ CIO 결정 ─→ [사람 승인 / auto] ─→ 엔진 실행 ─→ 회고·Attribution ─┐
매크로·데이터  ─┘   (백테스트·시그널)   (+Devil's Advocate)            ↑                                              │
                                          Risk·Compliance 게이트 ──────┘                  학습 루프 ────────────────────┘
```

- 자산팀의 *깊이* 와 퀀트팀의 *폭·규율* 이 상호 견제·보완(quantamental).
- 모든 결정은 IC를 거쳐 **기록**되고, 실행 결과는 회고로 **학습 루프**에 환류된다.
- 실행 직전 게이트는 항상 **Risk + Compliance**. 자동(auto) 모드에서도 이 게이트는 유지된다([PRODUCT_BLUEPRINT.md](PRODUCT_BLUEPRINT.md) §2·§7).

---

## 5. AI 시장 정렬 — Autofolio가 메인스트림인 이유

| 2026 업계 동향 | Autofolio 대응 |
|---|---|
| Agentic AI가 운용의 **OS화** | "Agentic Quant Portfolio OS" (MVP_SPEC §1.3) |
| 멀티에이전트 분업이 표준 | 4축 20+ 에이전트 조직 |
| **Human-in-the-loop**이 베스트프랙티스 (AlphaGPT 등) | "제안만 / 사람 승인" 가드레일 (MVP_SPEC §6.6) |
| 리서치 깔때기 역전(아이디어 검증이 병목) | ③퀀트팀 백테스트 루프 |
| LLM 환각·look-ahead·alpha decay 위험 | 백테스트 검증·point-in-time·킬스위치 |

---

## 6. 구현 상태 매트릭스

| 축 | 구성요소 | 상태 |
|---|---|---|
| ① 개발팀 | 5 에이전트 | ✅ 구현 |
| ② 자산운용팀 | 15 에이전트 + 15 스킬 | ✅ 구현 |
| ③ 퀀트팀 | 4 에이전트 + 4 스킬 | 📐 설계완료 · 구현대기 |
| ④ 거버넌스 | Devils-Advocate 에이전트 + IC 워크플로(`app/ui/ic.py`)+결정로그 ✅ P2 / 나머지 3 에이전트 📐 대기 | 🔄 부분구현 |
| 에이전트 실연결 | Anthropic API 페르소나 구동(`app/ui/agents_runtime.py`) | ✅ P2 (키 없으면 스텁) |

## 7. 다음 단계 (조직 측면)
1. ③퀀트팀 에이전트·스킬 생성 (+ `app/` 백테스트 모듈은 개발팀과 협업).
2. ④거버넌스: Devil's Advocate·Performance 분석가 먼저 → `/ic`·`/retro` 커맨드 → 결정/저널 로그.
3. 제품/시스템 로드맵은 [PRODUCT_BLUEPRINT.md](PRODUCT_BLUEPRINT.md) §8과 동기화.
