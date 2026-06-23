# UI 개선 백로그 (TASK 후보) — 데이터viz + 에셋 (2026-06-19)

> 리서치 산출물. **구현은 별도 승인 후**. 각 항목은 `agents/lead_engineer/tasks/`의 정식 TASK로 승격 가능(번호는 승격 시 부여 — 동시 세션과 충돌 방지). `docs/design-system.md` 제안 모드(Light/Standard/Heavy)에 매핑.

## P1 — 높은 임팩트 / 낮은 노력
1. **EquityChart 기간 선택기 + 기준선 컬러링** — 1D/1W/1M/3M/1Y/ALL 세그먼트, 기간수익 부호로 면적 컬러링(KR red/blue), 시작값 기준선. 파일 `web/src/components/domain/EquityChart.tsx`(+데이터 레이어). 모드: **Standard**.
2. **숫자 포맷 일원화 + 만/억 단축** — 모든 셀을 `web/src/lib/format.ts` 경유, `fmtWonShort`(만/억) 추가, 부호·tabular 일관. 파일 `format.ts`,`HoldingsTable.tsx`,`DataTable.tsx`. 모드: **Light~Standard**.
3. **차트 categorical 팔레트 분리(색맹 안전)** — `web/src/lib/design-tokens.ts`에 `categoricalPalette`(Okabe-Ito 7색) 신설, PnL 의미색과 분리. 모드: **Standard**. (상세: `dataviz-pattern-gap-analysis.md` §3)

## P2 — 중간
4. **사이드바 이모지 → Lucide 아이콘** — `web/src/components/layout/SidebarNav.tsx` `icon` 타입 변경 + 매핑(홈/포트폴리오/매매/내역/분석/에이전트/알림/성향진단/설정). 모드: **Light**.
5. **빈/에러 상태 일러스트 + 마이크로카피** — unDraw(#3182F6 리컬러) `web/public/illustrations/` 자체호스팅, 친근 해요체+다음단계 안내, 문자열 중앙화. 차트·테이블·리스트 컴포넌트. 모드: **Standard**.
6. **PnL CVD 안전 + 비색 신호** — `format.ts` `pnlColor`에 CVD-safe 변형 + ▲/▼ 글리프 병기, `globals.css` 토큰. 모드: **Light**.
7. **배분 차트 드릴다운** — `AllocationChart.tsx` 셀 클릭 필터(+ 집중도 treemap 변형 선택). 모드: **Standard**.
8. **모바일 차트 스크럽** — `EquityChart`/`CandleChart` crosshair-move→값/날짜 읽기. 모드: **Standard**.
9. **차트 a11y 보강** — 캔버스 차트(lightweight-charts)마다 숨김/확장 데이터테이블 병행, 툴팁/범례 키보드·ARIA. 모드: **Standard**.

## P3 — 큰 작업 / 후순위
10. **보유 테이블 스파크라인 + 저장 뷰** — `HoldingsTable.tsx` 행별 미니 추세 + 컬럼 구성 저장. 모드: **Standard**.
11. **타입 스케일 + 엘리베이션 토큰** — 명시 스케일·elevation 3단계·`<Brand/>` 컴포넌트 추출. `globals.css`,`design-tokens.ts`. 모드: **Standard**.
12. **다크모드 준비** — 의미색 대비 점검·다크 대응 토큰. 모드: **Heavy**(전역 영향).
13. **캔들 보조지표(선택)** — MA/거래량/RSI opt-in. `CandleChart.tsx`. 모드: **Standard**.
14. **파비콘/브랜드 마크** — 자체 SVG 마크 + 파비콘 세트로 `web/public/` Next 플레이스홀더 교체. 모드: **Light**.

## 공통 준수
- 구현 시 `web/AGENTS.md`(Next.js 16: node_modules/next/dist/docs 선독) 준수.
- KR PnL 관습(상승=빨강/하락=파랑) + Western 토글 유지.
- 에셋은 자체호스팅(런타임 CDN 0), 라이선스 채택 전 재확인(특히 unDraw 팩-재배포 금지·Remix 비표준).
- 검증: `docs/design-system.md` 규칙 위반 0, `scripts/design_system_gate.py --check` 경고 감소, prod 모드 E2E(CI=1).

## 확장 리서치 추가 후보 (2026-06-19b) — Top 12

> 출처: [확장 리서치 개요](./2026-06-19-open-source-visual-assets-expanded.md) 및 토픽 5문서. 전부 퍼미시브(MIT/Apache/ISC/CC0/OFL)·자체호스팅(런타임 CDN 0) 검증(2026-06-19).
> **정식 TASK 승격 상태:** 보류 — 등록 시점에 동시 세션이 TASK 레지스트리(INDEX/AUDIT-LOG, TASK-115~119)를 작업 중이라 번호·파일 충돌 위험. **레지스트리 비경합 시점에 TASK-120+ 로 승격**(COMPOUND-032: 열린 작업은 TASK 로 존재 — 본 목록이 그 중간 보관소).

| # | 후보 | 영역 | 대표 자원(라이선스) | 대상 파일 | 우선도 | 충돌 위험 |
|---|---|---|---|---|---|---|
| E1 | 자산곡선·KPI 미니차트 경량화 | 그래프 | uPlot (MIT) + uplot-react | `EquityChart.tsx`·`KpiCard.tsx`(+데이터) | P1 | 중(EquityChart 동시수정 여부 확인) |
| E2 | 캔들 전용 엔진 + 내장 지표 | 그래프 | KLineChart (Apache-2.0) | `CandleChart.tsx` | P1 | 중 |
| E3 | 테이블 셀 스파크라인 | 그래프 | @mui/x-charts SparkLineChart(MIT) 또는 @fnando/sparkline(MIT) | `HoldingsTable.tsx` | P2 | 높음(동시수정 중) |
| E4 | 히트맵·KR PnL diverging 팔레트 | 컬러 | ColorBrewer RdBu(귀속) | `design-tokens.ts`·신규 히트맵 | P1 | 높음(design-tokens untracked) |
| E5 | 트리맵(집중도) sequential 팔레트 | 컬러 | Viridis/Cividis (CC0) | `design-tokens.ts`·`AllocationChart.tsx` | P2 | 높음 |
| E6 | dark-mode `#3182F6` 토큰 | 컬러 | Radix Colors (MIT) | `design-tokens.ts`·`globals.css` | P2 | 높음 |
| E7 | 숫자 포맷 만/억 단축 + tabular 일원화 | 포맷 | (자체) `fmtWonShort` | `format.ts`(+테이블) | **P1** | **낮음(format.ts clean)** ← 우선 착수 |
| E8 | Lucide 보완 + ₩·candlestick 글리프 | 아이콘 | MingCute(Apache)·Tabler `currency-won`(MIT) | `SidebarNav.tsx`·아이콘 매핑 | P2 | 높음(SidebarNav 동시수정) |
| E9 | 국기(FX·멀티마켓) | 아이콘 | circle-flags + flag-icons (MIT) | 통화 피커·계좌행(신규) | P2 | 낮음(신규) |
| E10 | 계정·AI 에이전트 아바타 | 캐릭터 | DiceBear Notionists/Bottts(CC0/무료)·Boring Avatars(MIT) | 계정·에이전트 탭(신규 모듈) | P2 | 낮음(신규) |
| E11 | 빈/에러/온보딩 일러스트 + 마스코트 | 이미지 | Open Doodles/IRA Design·unDraw | `web/public/illustrations/`(신규) | P2 | 낮음(신규 에셋) |
| E12 | 금융 대시보드 컴포넌트 채택 평가 | 컴포넌트 | shadcn/ui(MIT) + Tremor(Apache) | 평가 문서 → 점진 도입 | P3 | 낮음(평가 우선) |

**자율 착수 순서(충돌 낮은 것부터):** E7(format.ts) → E9/E10/E11(신규 모듈·에셋) → 동시 세션 web 변경 정리 후 E1~E6·E8(기존 컴포넌트 수정).
