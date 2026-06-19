# 데이터 시각화 — 라이브러리 + 컬러 시스템 (확장 리서치, 2026-06-19)

> 리서치/큐레이션만. **코드·의존성 변경 0.** 적용은 별도 승인 후 단계적.
> 1차 리서치([dataviz-pattern-gap-analysis.md](./dataviz-pattern-gap-analysis.md))가 다룬 baseline(Recharts·lightweight-charts·ECharts·Carbon·Nivo·Visx·Polaris)과 팔레트(Okabe-Ito·Carbon 5색)를 **넘어서**, 자체호스팅(런타임 CDN 0)·한국 핀테크 상용(유료 판매 가능성)·Lucide/Recharts 기존 스택 정합 기준으로 확장한다.
> 라이선스는 전부 실제 GitHub `LICENSE`/npm 레지스트리/공식 페이지에서 **검증일 2026-06-19** 기준 확인. 불확실 항목은 ⚠️. 관련 문서: [개요](./2026-06-19-open-source-visual-assets-expanded.md).

---

## 시각화 라이브러리 (확장)

> 전제: **자체호스팅 전용 — 런타임 CDN 0**, 한국 핀테크 상용 서비스(유료 판매 가능성) 기준.
> 베이스라인(이미 사용/검토 완료, 신규 제안 아님): Recharts(MIT), lightweight-charts(Apache-2.0), Apache ECharts(Apache-2.0), IBM Carbon Charts, Nivo(MIT), Visx(MIT), Shopify Polaris, robinhood/spark. **TradingView Lightweight Charts(Apache-2.0)** 도 베이스라인이며, 아래 상용 제한 TradingView "Advanced Charts" 와 **다른 제품**임에 주의.

### 비교표 — 퍼미시브 & 자체호스팅 가능 (권장 후보군)

| 라이브러리 | 유형 | 라이선스(검증·SPDX/custom) | 번들/무게(unpacked·런타임) | 자체호스팅 | 적합도 | 통합 노트(Autofolio 표면) | URL |
|---|---|---|---|---|---|---|---|
| **uPlot** (`uplot` + `uplot-react`) | Canvas 시계열(라인/면) | **MIT** (SPDX 표준) ✓ | 런타임 **~50KB gzip**(동급 최소) | ✓ | ★★★★★ | EquityChart(자산곡선)·KpiCard 미니차트 최적. 초경량·초고속. 캔들 미지원(수동 path). `uplot-react`(MIT)로 React 연동 | [LICENSE](https://raw.githubusercontent.com/leeoniya/uPlot/master/LICENSE) |
| **KLineChart** (`klinecharts`) | 전용 캔들/K-line 엔진 | **Apache-2.0** (SPDX 표준, 특허허여) ✓ | canvas 코어 경량 | ✓ | ★★★★★ (캔들) | **CandleChart 1순위** — 캔들+내장 기술지표. KR 상승=빨강/하락=파랑 색 매핑 자유. React 공식 래퍼 없음 → `useRef`/`useEffect` 약 30줄 글루. ⚠️ 최신 `10.0.0-beta3`, 안정 `7.3.0` | [LICENSE](https://raw.githubusercontent.com/klinecharts/KLineChart/master/LICENSE) |
| **@mui/x-charts** `SparkLineChart` | React 스파크라인/차트(커뮤니티) | **MIT** (커뮤니티; SPDX 표준) ✓ | v9.6.0, 2025-01 publish | ✓ | ★★★★★ (스파크라인) | **홀딩스 테이블 셀 스파크라인 1순위**(현행·유지보수 중). ⚠️ MUI X 듀얼: **커뮤니티=MIT**, `-pro/-premium`만 유료 — `x-charts`(스파크라인 포함)는 MIT | [npm](https://registry.npmjs.org/@mui/x-charts/latest) · [라이선스 정책](https://mui.com/x/introduction/licensing/) |
| **billboard.js** (`billboard.js` + `@billboardjs/react`) | D3 기반 범용 차트(Naver) | **MIT** (SPDX 표준, NAVER Corp.+Tanaka) ✓ | dist 전체 ~13.5MB(런타임 import는 일부) | ✓ | ★★★★☆ | **국내(Naver) 벤더·활발 유지보수**(v4.0.1, **2026-06-16 publish**). EquityChart·AllocationChart 메인/디테일 차트에 강함. 풀 D3 엔진이라 셀 단위 스파크라인엔 과함 → 본 차트용 | [LICENSE](https://raw.githubusercontent.com/naver/billboard.js/master/LICENSE) |
| **Chart.js** (`chart.js` + `react-chartjs-2`) | 범용 canvas 차트 | **MIT** (양쪽 SPDX 표준) ✓ | core 소스 大·래퍼 小 | ✓ | ★★★★☆ | 가장 안전한 라이선스+최다 유지보수(~13M DL/주). KpiCard·EquityChart·AllocationChart 도넛 기본. 캔들은 MIT 플러그인 `chartjs-chart-financial` 필요 | [LICENSE](https://raw.githubusercontent.com/chartjs/Chart.js/master/LICENSE.md) |
| **react-financial-charts** | React 선언형 캔들 컴포넌트 | **MIT** (SPDX 표준) ✓ | 메타패키지 小(+스코프 10패키지+d3-*) | ✓ | ★★★★☆ (캔들) | JSX 선언형 캔들/지표 원할 때 CandleChart 대안. ⚠️ 릴리스 정체(2.0.1 장기)·d3 의존 다수 | [LICENSE](https://raw.githubusercontent.com/react-financial/react-financial-charts/master/LICENSE) |
| **AntV S2** (`@antv/s2` + `@antv/s2-react`) | **표/피벗(스프레드시트) 시각화** | **MIT** (SPDX 표준) ✓ | ~14.78MB | ✓ | ★★★★☆ (데이터테이블) | 홀딩스/분석 탭 **다차원 피벗·드릴다운 표**에 강함. ⚠️ DL ~5.3k/주(커뮤니티 작음)·문서 중국어·번들 큼 | [LICENSE](https://raw.githubusercontent.com/antvis/S2/next/LICENSE) |
| **shadcn/ui charts** | copy-paste 차트 블록(Recharts 위) | **MIT** (shadcn-ui/ui; SPDX 표준) ✓ | n/a(소스 벤더링, 런타임=Recharts) | ✓ | ★★★★☆ | npm 의존 아님 — 소스 복사. Tailwind+자체 디자인시스템 정합 최상(이미 Tailwind). 전이 의존=Recharts(MIT). 복사 코드 유지보수 자가 부담 | [LICENSE](https://raw.githubusercontent.com/shadcn-ui/ui/main/LICENSE.md) |
| **Plotly.js** (`plotly.js` + `react-plotly.js`) | 범용 인터랙티브(캔들 내장) | **MIT** (SPDX 표준) ✓ | 소스 大(런타임 min ~3–4MB, partial bundle로 축소) | ✓ | ★★★☆☆ | 캔들/OHLC 내장·기능 풍부하나 **무겁다**. partial/custom bundle 필수. 지도 trace만 Mapbox 토큰(일반 차트 0) | [LICENSE](https://raw.githubusercontent.com/plotly/plotly.js/master/LICENSE) |
| **Tremor** (`@tremor/react`) | React KPI/대시보드 키트(Recharts 기반) | **Apache-2.0** (SPDX 표준) ✓ | 494KB, v3.18.7 | ✓ | ★★★☆☆ | KpiCard·대시보드 프리미티브 외관 우수. ⚠️ **npm 동결**(3.18.7, 2025-01 이후) — 동력은 copy-paste "Tremor Raw"로 이동. 장기 의존 중위험 | [GitHub LICENSE](https://raw.githubusercontent.com/tremorlabs/tremor/main/LICENSE) · [npm](https://registry.npmjs.org/@tremor/react/latest) |
| **AntV G2 / G2Plot** (`@antv/g2`, `@antv/g2plot` + `@ant-design/charts`) | grammar-of-graphics 차트 | **MIT** (SPDX 표준) ✓ | G2 8.4MB / G2Plot 9.1MB | ✓ | ★★★☆☆ | `@ant-design/charts`(MIT)로 React 연동. EquityChart·AllocationChart·KPI 커버. ⚠️ G2Plot은 구 G2 v4 기반(유지보수 모드)·문서 중국어 | [G2 LICENSE](https://raw.githubusercontent.com/antvis/G2/master/LICENSE) · [G2Plot LICENSE](https://raw.githubusercontent.com/antvis/G2Plot/master/LICENSE) |
| **Observable Plot** (`@observablehq/plot`) | grammar-of-graphics(SVG) | **ISC** (MIT 동등, SPDX 표준) ✓ | 1.46MB, v0.6.17 | ✓ | ★★★☆☆ | 간결 문법 AllocationChart·EquityChart. ⚠️ pre-1.0 API·React 공식 래퍼 없음(수동)·표/피벗 없음 | [LICENSE](https://raw.githubusercontent.com/observablehq/plot/main/LICENSE) |
| **VictoryChart** (`victory`) | React 네이티브 차트 컴포넌트 | **MIT** (본문 verbatim MIT; ⚠️ GitHub API는 `LICENSE.txt`+DT 주석 탓 NOASSERTION 오표기) ✓ | 2.17MB, v37.3.6 | ✓ | ★★★☆☆ | React DX 최상(컴포넌트=React). ⚠️ 웹 `victory` 릴리스 ~17개월 정체, 동력은 `victory-native`로 이동 — 장기 의존 전 거버넌스 재확인. 표/피벗 없음 | [LICENSE.txt](https://raw.githubusercontent.com/FormidableLabs/victory/main/LICENSE.txt) |
| **D3 core** (`d3`) | 저수준 시각화 툴킷 | **ISC** (MIT 동등, SPDX 표준) ✓ | 0.83MB(메타) | ✓ | ★★☆☆☆ | 완전 커스텀 자산곡선/KPI 기반(엔진). 빌드 비용 최고(축·스케일·렌더 직접). turnkey 아님 | [LICENSE](https://raw.githubusercontent.com/d3/d3/main/LICENSE) |
| **Frappe Charts** (`frappe-charts`) | 경량 SVG 차트(0 deps) | **MIT** (SPDX 표준) ✓ | ~1.0MB, v1.6.2 | ✓ | ★★☆☆☆ | 가볍고 0 deps·깔끔하나 React 공식 래퍼 없음·풀사이즈 차트 지향(셀 스파크라인엔 부적). ⚠️ 안정선 2021 정체 | [LICENSE](https://raw.githubusercontent.com/frappe/charts/master/LICENSE) |

### 비교표 — 스파크라인 보조 후보(테이블 셀)

| 라이브러리 | 라이선스(검증) | 상태 | 적합도/노트 | URL |
|---|---|---|---|---|
| **@mui/x-charts `SparkLineChart`** | **MIT**(커뮤니티) ✓ | 현행·유지보수 | **테이블 인라인 스파크라인 1순위**(상단 표) | [npm](https://registry.npmjs.org/@mui/x-charts/latest) |
| **@fnando/sparkline** | **MIT** ✓ | ⚠️ 정체(2018)이나 **~50KB·0 deps·안정** | SVG에 직접 draw(행별 스타일 완전 제어). React는 ~15줄 ref 래퍼 자작. 표면 작아 저위험 — **경량 2순위** | [LICENSE](https://raw.githubusercontent.com/fnando/sparkline/main/LICENSE) |
| react-sparklines | **MIT** ✓ | ⚠️ **정체(2017-07, React 15 기준)**·DL ~235k/주 | 네이티브 `<Sparklines>` drop-in 최강 ergonomics이나 React 18+ 미보증 → 핀+스모크테스트 조건부 | [LICENSE](https://raw.githubusercontent.com/borisyankov/react-sparklines/master/LICENSE) |
| `sparklines` (vanilla) | **MIT** ✓ | ⚠️ 정체(2020)·React 바인딩 없음 | 바닐라 SVG·직접 래핑. 비권장 | [npm](https://registry.npmjs.org/sparklines/latest) |
| uPlot(상단) | MIT ✓ | 활발 | 셀 단위 미니 라인 다량 렌더에도 적합(경량) | (상단) |

### 상용 제한 / 제외(EXCLUDE) — ⚠️ 유료 핀테크 제품 기준

| 제품 | 라이선스 유형 | 상용 자체호스팅? | 핵심 제약 ⚠️ | 판정 | URL |
|---|---|---|---|---|---|
| **ApexCharts** (`apexcharts` + `react-apexcharts`) | **custom 듀얼(비-SPDX)**, npm `license:"SEE LICENSE IN LICENSE"`; 구버전(≤4.x)만 MIT | 조건부(유료) | **2025-06-26 MIT→매출연동 변경.** 커뮤니티 무료=매출 **<$2M**만. **≥$2M=Commercial(유료)**. 제품 임베드 재배포는 **매출 무관 OEM**. "경쟁 차트 제품 금지" | **제외(또는 유료/구MIT핀)** | [license](https://apexcharts.com/license/) · [OEM](https://apexcharts.com/license/oem/) · [변경공지](https://apexcharts.com/blog/new-licencing-model/) · [구 MIT v3.54.1](https://raw.githubusercontent.com/apexcharts/apexcharts.js/v3.54.1/LICENSE) |
| **Highcharts** | proprietary(무료=CC BY-NC, 비상용만) | 유료시 가능 | 상용 무료 불가. 공개 웹앱=**SaaS $366/seat/년**, 고객 호스팅/3자 빌드=OEM(견적). 자체호스팅 허용(유료) | **제외(SaaS 라이선스 구매 시 가능)** | [shop.highcharts.com/license](https://shop.highcharts.com/license) |
| **amCharts 5** | proprietary(무료=브랜딩 링크 강제) | 유료시 가능 | 무료티어 amCharts 브랜딩 링크 필수, 제거=유료. SaaS **$280/년 또는 $650 영구/seat** | **제외(무료 브랜딩 티어); 유료시 가능** | [amcharts.com/online-store](https://www.amcharts.com/online-store/) |
| **AnyChart** | proprietary(소스 공개·라이선스 유료) | 유료시 가능 | 무료/트라이얼 **"Credits" 워터마크**(제거 불가, 비상용). 상용=유료(SaaS/OEM, 견적) | **제외(유료 라이선스 시 가능)** | [license](https://www.anychart.com/support/pages/license/?type=saas-annual) · [LICENCE](https://github.com/AnyChart/AnyChart/blob/master/LICENCE) |
| **TradingView Advanced Charts**(구 Charting Library) | proprietary·무료(서명 계약 필요, **오픈소스 아님**) | 조건부(승인+서명) | ⚠️ **신청/승인 게이트**, TradingView **로고+dofollow 링크 의무**, **파트너십 블로그 게시 의무(출시 14일 전)**, **비공개 레포 강제(npm 불가)**, **"경쟁 서비스 개발 금지"**, 위반 **건당 $50,000**, 컴플라이언스 모니터링권. *Lightweight Charts(Apache-2.0)와 별개* | **제외(핀테크 차트앱은 no-compete 충돌 위험 — 법무 검토 전 비권장)** | [advanced-charts](https://www.tradingview.com/advanced-charts/) · [free-charting-libraries](https://www.tradingview.com/free-charting-libraries/) · [계약 PDF](https://s3.amazonaws.com/tradingview/charting_library_license_agreement.pdf) |
| **Syncfusion** charts | proprietary(Community 협소) | 유료시 가능 | Community 무료=매출 **<$1M & 개발자 ≤5 & 직원 ≤10 & VC 누적 ≤$3M** 전부 충족 시만. 핀테크 SaaS 초과 가능성↑→유료 | **제외(조건 미달 시 유료)** | [communitylicense](https://www.syncfusion.com/products/communitylicense) · [pricing](https://www.syncfusion.com/sales/pricing) |
| **DevExtreme**(DevExpress) charts | proprietary(상용 무료/커뮤니티 없음) | 유료시만 | 모든 상용 앱=개발자당 12개월 구독(~$881.99~) 필수 | **제외(유료 구독 필수)** | [Licensing](https://js.devexpress.com/Licensing/) · [Buy](https://js.devexpress.com/Buy/) |
| **Britecharts** (`britecharts`) | **Apache-2.0**(주의: MIT 아님) ✓ | ✓(라이선스 OK) | 라이선스 OK이나 ⚠️ **정체(2023-01)**·D3 v5(구버전)·React 래퍼 없음. *canonical 레포는 `britecharts/britecharts`(eventbrite/는 이전 스텁)* | **비권장(정체)** — 라이선스 자체는 자체호스팅 OK | [LICENSE.md](https://raw.githubusercontent.com/britecharts/britecharts/master/LICENSE.md) |
| **react-stockcharts** | **MIT** ✓ | ✓(라이선스 OK) | 라이선스 OK이나 ⚠️ **2018 이후 방치**(0.7.8, React 15/16). react-financial-charts가 후계 | **비권장(폐기됨)** — 대신 react-financial-charts | [LICENSE](https://raw.githubusercontent.com/rrag/react-stockcharts/master/LICENSE) |

### 권장(Top picks) — Autofolio 표면 매핑

1. **EquityChart(자산곡선) + KpiCard 미니차트 → `uPlot`(MIT) + `uplot-react`(MIT).** 동급 최소 ~50KB gzip, 초고속, 외부호출 0. NAV/자산곡선·다수 KPI 소형 차트 최적.
2. **CandleChart(캔들) → `KLineChart`(Apache-2.0).** 캔들+내장 기술지표 전용, KR 상승=빨강/하락=파랑 매핑 자유. React 글루 약 30줄. JSX 선언형 선호 시 대안 `react-financial-charts`(MIT).
3. **홀딩스 테이블 셀 스파크라인 → `@mui/x-charts` `SparkLineChart`(커뮤니티 MIT, 현행).** 경량·완전제어 원하면 `@fnando/sparkline`(MIT, ~50KB, 0 deps, 약 15줄 래퍼). (react-sparklines는 2017 정체 → 핀+스모크테스트 조건부.)
4. **AllocationChart(배분 도넛)/범용 KPI → `Chart.js`(MIT) + `react-chartjs-2`(MIT).** 가장 안전한 라이선스+최다 유지보수.
5. **메인/디테일 범용 차트에 국내 벤더 선호 시 → `billboard.js`(MIT, Naver, v4.0.1 2026-06-16 활발).** EquityChart·AllocationChart에 적합(셀 스파크라인엔 과함).
6. **분석/에이전트 탭 피벗·드릴다운 데이터테이블 → `AntV S2`(MIT) + `@antv/s2-react`.**
7. **자체 디자인시스템 정합 최우선 → `shadcn/ui charts`(MIT) 소스 벤더링**(Tailwind 이미 사용, 전이 의존=Recharts). KPI 외관은 **Tremor**(Apache-2.0)도 후보이나 npm 동결로 중위험.

> **핵심:** 기존 Recharts + lightweight-charts 베이스라인은 유지하되, **자산곡선·KPI엔 uPlot**, **캔들엔 KLineChart**, **테이블 스파크라인엔 @mui/x-charts**를 좁게 보강하는 것이 가장 라이선스-깨끗·경량 경로다. 전면 교체 불필요.

### 제외(EXCLUDE) 명시 — 사유 요약

- **ApexCharts** — 2025-06-26 비-SPDX 매출연동 듀얼 라이선스 전환(npm `license:"SEE LICENSE IN LICENSE"`). 유료 핀테크엔 Commercial/OEM 비용 위험. *"ApexCharts=MIT"는 옛 정보.* 정 쓰려면 유료 또는 구 MIT 버전 핀(보안·기능 갱신 포기).
- **Highcharts / amCharts / AnyChart / Syncfusion / DevExtreme** — 상용 자체호스팅에 **유료 라이선스 필수**(또는 무료티어가 비상용/워터마크/브랜딩 강제). 기본 제외, 예산 승인 시 조건부.
- **TradingView Advanced Charts** — 무료지만 승인 게이트+의무 출시 블로그+비공개 레포+**경쟁 서비스 개발 금지**+건당 $50k. 차트/분석 노출 핀테크 앱과 no-compete 충돌 소지 → 법무 검토 전 제외. (무료가 필요하면 베이스라인 **Lightweight Charts(Apache-2.0)** 사용.)
- **react-stockcharts**(2018 방치)·**Britecharts**(2023 정체, Apache-2.0)·**react-sparklines**(2017 정체) — 라이선스는 퍼미시브이나 유지보수 사망/정체로 신규 빌드 비권장. 각각 react-financial-charts / 베이스라인 차트 / MUI X SparkLineChart로 대체.

### 검증 메모

- 모든 퍼미시브 후보는 **런타임 CDN/제3자 API 요구 0** — 전부 클라이언트에서 사용자 데이터로 렌더, 자체호스팅 요건 충족. (예외: Plotly의 지도 trace만 Mapbox 토큰 — 일반 차트는 불필요.)
- SPDX 비표준 1건: **ApexCharts**(custom 듀얼). 나머지는 MIT/Apache-2.0/ISC 표준.
- ⚠️ Victory는 본문이 verbatim MIT이나 GitHub 라이선스 API가 `LICENSE.txt`+DefinitelyTyped 주석 탓 `NOASSERTION` 오표기 — MIT로 취급.
- ⚠️ MUI X 듀얼: 커뮤니티(`@mui/x-charts` 등)=MIT, `-pro`/`-premium`만 상용. SparkLineChart는 커뮤니티(MIT) 포함.
- ⚠️ Britecharts canonical 레포는 `britecharts/britecharts`(구 `eventbrite/britecharts`는 "Repository Moved" 스텁) — LICENSE.md = Apache-2.0.

---

## 데이터viz 컬러 시스템·팔레트 (확장)

> Autofolio는 **self-host(런타임 CDN 0)** 이므로 팔레트는 토큰 hex로 코드에 임베드되며, 따라서 *팔레트 데이터/스펙의 라이선스*가 중요하다. 기존 문서가 다룬 **Okabe-Ito CUD**와 **IBM Carbon 5색**은 중복 제외하고 그 *너머*를 다룬다. 핵심 공백은 갭 분석이 지적한 **히트맵·트리맵용 sequential/diverging 팔레트 부재**다.

### 검증 매트릭스

| 팔레트/시스템 | 유형 | 라이선스(검증) | 핵심 hex | 적합 표면 | 비고(CVD/WCAG) | URL |
|---|---|---|---|---|---|---|
| **ColorBrewer 2.0 — RdBu** (diverging, 5-class) | diverging | **Apache-2.0 스타일** — 상업 OK, **단 "Cynthia Brewer 개발" 귀속 필수**, "ColorBrewer"를 제품명에 사용 금지 ✅ | `#ca0020 #f4a582 #f7f7f7 #92c5de #0571b0` | **KR PnL 히트맵/트리맵**(빨↔파, 중립 흰 midpoint) | RdBu/RdYlBu/BrBG/PuOr = ColorBrewer가 colorblind-safe로 명시 분류 | [colorbrewer2.org/export/LICENSE.txt](https://colorbrewer2.org/export/LICENSE.txt) · [colorbrewer2.org](https://colorbrewer2.org/#type=diverging&scheme=RdBu&n=5) |
| **ColorBrewer 2.0 — RdYlBu** (diverging, 5) | diverging | 동일(Apache 스타일, 귀속 필수) ✅ | `#d7191c #fdae61 #ffffbf #abd9e9 #2c7bb6` | 위와 동일(중립이 노랑 톤이라 흰 배경에서 midpoint가 더 또렷) | colorblind-safe 분류. ⚠️ 중앙 `#ffffbf`는 흰 배경 대비 낮음 → 셀 경계 필요 | [colorbrewer2.org](https://colorbrewer2.org/#type=diverging&scheme=RdYlBu&n=5) |
| **ColorBrewer 2.0 — YlOrRd** (sequential, 5) | sequential | 동일 ✅ | `#ffffb2 #fecc5c #fd8d3c #f03b20 #bd0028` | 단방향 강도 히트맵(예: Today Gain *절대 변동 크기*) | 단조 명도. ⚠️ 밝은 끝 흰 배경 대비 부족 → 어두운 배경/경계 권장 | [colorbrewer2.org](https://colorbrewer2.org/#type=sequential&scheme=YlOrRd&n=5) |
| **ColorBrewer 2.0 — Blues** (sequential, 7) | sequential | 동일 ✅ | `#eff3ff #c6dbef #9ecae1 #6baed6 #4292c6 #2171b5 #084594` | 집중도 트리맵(단색 강도), 브랜드 blue 계열과 자연스러움 | 인쇄/색맹 모두 안전(단색 sequential은 본질적 CVD-안전) | [colorbrewer2.org](https://colorbrewer2.org/#type=sequential&scheme=Blues&n=7) |
| **Paul Tol — sunset** (diverging, 11) | diverging | SRON 기술노트(TN/09-002). ⚠️ **명시 라이선스 텍스트 없음** — 위젯/패키지로 광범위 배포(파생 `tol-colors`=BSD-3). hex 자체는 자유 사용 통념이나 **공식 라이선스 페이지 부재** ⚠️ | `#364B9A #4A7BB7 #6EA6CD #98CAE1 #C2E4EF #EAECCC #FEDA8B #FDB366 #F67E4B #DD3D2D #A50026` | **KR PnL diverging 대안**(RdYlBu 기반이나 중앙이 더 어둡고 대칭 개선) | 저자가 **color-blind vision에서 작동**한다고 명시. bad-data=`#FFFFFF` | [personal.sron.nl/~pault](https://personal.sron.nl/~pault/) |
| **Paul Tol — BuRd** (diverging, 9) | diverging | 동일(⚠️ 라이선스 텍스트 부재) | = **ColorBrewer RdBu의 reverse**(파→빨) | KR PnL용(파=하락 시작이 자연) | color-blind safe 명시. bad-data=`#FFEE99` | [packages.tesselle.org/khroma](https://packages.tesselle.org/khroma/reference/scale_tol_BuRd.html) |
| **Paul Tol — bright** (qualitative, 7) | categorical | 동일(⚠️ 라이선스 텍스트 부재) | `#4477AA #EE6677 #228833 #CCBB44 #66CCEE #AA3377 #BBBBBB` | 배분 도넛/스택 등 categorical(Okabe-Ito 대안) | 저자 명시 color-blind safe. `#4477AA`=Toss-blue 계열 앵커 | [personal.sron.nl/~pault](https://personal.sron.nl/~pault/) |
| **Paul Tol — vibrant** (qualitative, 7) | categorical | 동일 | `#EE7733 #0077BB #33BBEE #EE3377 #CC3311 #009988 #BBBBBB` | categorical(채도 높은 변형) | color-blind safe. `#0077BB`=on-brand blue | [personal.sron.nl/~pault](https://personal.sron.nl/~pault/) |
| **Paul Tol — muted** (qualitative, 9) | categorical | 동일 | `#CC6677 #332288 #DDCC77 #117733 #88CCEE #882255 #44AA99 #999933 #AA4499` | 시리즈 ≥8개 categorical | color-blind safe. ⚠️ 명확한 red/medium-blue 부재 | [personal.sron.nl/~pault](https://personal.sron.nl/~pault/) |
| **Viridis** (sequential, perceptually-uniform) | sequential | **CC0 / public domain** — 제약 0(귀속 권장만) ✅✅ | `#440154 #3B528B #21908C #5DC863 #FDE725` (5-stop) | 집중도 트리맵·강도 히트맵(지각 균일 = 값 차이가 명도로 정확 전달) | 명시적 CVD-친화 설계. 단조 명도 → 흑백 인쇄/색맹 모두 안전 | [github.com/BIDS/colormap](https://github.com/BIDS/colormap/blob/master/colormaps.py) |
| **Cividis** (sequential, CVD-최적화) | sequential | **CC0** (matplotlib) ✅✅ | 짙은 청색 → 회청 → 황색(viridis를 적·녹색맹 인지 동일하도록 보정) | **CVD 사용자 우선** 강도 히트맵·트리맵 | PNNL(Nuñez·Anderson·Renslow, PLOS ONE 2018)이 **deuteranopia 최적화**로 설계 — viridis보다 CVD-안전 우위. ⚠️ 정확 anchor hex는 matplotlib `cm.cividis`에서 샘플 권장 | [matplotlib cividis](https://matplotlib.org/stable/users/prev_whats_new/whats_new_2.2.html) · [kennethmoreland.com](https://www.kennethmoreland.com/color-advice/) |
| **Magma / Plasma / Inferno** (sequential) | sequential | **CC0** ✅✅ | magma: `#000004 #51127C #B63679 #FB8861 #FCFDBF` | 어두운 대시보드 강도 히트맵(검정 배경에서 magma/inferno가 viridis보다 대비 우수) | 모두 지각 균일·CVD-친화. inferno/magma는 dark-mode 배경에 적합 | [github.com/BIDS/colormap](https://github.com/BIDS/colormap/blob/master/colormaps.py) |
| **Radix Colors** (UI scale, 12-step, light+dark) | UI | **MIT** (Modulz/WorkOS) ✅✅ | blue dark: `#0d1520 #111927 #0d2847 #003362 #004074 #104d87 #205d9e #2870bd #0090ff #3b9eff #70b8ff #c2e6ff` | **dark-mode 토큰 전반**·차트 표면/보더/텍스트 계조 | 12스텝이 용도별(배경/보더/솔리드/텍스트) 대비 보장 설계. step 11/12는 본문 텍스트 대비 충족 | [LICENSE](https://github.com/radix-ui/colors/blob/main/LICENSE) · [radix-ui.com/colors](https://www.radix-ui.com/colors) |
| **Open Color** (UI scale, 10-step) | UI | **MIT** (heeyeun) ✅✅ | blue: `#e7f5ff #d0ebff #a5d8ff #74c0fc #4dabf7 #339af0 #228be6 #1c7ed6 #1971c2 #1864ab` | UI 토큰·차트 계조(가벼운 대안, Tailwind류) | 색맹 자동보장 아님(UI scale) → 데이터 인코딩엔 위 CVD 팔레트 사용 | [LICENSE](https://github.com/yeun/open-color/blob/master/LICENSE) |
| **Tailwind 기본 팔레트** (UI scale) | UI | **MIT** (Tailwind Labs) ✅✅ | blue: `#eff6ff … 500:#3b82f6 … 700:#1d4ed8 … 950:#172554` | UI 토큰(이미 Tailwind 사용 중) | **blue-500 `#3b82f6` ≈ 브랜드 `#3182F6`** (사실상 동일) → 브랜드 앵커로 자연 정렬 | [LICENSE](https://github.com/tailwindlabs/tailwindcss/blob/master/LICENSE) |
| **Catppuccin** (dark theme, 4 flavor) | UI | **MIT** ✅✅ | Mocha base `#1e1e2e`, text `#cdd6f4`, blue `#89b4fa`, red `#f38ba8`, green `#a6e3a1` | dark-mode 차트 표면/배경(Mocha) 후보 | 저채도 파스텔 → 대비 부드러움. data 인코딩보다 chrome/배경용 | [LICENSE](https://github.com/catppuccin/catppuccin/blob/main/LICENSE) |
| **d3-scale-chromatic** (구현 라이브러리) | (구현) | **ISC** (Bostock) + 내장 ColorBrewer는 **Apache-2.0**(Brewer 귀속) ✅ | `interpolateRdBu`, `interpolateViridis`, `schemeBlues` 등 | 위 팔레트의 *런타임 보간* 필요 시(self-host npm) | 라이선스 깨끗. 단 ColorBrewer 귀속 의무는 그대로 승계 | [LICENSE](https://github.com/d3/d3-scale-chromatic/blob/main/LICENSE) |
| **chroma.js** (구현 라이브러리) | (구현) | **BSD-3** (Aisch) + 내장 ColorBrewer **Apache-2.0** ✅ | `chroma.scale('RdBu')`, `chroma.scale(['#3182F6','#f7f7f7','#F04452'])` 등 | 커스텀 KR-PnL 램프 보간·`.classes(n)` 이산화 | 깨끗. ColorBrewer 귀속 승계. 번들 작음 | [LICENSE](https://github.com/gka/chroma.js/blob/main/LICENSE) |
| **Material / Tonal palettes** (UI scale) | UI | **Apache-2.0** (Google) ✅ | tonal: 0–100 명도 톤(예: blue `40:#0061A4`) | (참고) tonal 단색 강도 → 트리맵 단색 램프 가능 | HCT 기반 지각 톤. Autofolio는 이미 Radix/Tailwind류로 충분 | [LICENSE](https://github.com/material-foundation/material-color-utilities/blob/main/LICENSE) |

### 권장

**1) 히트맵 (Fidelity Today Gain/Loss 스타일) — *부호 있는* PnL 변동:** **ColorBrewer RdBu(또는 Paul Tol BuRd)** 를 KR 관습에 맞춰 **반전 매핑**. 양(상승)→빨강 끝, 음(하락)→파랑 끝, 0 부근→중립 `#f7f7f7`.
- KR diverging 램프(5-class): `#0571b0`(큰 하락) · `#92c5de` · `#f7f7f7`(보합) · `#f4a582` · `#ca0020`(큰 상승). *데이터→색 스케일을 KR 부호 규약에 배치.*

**2) 트리맵 (집중도) — *단방향* 강도:** **Viridis(또는 CVD 우선이면 Cividis)** 또는 **ColorBrewer Blues**. 집중도(비중)는 부호 없는 크기 → diverging이 아닌 sequential.
- 1순위 **Viridis** `#440154→#3B528B→#21908C→#5DC863→#FDE725`(CC0). 브랜드 정합 우선이면 **Blues 7-class** `#eff3ff … #084594`.
- ⚠️ 밝은 타일엔 어두운 글자, 어두운 타일엔 흰 글자로 **명도 기준 자동 대비 전환**(텍스트 4.5:1).

**3) KR PnL diverging 램프 (색맹-안전 + 중립 midpoint) — 최종 추천:** **ColorBrewer RdBu(=Paul Tol BuRd reverse).** ColorBrewer가 RdBu를 colorblind-safe로 명시 분류 + Paul Tol도 BuRd를 동일 보증 → **두 독립 권위가 동일 램프를 CVD-안전으로 보증**. 중립 `#f7f7f7`이 보합을 또렷이 분리.
- 5-class(KR: 빨=상승, 파=하락): 상승↑ `#ca0020` `#f4a582` · 보합 `#f7f7f7` · `#92c5de` `#0571b0` ↓하락.
- 비색 중복 인코딩 필수(WCAG 1.4.1): 색 + `▲/▼` + `+/−` 부호 동반.
- **categorical 시리즈 색과 네임스페이스 분리**(기존 문서 원칙 유지): 트리맵 sequential·도넛 categorical(Okabe-Ito/Tol bright)·히트맵 diverging은 서로 다른 토큰 세트.

**4) Western 토글(상승=초록):** RdBu는 초록을 못 담음. Western 전용 diverging이 필요하면 `초록=#1a9850 / 중립=#f7f7f7 / 빨강=#d73027`(RdYlGn은 적록색맹 취약 → 회피), 반드시 ▲/▼ 병행. 가장 안전한 길은 **PnL 의미를 부호+화살표에 싣고 색은 보조로 격하**.

**5) dark-mode 토큰 (`#3182F6` 가이드):** 브랜드 blue를 다크 배경에 그대로 얹으면 대비 저하 → **Radix `blue dark` scale** 토큰화:
- 솔리드 강조 **`--blue-9 #0090ff`** 또는 **`--blue-10 #3b9eff`**; 라인/텍스트 대비 **`--blue-11 #70b8ff`**; 제목 **`--blue-12 #c2e6ff`**; 표면/보더 `--blue-2 #111927`·`--blue-6 #104d87`.
- **light=브랜드 `#3182F6`(=Tailwind blue-500), dark=Radix blue-9/10/11** 매핑. 데이터 인코딩 색은 항상 위 CVD 팔레트로, 표면/chrome만 dark UI scale.

**표면별 매핑 요약:**

| 표면 | 권장 팔레트 | 유형 |
|---|---|---|
| 히트맵 (Today Gain/Loss) | ColorBrewer RdBu / Tol BuRd (KR 부호 매핑) | diverging |
| 트리맵 (집중도) | Viridis(1순위) / Cividis(CVD우선) / Blues(브랜드) | sequential |
| AllocationChart 도넛 | Okabe-Ito(기존) 또는 Tol bright/muted | categorical |
| EquityChart PnL 음영 | KR RdBu 양끝(상승 `#ca0020` / 하락 `#0571b0`) | diverging 의미색 |
| style box (3×3) | Blues 또는 viridis 단색 강도 | sequential |
| dark-mode 토큰 (`#3182F6`) | Radix blue dark (9/10/11/12) | UI scale |
| 다크 차트 배경 | Radix gray/blue dark 1–2, Catppuccin Mocha | UI scale |

### 제외 / 주의

- ⚠️ **Paul Tol 라이선스 미확정:** SRON 기술노트에 **명시 라이선스 텍스트가 없음**(검증일 2026-06-19). hex 값은 다수 OSS에 광범위 임베드되어 자유 사용이 통념이나 **상용 임베드 전 저자 확인 권장**. 라이선스 명확성 우선이면 **CC0(viridis/cividis) 또는 Apache-스타일+귀속(ColorBrewer)로 대체** — sunset≈RdYlBu, BuRd=RdBu reverse라 ColorBrewer로 거의 동치 치환 가능.
- ⚠️ **ColorBrewer 귀속 의무:** 채택 시 문서/SW에 *"This product includes color specifications and designs developed by Cynthia Brewer (http://colorbrewer.org/)"* 표기 필수, 제품명에 "ColorBrewer" 사용 금지. d3-scale-chromatic·chroma.js 경유 시에도 의무 승계.
- **제외 — RdYlGn / 일반 red-green diverging:** 적록색맹에 가장 취약. PnL을 색 단독 인코딩 금지.
- ⚠️ **UI scale(Radix/Open Color/Tailwind/Material)은 데이터 인코딩 CVD-안전을 보장하지 않음** — UI chrome/토큰/계조용. 차트 데이터 색은 반드시 CVD-검증 팔레트(Okabe-Ito, Tol, Viridis/Cividis, ColorBrewer)에서.
- ⚠️ **대비 캐비엇(흰 배경, SC 1.4.11 데이터 3:1):** diverging 중앙색(`#f7f7f7`,`#ffffbf`,`#EAECCC`)·sequential 밝은 끝(`#ffffb2`,`#FDE725`)은 흰 배경 대비 3:1 미달 → **셀/타일 경계선** 또는 **어두운 배경** 병용. 최종 [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)로 확인.
