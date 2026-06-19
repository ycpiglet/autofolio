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
