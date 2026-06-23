# 신규 비주얼 컴포넌트 — 채택·배선 가이드

> 이 PR(`feat/ui-asset-impl`)이 추가한 **net-new 자체호스팅 컴포넌트/모듈**과, 각각을 **어느 기존 화면에 배선**할지 맵. 모든 항목은 단위테스트(`npm run test:unit`) + `npm run build`로 검증됨. 기존(동시 편집 중) 파일은 **무접촉**으로 추가했고, 배선은 충돌 최소화를 위해 별도 단계로 둠.
> 검증: `cd web && npm run test:unit` (vitest, 95+ pass) · `npm run build`. 라이선스 NOTICE: `docs/research/third-party-notices-draft-expanded.md`.

## 추가된 것 (전부 net-new)

| 모듈/컴포넌트 | 무엇 | 의존성 | 배선 대상(기존 화면) |
|---|---|---|---|
| `lib/format.ts` `fmtWonShort`/`fmtWonShortSigned` | 만/억 단축(₩1.2억) | 0 | 금액 셀 전반(`HoldingsTable`·`DataTable`·`KpiCard`) |
| `lib/chart-palette.ts` | CVD-safe categorical/diverging/sequential/dark 토큰 + 헬퍼 | 0 | 차트 색을 이 토큰으로(`design-tokens.ts` 통합 또는 직접 import) |
| `components/ui/Avatar.tsx` (+`lib/avatar.ts`) | DiceBear 계정/에이전트 아바타 | @dicebear | 계정 헤더·`agents/` 탭(에이전트별 `seed`) |
| `components/domain/EquityChartUplot.tsx` (+`lib/equity-series.ts`) | uPlot 자산곡선(경량) | uplot | `EquityChart.tsx` 엔진 교체 또는 신규 사용처 |
| `components/domain/EquityChartRanged.tsx` (+`lib/equity-range.ts`) | **기간 선택기(1D~ALL) + 기간수익 컬러링(P1 #1)** | uplot | `home/page.tsx`·`portfolio/page.tsx`의 자산곡선 자리 |
| `components/domain/CandleChartKline.tsx` (+`lib/candle-series.ts`) | KLineChart 캔들(KR 빨/파) | klinecharts | `CandleChart.tsx` 또는 분석 탭 |
| `components/domain/Sparkline.tsx` (+`lib/sparkline-util.ts`) | 테이블 셀 미니추세 | @fnando/sparkline | `HoldingsTable.tsx` 행별 컬럼 |
| `components/domain/AllocationTreemap.tsx` (+`lib/treemap.ts`) | 집중도 트리맵(P2) | 0 | `AllocationChart.tsx` 옆 드릴다운/대안 뷰 |
| `components/ui/EmptyState.tsx` (+`ui/illustrations/*`) | 빈/에러/온보딩 상태 | 0 | 빈 리스트/결과/에러(차트·테이블·내역) — `@/components/ui/EmptyState` |
| `components/ui/icons/CurrencyWon`·`Candlestick` | Lucide 결핍 글리프(₩·캔들) | 0 | `SidebarNav`·금액/차트 라벨 |
| `components/ui/Flag.tsx` (+`lib/flags.ts`) | 국기 kr/us/cn/jp/eu(circle-flags MIT) | 0 | FX/멀티마켓 통화 피커·계좌 행 |

## 배선 원칙

1. **충돌 최소화**: 배선 대상 다수(`HoldingsTable`·`AllocationChart`·`SidebarNav`·`globals.css`·`portfolio/page`)가 현재 동시 세션 편집 중 → 그 파일들이 정리(커밋)된 뒤 배선하면 머지 충돌 0. `EquityChart.tsx`·`CandleChart.tsx`·`home/page.tsx`는 비교적 깨끗.
2. **엔진 교체형**(EquityChart→uPlot, CandleChart→KLineChart)은 공개 API 보존 + **prod E2E(CI=1)·브라우저 스모크로 시각 회귀 확인** 후 머지.
3. **신규 표면**(아바타·트리맵·빈상태·국기 피커)은 새 위치에 추가 → 회귀 위험 낮음, 우선 배선 권장.
4. KR PnL 관습(상승=빨강/하락=파랑)·자체호스팅(런타임 CDN 0)·`tabular-nums`·WCAG(색 단독 금지) 준수.

## 미적용(별도)
- **폰트(C1, Wanted Sans/SUIT)**: woff2 자체호스팅 + `globals.css`/layout(동시 편집 중) 통합 필요 → 별도.
- **실제 일러스트 큐레이션(B)**: 현재 EmptyState는 자체 제작 브랜드 SVG 기본값 — unDraw/Open Doodles 교체는 디자인 결정.
