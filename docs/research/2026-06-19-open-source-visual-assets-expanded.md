# 오픈소스/무료 비주얼 에셋·리소스 — 확장 리서치 개요 (2026-06-19)

> 산출물: **리서치/큐레이션 문서만.** 코드·의존성·웹 파일 변경 0. 적용은 백로그대로 별도 승인 후 단계적.
> 목적: 1차 리서치(아래 4개 문서)를 **훨씬 넓게 확장** — 특히 사용자 요청대로 **그래프·이미지·캐릭터** 같은 시각 요소를 필수로, 무료/오픈소스 또는 차용 가능한 **design·asset·component·font·image·resource**를 망라.
> 방법: 9개 독립 도메인을 병렬 리서치 에이전트로 조사, 각 항목 라이선스를 **실제 LICENSE 파일/공식 페이지에서 검증(검증일 2026-06-19, URL 인용)**, 제약은 ⚠️/제외로 명시.

## 이 확장 묶음의 문서

| 문서 | 다루는 영역 |
|---|---|
| **이 문서** | 개요·종합 Top picks·**라이선스 리스크 레지스터**·검증 자세 |
| [dataviz-libraries-and-color-expanded.md](./dataviz-libraries-and-color-expanded.md) | **그래프** — 시각화 라이브러리(uPlot·KLineChart·Chart.js·billboard.js 등) + 데이터viz 컬러(히트맵/트리맵 sequential·diverging, CVD-안전, 다크모드) |
| [icons-flags-currency-expanded.md](./icons-flags-currency-expanded.md) | 아이콘(MingCute 등) + **국기**(FX·멀티마켓) + 통화/암호화폐 글리프 |
| [illustrations-characters-avatars-3d-expanded.md](./illustrations-characters-avatars-3d-expanded.md) | **이미지·캐릭터** — 핀테크 일러스트 + 마스코트 + **아바타(계정·AI 에이전트)** + **3D** |
| [ui-components-and-motion-expanded.md](./ui-components-and-motion-expanded.md) | **컴포넌트** — UI 라이브러리/대시보드 템플릿(shadcn·Tremor) + 애니메이션/Lottie/로더 |
| [typography-and-imagery-expanded.md](./typography-and-imagery-expanded.md) | **폰트**(한글 Wanted Sans·SUIT + 숫자 Inter·Reddit Mono) + 이미지/배경/그라데이션/패턴 |

**1차 리서치(베이스라인, 여전히 유효):** [개요](./2026-06-19-ui-dataviz-assets-research.md) · [데이터viz 갭분석](./dataviz-pattern-gap-analysis.md) · [에셋 큐레이션 매트릭스](./asset-curation-matrix.md) · [UI 개선 백로그](./ui-improvement-backlog.md).

## Executive Summary

- **그래프(데이터viz):** 기존 Recharts + lightweight-charts 베이스는 유지하되, **자산곡선·KPI엔 uPlot(MIT, ~50KB)**, **캔들엔 KLineChart(Apache-2.0)**, **테이블 스파크라인엔 @mui/x-charts(커뮤니티 MIT)** 를 좁게 보강. 갭 분석이 지적한 **히트맵·트리맵 팔레트 부재**는 **ColorBrewer RdBu(KR PnL diverging)** + **Viridis/Cividis(CC0, 트리맵 sequential)** 로 채움. 국내 벤더 선호 시 **billboard.js(Naver, 활발)**.
- **이미지·캐릭터:** **마스코트=Open Doodles(CC0)/IRA Design(MIT)**, **계정 아바타=DiceBear Notionists(CC0)**, **AI 에이전트 아바타=DiceBear Bottts 또는 Boring Avatars(MIT)** — 에이전트별 시드로 고유 페르소나. **3D 액센트=3dicons.co(CC0)+Microsoft Fluent Emoji 3D(MIT)**. 단일 `#3182F6` 리컬러가 최우선인 빈 상태는 기존 **unDraw**가 여전히 우위.
- **컴포넌트:** **shadcn/ui(MIT) + Tremor(Apache-2.0)** 가 정답에 가장 가까움 — 둘 다 Tailwind+Radix, 차트가 Recharts라 기존 스택과 정합. **Tremor Blocks가 2026-06-19 시점 전면 무료화**(Vercel 인수)로 금융 대시보드 블록 300+ 무상.
- **폰트:** 조사 16종 전부 **정식 OFL, 제외 0**. 한글 **Wanted Sans/SUIT**(가변·핀테크), 금융 숫자 **Inter**(tnum+slashed-0 유일) + 모노 **Reddit Mono/JetBrains Mono**.
- **공통:** 모든 추천은 **퍼미시브(MIT/Apache/ISC/CC0/OFL) + 자체호스팅(런타임 CDN 0)** — Autofolio의 오프라인 자세와 일치. 런타임 아이콘/아바타/폰트 CDN·핫링크는 전부 배제.

## 가장 높은 레버리지 권고 (Cross-cutting Top 12)

| # | 권고 | 영역 | 대표 자원(라이선스) | 표면 |
|---|---|---|---|---|
| 1 | 자산곡선·KPI 미니차트 경량화 | 그래프 | **uPlot** (MIT) | `EquityChart`·`KpiCard` |
| 2 | 캔들 전용 엔진 + 내장 지표 | 그래프 | **KLineChart** (Apache-2.0) | `CandleChart` |
| 3 | 테이블 셀 스파크라인 | 그래프 | **@mui/x-charts** (커뮤니티 MIT) | `HoldingsTable` |
| 4 | 히트맵·KR PnL diverging 팔레트 | 컬러 | **ColorBrewer RdBu** (Apache·귀속) | 히트맵·PnL 음영 |
| 5 | 트리맵(집중도) sequential 팔레트 | 컬러 | **Viridis/Cividis** (CC0) | 집중도 트리맵 |
| 6 | dark-mode `#3182F6` 토큰 | 컬러 | **Radix Colors** (MIT) | 전역 다크 토큰 |
| 7 | Lucide 보완 + 원화 ₩·캔들 글리프 | 아이콘 | **MingCute**(Apache) / **Tabler `currency-won`**(MIT) | 전 표면·FX |
| 8 | 국기(FX·멀티마켓) | 아이콘 | **circle-flags + flag-icons** (MIT) | 통화 피커·계좌행 |
| 9 | 계정·AI 에이전트 아바타 | 캐릭터 | **DiceBear Notionists/Bottts**(CC0/무료) · **Boring Avatars**(MIT) | 계정·에이전트 탭 |
| 10 | 마스코트 + 핀테크 일러스트 | 이미지 | **Open Doodles/IRA Design**(CC0/MIT) · unDraw | 온보딩·빈/성공 상태 |
| 11 | 금융 대시보드 컴포넌트 | 컴포넌트 | **shadcn/ui + Tremor**(MIT/Apache) | 대시보드 전반 |
| 12 | 한글 UI 폰트 + 금융 숫자 | 폰트 | **Wanted Sans/SUIT**(OFL) + **Inter/Reddit Mono**(OFL) | 전 텍스트·수치 테이블 |

## 라이선스 리스크 레지스터 (제외·주의 종합)

> **제품 맥락:** Autofolio는 유료 상용 지향(→ [판매 전 금융규제 게이트](../../CLAUDE.md))이므로 **CC-BY(귀속)·CC-BY-SA(카피레프트)·비상업·독점**은 트리아지 대상. 아래는 채택 시 반드시 피하거나 조건을 충족해야 하는 항목.

### ❌ 제외 (상용 부적합 / 사용 불가)

| 자원 | 사유 |
|---|---|
| **ApexCharts** | 2025-06-26 MIT→매출연동 듀얼(비-SPDX). 유료 핀테크엔 Commercial/OEM 비용 위험 |
| **Highcharts·amCharts·AnyChart·Syncfusion·DevExtreme** (차트) | 상용 자체호스팅에 유료 라이선스 필수(또는 무료=비상용/워터마크/브랜딩) |
| **TradingView Advanced Charts** | 승인 게이트+의무 블로그+비공개 레포+**경쟁 서비스 금지**+위반 건당 $50k. (무료 필요시 베이스라인 Lightweight Charts) |
| **Untitled UI Icons** | LICENSE가 재배포 금지(package.json "MIT"는 오기). 원시 SVG 벤더링 불가 |
| **Absurd Design**(무료) | 무료 티어 = 비상업 전용 + 귀속 강제 |
| **DrawKit** | 컴파일/재배포 전면 금지 + AI학습 금지 → 앱 번들 자체 금지 |
| **Reshot** | 2026년 1월 Envato 서비스 종료 → 신규 다운로드 불가 |
| **Lordicon**(Free) | 비상용 전용 + 출처표기 → 상용은 PRO 유료 |
| **Magic Pattern**(magicpattern.design) | 무료 내보내기 상업 사용 사전 서면 동의 필요 |
| **Tailwind Plus·MUI X Pro·CoreUI PRO·Creative Tim PRO·Cruip·각종 Pro 블록** | 유료/closed(무료 대안 충분) |
| **OpenMoji 국기·Arcticons·Cryptofonts·Multiavatar(핵심용)** | 카피레프트(CC-BY-SA/GPL) 또는 리브랜딩 금지 단서 |

### ⚠️ 주의 (조건부 사용 — 귀속·상표·약관 단서)

| 자원 | 조건 |
|---|---|
| **ColorBrewer** 팔레트 | Cynthia Brewer 귀속 표기 의무 + 제품명에 "ColorBrewer" 금지 |
| **Paul Tol** 팔레트 | 명시 라이선스 텍스트 부재 → 상용 전 저자 확인(또는 CC0/ColorBrewer로 동치 치환) |
| **CC-BY 아이콘 세트**(Solar·Streamline·Lets-Icons·Basil·CoreUI free) | 가시 귀속 필수(Streamline은 클릭 링크 강제) → 무귀속 운용이면 회피 |
| **DiceBear CC-BY 스타일**(Adventurer·Personas·Micah·Big Smile·Fun Emoji) | 귀속 필수 → CC0 스타일(Notionists·Lorelei·Open Peeps 등)로 한정하면 부담 0 |
| **DiceBear Bottts/Avataaars** | Pablo Stanley 커스텀 무료(귀속 강제 없음) — 상용 배포 직전 약관 재확인 |
| **브랜드/암호화폐/카드 로고**(Simple Icons·web3icons·ccicons) | 코드가 CC0/MIT여도 **로고는 상표** → 토스·카카오·증권사·거래소·카드사 표시는 브랜드별 가이드라인 개별 검토(출시 전 게이트) |
| **Storyset·Ouch!·Iconscout·Popsy**(일러스트) | 무료는 귀속/링크백 강제 → 유료 전환 시에만 무귀속 |
| **Blush**(일러스트) | 브랜드 리컬러 가능한 SVG는 Pro(유료), 무료는 PNG+프리셋만 |
| **Stubborn·Shapefest** | 커스텀 무료지만 재배포 금지(Stubborn 내부 마스코트만, Shapefest 마케팅 비주얼만) |
| **Hero Patterns** | CC-BY 귀속 의무 → 표기 동선 없으면 SVGBackgrounds/pattern.css 대체 |
| **LottieFiles·Rive 애니메이션 에셋** | "런타임 MIT ≠ 에셋 무료" — 파일별(LottieFiles)·CC-BY 4.0 균일 출처표기(Rive) 확인 |
| **useAnimations 아이콘·css-loaders.com 원본** | 아이콘 CC-BY+재배포금지 / 원본 라이선스 미명시 → MIT 대안(react-spinners·cssloaders 포크) |
| **사진(Unsplash·Pexels·Pixabay)·Openverse** | 자산 재배포/재판매 금지(제품 UI 무관)·AI/모델릴리스 미검증 컷 개별 검수·Openverse 라이선스 미보증 |
| **SUIT·Gmarket Sans·Commit Mono** | 정식 OFL이나 OFL.txt/LICENSE-FONT를 vendored 폴더에 직접 동봉 필요 |

## 검증 자세 (중요)

- **라이선스는 각 출처의 실제 LICENSE 파일/공식 라이선스 페이지에서 확인**(검증일 2026-06-19, URL은 각 토픽 문서에 인용). 그래도 **채택 전 최종 재확인 권장** — 라이선스는 변한다(예: **ApexCharts가 2025-06-26 MIT→매출연동**으로 변경, **Tremor Blocks가 유료→무료화**, **Reshot 2026-01 종료**).
- **"런타임 MIT ≠ 에셋 무료"**: 차트/컴포넌트 라이브러리 코드 라이선스와, 거기서 받는 Lottie/Rive 애니메이션·DiceBear 아트 스타일·Iconify 세트의 라이선스는 **별개**. 각각 검증.
- **자체호스팅(런타임 CDN 0) 강제**: `api.dicebear.com`·`api.iconify.design`·`boringavatars.com`·폰트 CDN·이미지 핫링크 전부 금지. Iconify는 `unplugin-icons`로 빌드타임 트리셰이킹 시에만 사용.
- **상표 ≠ 저작권**: 브랜드/결제/거래소 로고는 코드 라이선스가 CC0/MIT여도 로고 자체가 상표 → 본 저장소의 판매 전 게이트와 함께 출시 전 개별 검토.
- ⚠️ 일부 항목은 미검증(각 토픽 문서에 명시): Carbon/Hugeicons의 ₩ 글리프, Cividis 정확 anchor hex, Delesign/Flowbite finance 인벤토리, 일부 사진 사이트 자산별 라이선스 등 — 채택 전 확인.

## 다음 단계 (적용은 별도 승인)

1. **백로그 승격:** 위 Top 12 중 우선순위를 [ui-improvement-backlog.md](./ui-improvement-backlog.md) 또는 `agents/lead_engineer/tasks/`의 정식 TASK로 승격(번호는 승격 시 부여, 동시 세션 충돌 방지).
2. **구현 시 준수:** `web/AGENTS.md`(Next.js 16 주의), KR PnL 관습(상승=빨강/하락=파랑)+Western 토글, 자체호스팅, 라이선스 채택 전 재확인.
3. **검증 게이트:** `docs/design-system.md` 규칙 위반 0, `scripts/design_system_gate.py --check` 경고 감소, prod 모드 E2E(CI=1).
4. **컴플라이언스:** 브랜드 로고·귀속 의무 항목은 출시 전 개별 검토(상표 가이드라인) — 판매 전 금융규제 게이트와 함께.
