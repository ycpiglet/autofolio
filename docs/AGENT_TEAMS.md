# Autofolio 에이전트 조직 (Agent Teams)

> 📚 관련 기획서: [ORG_PLAN.md](ORG_PLAN.md)(4축 조직 전체 그림) · [PRODUCT_BLUEPRINT.md](PRODUCT_BLUEPRINT.md)(제품·시스템 설계) · [README.md](README.md)(문서 맵). 본 문서는 **현재 구현된 ①개발팀·②자산운용팀**의 상세다. 퀀트팀(③)·거버넌스(④)는 ORG_PLAN에 설계됨(구현 대기).

Autofolio는 (현재) 두 개의 **서로 다른 에이전트 팀**으로 운영된다.

1. **개발팀 (Dev Team)** — Autofolio라는 *소프트웨어*를 만든다. (Python, KIS Open API, Streamlit, SQLite)
2. **개인자산운용팀 (Asset Management Team)** — Autofolio로 *돈을 굴린다*. (리서치, 자산배분, 조건 제안)

두 팀은 목적·지식·산출물이 완전히 다르므로 에이전트 정의와 디렉토리를 분리한다.

```
.claude/
├── agents/
│   ├── dev-team/      ← 소프트웨어를 만드는 사람들 (5)
│   └── asset-team/    ← 돈을 굴리는 사람들 (15)
│       ├── leadership/   ← 전 지역 총괄 (CIO·PM·매크로·리스크)
│       ├── korea-desk/   ← 한국 현금시장
│       ├── us-desk/      ← 미국 현금시장
│       └── global-desk/  ← 자산군(파생·원자재·FX) 글로벌
└── skills/            ← 자산팀 전문가별 도메인 지식(스킬) 15종
```

---

## 1. 리서치 요약: 자산운용 조직 + 지역 구성

### 1.1 위계(계급)
표준 자산운용사 프런트오피스 위계: **CIO → Portfolio Manager → 자산군 전문가/전략가**, 이를 가로지르는 **Risk Manager(견제·통제)**.

- **CIO(최고투자책임자)** — 투자 철학·전략적 자산배분 총괄. PM이 보고.
- **Portfolio Manager** — 전략을 실제 비중·주문으로 구현.
- **Specialist/Analyst(자산군 전문가)** — 주식·채권·ETF·펀드 등 리서치.
- **Macro Strategist** — 거시·금리·환율 하우스뷰.
- **Risk Manager** — 미들오피스에서 리스크 통제.

출처: [CFA Institute](https://www.cfainstitute.org/programs/cfa-program/careers/portfolio-manager) · [OpsDog](https://opsdog.com/categories/organization-charts/asset-management) · [Financial Edge](https://www.fe.training/free-resources/asset-management/types-of-roles-in-asset-management/) · [300Hours](https://300hours.com/wealth-management-career-path/)

### 1.2 한국/미국 팀을 따로 둘 것인가? — 설계 결정
**결론: 부분 분리(하이브리드)가 최적.**

| 축 | 분리 기준 | 이유 |
|---|---|---|
| **현금시장(주식·채권·ETF·펀드)** | **지역별 데스크(한국/미국)** | 시장·거래시간·규제·세제·통화·데이터 소스가 다르고 **로컬 전문성**이 성과를 좌우. KOSPI 밸류에이션과 S&P 밸류에이션, 국고채와 US Treasury는 별개 도메인. |
| **파생·원자재·FX(선물·옵션·현물·통화)** | **글로벌 자산군 데스크(지역 무관)** | 이들은 *자산군의 메커니즘*(레버리지·롤·그릭스·환)이 본질이고 지역색이 약함. KOSPI200 선물과 ES 선물은 같은 "선물" 지식을 공유. |
| **총괄·통제(CIO·PM·매크로·리스크)** | **전 지역 단일(global)** | 매크로(Fed↔BOK, USD/KRW)와 리스크·배분은 두 지역을 *연결*해야 의미가 있음. 분리하면 통합 뷰가 깨짐. |

→ 그래서 **leadership(글로벌) + korea-desk + us-desk + global-desk** 4블록 구조.

---

## 2. 개인자산운용팀 (Asset Management Team) — 15 에이전트

### 2.1 Leadership (전 지역 총괄)
| 에이전트 | 직책 | 스킬 | 책임 |
|---|---|---|---|
| `autofolio-cio` | 최고투자책임자 | `investment-policy` | 투자철학·전략적 자산배분·최종 종합 |
| `autofolio-portfolio-manager` | 포트폴리오 매니저 | `portfolio-construction` | 배분을 비중·리밸런싱·목표가 조건으로 구현 |
| `autofolio-macro-strategist` | 매크로 전략가 | `macro-strategy` | 한·미·글로벌 거시/금리/환율 하우스뷰 |
| `autofolio-risk-manager` | 리스크 매니저 | `risk-management` | 사이징·드로다운·안전한도 견제 |

### 2.2 Korea Desk (한국 현금시장)
| 에이전트 | 직책 | 스킬 |
|---|---|---|
| `autofolio-kr-equity-specialist` | 국내주식 전문가 | `kr-equity-research` |
| `autofolio-kr-etf-specialist` | 국내(KRX) ETF 전문가 | `kr-etf-research` |
| `autofolio-kr-fund-specialist` | 펀드 전문가(공모펀드) | `kr-fund-research` |
| `autofolio-kr-fixed-income-specialist` | 채권 전문가(국고채·회사채) | `kr-fixed-income-research` |

### 2.3 US Desk (미국 현금시장)
| 에이전트 | 직책 | 스킬 |
|---|---|---|
| `autofolio-us-equity-specialist` | 미국주식 전문가 | `us-equity-research` |
| `autofolio-us-etf-specialist` | 미국 상장 ETF 전문가 | `us-etf-research` |
| `autofolio-us-fixed-income-specialist` | 미국채권 전문가(Treasury·credit) | `us-fixed-income-research` |

### 2.4 Global Desk (자산군 / 지역 무관)
| 에이전트 | 직책 | 스킬 |
|---|---|---|
| `autofolio-commodities-specialist` | 원자재·현물 전문가(금·은·원유·구리) | `commodities-research` |
| `autofolio-futures-specialist` | 선물 전문가(지수·상품 선물) | `futures-research` |
| `autofolio-options-specialist` | 옵션 전문가(그릭스·헤지·인컴) | `options-research` |
| `autofolio-fx-specialist` | 외환 전문가(USD/KRW·환헤지) | `fx-research` |

### 2.5 의사결정·승인 흐름
```
[korea-desk] 주식·ETF·펀드·채권 ─┐
[us-desk]    주식·ETF·채권       ─┤
[global-desk] 원자재·선물·옵션·FX ─┼─→ Portfolio Manager ─→ CIO(종합) ─→ [사람 최종 승인] ─→ 엔진 실행
                                  │        ↑
            Macro Strategist(하우스뷰) ────┘
            Risk Manager(전 단계 견제) ─────┘
```
- FX 전문가는 모든 해외(us-desk/global-desk) 제안에 **환 레이어**를 덧입힌다.
- 매크로 전략가는 한·미 데스크와 글로벌 데스크에 공통 하우스뷰를 공급한다.

### ⚠️ 안전 가드레일 (MVP_SPEC §6.6 준수)
- 자산팀 에이전트는 **제안·분석만** 한다. 조건 자동저장·자동매매 ON·직접 주문·비화이트리스트 자동편입·실전 주문 권한 **전부 금지**.
- 실행은 **사람의 명시적 승인** 후 `app/engine`을 통해서만.
- **파생·레버리지·원자재 현물(선물·옵션·commodities)·FX 헤지는 현 MVP 엔진 실행 범위 밖**이다. 해당 에이전트는 *교육·자문 한정*이며, 실제 자금 집행은 사람이 책임진다. (현 엔진의 실행 대상은 국장 ETF/대형주 화이트리스트.)

---

## 3. 개발팀 (Dev Team) — 17 에이전트

`ycpiglet/agent_runtime` 레포의 **16개 에이전트를 Claude Code 포맷으로 이식**(각 본문은 원본 `SKILL.md` 보존, 프론트매터만 부여)하고, Autofolio 전용 `kis-api-engineer`를 유지했다.

| 그룹 | 에이전트 |
|---|---|
| 리더십 | `autofolio-ceo` · `autofolio-owner` · `autofolio-managing-partner` · `autofolio-lead-engineer` |
| 엔지니어링 | `autofolio-backend-engineer` · `autofolio-cicd-engineer` · `autofolio-uiux-designer` · `autofolio-kis-api-engineer`(전용) |
| 품질 | `autofolio-qa` · `autofolio-beta-tester` · `autofolio-independent-auditor` |
| 지원/프로세스 | `autofolio-requirements-interviewer` · `autofolio-research-agent` · `autofolio-doc-steward` · `autofolio-scribe` · `autofolio-secretary` · `autofolio-timeline-agent` |

> 이식 시 일부 본문에 원본 레포 기준 상대경로 링크(예: `../lead_engineer/retros/...`)가 남아 있을 수 있다(원본 충실 보존). 필요 시 후속 정리.

---

## 4. 디렉토리 구조

```
.claude/
├── agents/
│   ├── dev-team/   (17 — agent_runtime 이식 + kis-api 전용)
│   │   ├── ceo.md · owner.md · managing-partner.md · lead-engineer.md
│   │   ├── backend-engineer.md · cicd-engineer.md · uiux-designer.md · kis-api-engineer.md
│   │   ├── qa.md · beta-tester.md · independent-auditor.md
│   │   └── requirements-interviewer.md · research-agent.md · doc-steward.md · scribe.md · secretary.md · timeline-agent.md
│   └── asset-team/
│       ├── leadership/
│       │   ├── cio.md
│       │   ├── portfolio-manager.md
│       │   ├── macro-strategist.md
│       │   └── risk-manager.md
│       ├── korea-desk/
│       │   ├── kr-equity-specialist.md
│       │   ├── kr-etf-specialist.md
│       │   ├── kr-fund-specialist.md
│       │   └── kr-fixed-income-specialist.md
│       ├── us-desk/
│       │   ├── us-equity-specialist.md
│       │   ├── us-etf-specialist.md
│       │   └── us-fixed-income-specialist.md
│       └── global-desk/
│           ├── commodities-specialist.md
│           ├── futures-specialist.md
│           ├── options-specialist.md
│           └── fx-specialist.md
└── skills/   (자산팀 전문가별 도메인 지식 15종, flat 구조)
    ├── investment-policy/        portfolio-construction/   macro-strategy/   risk-management/
    ├── kr-equity-research/       kr-etf-research/          kr-fund-research/ kr-fixed-income-research/
    ├── us-equity-research/       us-etf-research/          us-fixed-income-research/
    └── commodities-research/     futures-research/         options-research/ fx-research/
docs/AGENT_TEAMS.md   ← 본 문서
```

---

## 5. 사용 방법

- 특정 관점이 필요하면 해당 에이전트를 호출한다.
  - "미국주식 NVDA 봐줘" → `autofolio-us-equity-specialist`
  - "금 지금 들어가도 돼?" → `autofolio-commodities-specialist`
  - "S&P 헤지하게 선물로 어떻게?" → `autofolio-futures-specialist`
  - "원달러 환헤지 해야 하나?" → `autofolio-fx-specialist`
- 각 자산팀 에이전트는 호출 시 자신의 전담 스킬(`.claude/skills/`)을 적용한다.
- 종합 판단은 전문가 의견을 모아 `autofolio-portfolio-manager` → `autofolio-cio` 순으로 통합한다.
- 서브에이전트는 다른 서브에이전트를 직접 호출하지 못하므로, **메인 세션이 오케스트레이터** 역할을 한다(전문가들을 차례로 호출→PM/CIO로 종합).
- 새 에이전트·스킬은 Claude Code 세션 갱신/재시작 후 자동 인식된다. 전문성을 더 깊게 하려면 해당 스킬 폴더에 `references/`를 추가한다.
