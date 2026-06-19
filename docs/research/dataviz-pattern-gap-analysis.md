# 데이터 시각화 — 패턴 갭 분석 + 차트 팔레트 제안 (2026-06-19)

> 리서치 기반. 코드 변경 없음. 인용 URL은 각 항목에 표기. 불확실 항목은 ⚠️로 플래그.

## 1. 레퍼런스 데이터viz 패턴 (요약)
- **Robinhood**: 단일 라인 중심·1D~ALL 기간선택, 전일종가 기준선 대비 라인 green/red 리컬러(⚠️ 공식 "Using charts" 페이지엔 미재진술 — 널리 보도되나 비공식), 캔들 green=up/red=down, 모바일 **롱프레스 스크럽** 값 읽기, Spark 스파크라인 오픈소스. ([Using charts](https://robinhood.com/us/en/support/articles/using-charts/), [Advanced charts](https://robinhood.com/us/en/support/articles/using-advanced-charts), [robinhood/spark](https://github.com/robinhood/spark))
- **Fidelity**: 강력한 **포지션 테이블**(컬럼 드래그·추가/삭제·Save View), 탭로트 인라인 확장, 실시간 종목 노랑 하이라이트·계산 툴팁 점선밑줄, **Today Gain/Loss 히트맵**(밝을수록 큰 변동, 박스 크기=집중도), 배분 pie+스타일박스. ([Positions What's New](https://www.fidelity.com/accounts/popups/positions-whats-new.shtml))
- **Schwab**(⚠️ 도메인이 자동 fetch 차단 — 검색 추출): 배분 pie 셀 클릭 드릴다운, 성과는 벤치마크 비교, 2025-12 확장-시간 평가 토글·테이블뷰 추가. ([extract](https://www.schwab.com/content/how-to-use-performance-reporting))
- **토스증권**: 초심자 우선 — **면적/라인 추세선 + 하단 기간버튼**, 출시 때 캔들 미포함(나중 opt-in), 보유는 간결 리스트·상단 수익률, **자산배분/총자산 추세 그래프 없음**(입출금·환율 왜곡 이슈), 마이크로카피 "구매/판매", 친근 해요체 에러시스템. ⚠️ 색 토글 부재는 포럼 출처. ([weeklyux 티어다운](https://weeklyuxuichallenge.oopy.io/19662e31-fc9c-8043-85cc-fe7880bc7d87), [toss.tech 8 writing principles](https://toss.tech/article/8-writing-principles-of-toss), [toss error message system](https://toss.tech/article/introducing-toss-error-message-system))
- **카카오페이증권/미니스탁**: 총자산+수익률 우선, 소수점 매수 e-커머스식 바텀모달·배송추적식 진행, 지표 풍부한 차트. ([brunch](https://brunch.co.kr/@kellypoly/26))
- **보조 — Bloomberg**: green/red + **색맹 안전(CVD) 팔레트를 명시적으로 구축**(red/green 색상이 너무 유사). **Morningstar X-Ray**: 배분 pie + 섹터/지역 + Style Box(3×3, 가중평균 빨강 점). ([Bloomberg UX color accessibility](https://www.bloomberg.com/ux/2021/10/14/designing-the-terminal-for-color-accessibility/), [X-Ray](https://www.morningstar.co.uk/uk/xray/overview))

## 2. 현재 Autofolio 대비 갭 분석
| 영역 | 현재 | 레퍼런스 best-practice | 권장 변경(파일) | 우선도 |
|---|---|---|---|---|
| 기간 범위(자산곡선) | `EquityChart` 180d 고정·선택기 없음 | 모든 제품 1D/1W/1M/3M/1Y/ALL | 범위 칩 + 슬라이스/리페치; `EquityChart.tsx` | **P1** |
| 기준선/손익 음영 | 정적 blue 면적, 기준선 없음 | RH 전일종가 기준 green/red; KR=red up/blue down | 기간 부호로 면적 컬러링 + 시작값 기준선; `EquityChart.tsx` | **P1** |
| 숫자 포맷 일관성 | 컴포넌트별 `toLocaleString`·부호 제각각, 만/억 없음 | tabular figures, 일관 부호, 만/억 | 전 셀 `format.ts` 경유 + `fmtWonShort`; `format.ts`,`HoldingsTable.tsx`,`DataTable.tsx` | **P1** |
| PnL 색(CVD 안전) | KR red-up/blue-down + 토글, 색이 유일 신호 | Bloomberg CVD-safe 팔레트 | CVD-safe 변형 + ▲/▼ 비색 신호; `format.ts`,`globals.css` | **P2** |
| 배분 깊이 | `AllocationChart` 정적 donut | Schwab 셀 클릭 드릴다운; 집중도 treemap | 클릭 필터 + treemap 변형; `AllocationChart.tsx` | **P2** |
| 보유 테이블 밀도 | 텍스트 행, 추세 없음 | RH/Fidelity 스파크라인·히트맵, 저장 뷰 | 행별 스파크라인 컬럼; `HoldingsTable.tsx` | **P3** |
| 모바일 차트 인터랙션 | 정적·리사이즈만 | RH 롱프레스 스크럽·핀치/팬 | crosshair-move→값/날짜 읽기; `EquityChart.tsx`,`CandleChart.tsx` | **P2** |
| 캔들 지표 | KR red-up/blue-down 캔들(정확)·지표 없음 | RH 7지표·KakaoPay 지표 풍부·Toss opt-in | (선택) MA/거래량/RSI; `CandleChart.tsx` | **P3** |
| 빈/에러·마이크로카피 | 기능적 KR 문구 | Toss 친근 해요체·다음단계 안내·쉬운 라벨 | 다음단계 안내 + 따뜻한 보이스 + 문자열 중앙화 | **P2** |
| KPI | `KpiCard` `.kpi`(26/700/tabular) + `PnlText` | Toss/Kakao 총자산+수익률 상단 노출 — 일치 | 이미 정렬됨, 만/억 단축만(선택) | **P3** |

## 3. 차트 팔레트 제안 (색맹 안전 + Toss-blue 호환)
**문제**: 현재 `chartSeriesPalette`가 `primary(#3182F6)/negative(#F04452)/positive(#34C759)`를 categorical과 PnL 양쪽에 재사용 → 의미 충돌.
**원칙**: **PnL 의미색과 categorical 색의 hue 정체성은 절대 겹치지 않게 분리.**

### categorical 팔레트 — Okabe-Ito CUD (peer-reviewed CVD-safe)
출처: [CUD jfly](https://jfly.uni-koeln.de/color/), hex 참고 [easystats see](https://easystats.github.io/see/reference/scale_color_okabeito.html). Okabe-Ito Blue `#0072B2`가 Toss-blue 계열이라 on-brand 앵커.

| 슬롯 | Hex | 이름 | 비고 |
|---|---|---|---|
| cat-1 | `#0072B2` | Blue | 브랜드 계열 앵커, CVD-safe |
| cat-2 | `#E69F00` | Orange | blue 대비 높음 |
| cat-3 | `#009E73` | Bluish-green | PnL green과 구분 |
| cat-4 | `#CC79A7` | Reddish-purple | |
| cat-5 | `#56B4E9` | Sky-blue | ⚠️ 흰 배경 대비 ~1.9:1 → 채움+테두리에만 |
| cat-6 | `#D55E00` | Vermilion | |
| cat-7 | `#F0E442` | Yellow | ⚠️ 흰 배경 ~1.1:1 → 어두운 채움에만 |

**대안(≤5색)**: IBM Carbon CVD-safe `#648fff #785ef0 #dc267f #fe6100 #ffb000` (Viz Palette·WCAG 검증). ([Carbon dataviz](https://medium.com/carbondesign/color-palettes-and-accessibility-features-for-data-visualization-7869f4874fca))

### PnL 의미색 분리
- `pnlColorTokens`(KR up `#F04452`/down `#3182F6`, Western up `#34C759`, flat `#8E8E93`)는 그대로 — **이 3~4색은 오직 의미색으로만** 사용.
- `chartSeriesPalette`에서 `primary/negative/positive` 제거, categorical 앵커는 `#0072B2`(또는 `#648fff`), categorical green은 `#009E73`로. → "하락(#3182F6)"과 "카테고리(#0072B2)"가 다른 음영.
- 비색 중복 인코딩: up/down은 색만이 아니라 +/− 부호·화살표·위치도 동반(WCAG 1.4.1).

### 대비(WCAG)
- 데이터 색 vs 배경 **3:1**(SC 1.4.11). ⚠️ 흰 배경에서 `#F0E442`(~1.1:1)·`#56B4E9`(~1.9:1)는 미달 → 어두운 채움/테두리 병용.
- 차트 내 텍스트 라벨 **4.5:1**(SC 1.4.3). ⚠️ muted `#8B95A1`은 흰 배경 ~2.6:1 미달 → 수치 라벨엔 더 진한 회색(예 `#4E5968`).
- 그리드/보더(`#DDEE...#DDE1E7`)는 장식 → 저대비 유지 OK. (정확치는 [WebAIM Checker](https://webaim.org/resources/contrastchecker/)로 최종 확인.)
- 모든 수치 라벨 `tabular-nums`.

### design-tokens.ts 확장 방향(코드 아님)
`web/src/lib/design-tokens.ts`에 `categoricalPalette`(Okabe-Ito 7색) 신설 → `chartSeriesPalette`/`compactChartSeriesPalette`가 이를 가리키게. `pnlColorTokens`/`candleSeriesColors`/`equityAreaColors`/`lightweightChartTheme`는 불변. 앵커는 `catBlue:"#0072B2"`처럼 브랜드 `primary`와 구분 명명.

## 4. 시각화 라이브러리 비교 (라이선스 검증)
| 라이브러리 | 라이선스(검증·출처) | 비고 |
|---|---|---|
| **Recharts v3** (사용중) | **MIT** ([LICENSE](https://github.com/recharts/recharts/blob/master/LICENSE)) | 표준 차트 전반·DOM/ARIA·토큰 주입 쉬움 |
| **lightweight-charts v5** (사용중) | **Apache-2.0**, 로고/링크 강제 없음 ([LICENSE](https://github.com/tradingview/lightweight-charts/blob/master/LICENSE)) | 금융 시계열 특화·캔버스·초경량. ⚠️ 캔버스=스크린리더 비가시 |
| Apache ECharts | **Apache-2.0** ([LICENSE](https://github.com/apache/echarts/blob/master/LICENSE)) | 최대 카탈로그, 트리셰이킹 필수(전체 ~700-900KB) |
| IBM Carbon Charts | **Apache-2.0** ([repo](https://github.com/carbon-design-system/carbon-charts)) | a11y·CVD 팔레트 최강, D3+Carbon 무게 |
| Nivo | **MIT** ([LICENSE](https://github.com/plouc/nivo/blob/master/LICENSE.md)) | 넓은 차트·기본값 좋음, 번들 큼. ⚠️ "WCAG AA out of box"는 3자 리뷰 주장 |
| Visx | **MIT** ([LICENSE](https://github.com/airbnb/visx/blob/master/LICENSE)) | 저수준 프리미티브, a11y 직접 구현 부담 |
| Shopify Polaris(viz) | 디자인시스템 *가이드*(의존성 X) | "색만으로 인코딩 금지" 규칙 참고용 |

**권장**: **recharts + lightweight-charts 유지**(라이선스 깨끗·상보적·오프라인 OK). 전면 교체 불필요. **a11y만 패턴 차용**: 캔버스 차트마다 숨김/확장 데이터테이블 병행 + Carbon 색 방법론 + Polaris "색 단독 금지". 특정 차트(heatmap/sankey/calendar)만 필요하면 **Nivo를 그 차트에만** 좁게 추가.

## 5. 인터랙션 가이드
- **툴팁**: 고정 영역(코너/플롯 핀) — 현재 fixed-position 전환은 올바름. a11y: 툴팁은 포커스 불가, 트리거 키보드 도달·focus에서도 열림·Esc 닫힘·`aria-describedby` 연결. ([WAI tooltip](https://pressbooks.library.torontomu.ca/wafd/chapter/tooltips/))
- **기간 선택기**: 프리셋(1D~ALL) 세그먼트 + 선택 상태 표시 + 포커스 가능 버튼 + 뷰 간 선택 유지.
- **범례**: 클릭=시리즈 토글/더블클릭=단독, 상/하단 배치, 포커스 가능, 색 칩+라벨 텍스트 병기. ([AG Charts](https://www.ag-grid.com/charts/javascript/legend/))
- **크로스헤어**: 시계열은 동기화 수직선+값 읽기, 최근접 데이터점 스냅, 고정 툴팁에 값 표기.
- **hover/focus a11y**: 모든 hover에 키보드 등가(화살표로 데이터점 이동). 캔버스 차트는 데이터테이블 병행. 색 단독 인코딩 금지(WCAG 1.4.1).

### 불확실성 플래그
RH 라인 리컬러/점선 기준선은 비공식; Schwab 시각 사양은 검색추출만; "토스/카카오 색 토글 부재"는 포럼; 대비 수치는 추정(최종 WebAIM 확인); "Nivo AA out-of-box"는 3자 리뷰; Carbon 14색 전체 미열거(검증된 5색만).
