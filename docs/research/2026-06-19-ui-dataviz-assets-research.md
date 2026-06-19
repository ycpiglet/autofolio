# UI/UX 리서치 — 데이터 시각화 + 에셋 (2026-06-19)

> 산출물: **리서치/큐레이션 문서만**. 코드·의존성 변경 없음. 적용은 별도 승인 후 단계적 진행.
> 우선 영역: ① 데이터 시각화, ② 에셋·비주얼. 레퍼런스: 미국 증권(Robinhood/Fidelity/Schwab) + 오픈소스 디자인시스템(Carbon/Polaris) + 한국 핀테크(토스/카카오·토스증권). (Bloomberg/Morningstar 보조.)
> 관련 계획: `~/.claude/plans/stateful-prancing-rain.md` · 베이스라인: `reviews/DIAGNOSTIC-2026-06-18-ui-design-system-maturity.md` (UI 성숙도 2.6/5)

## 이 묶음의 문서
1. **이 문서** — 개요·핵심 권고·검증 자세.
2. [`dataviz-pattern-gap-analysis.md`](./dataviz-pattern-gap-analysis.md) — 레퍼런스 차트 패턴, 현재 대비 갭, **색맹 안전 차트 팔레트 제안**, 라이브러리 비교, 인터랙션 가이드.
3. [`asset-curation-matrix.md`](./asset-curation-matrix.md) — 아이콘/일러스트/브랜드/타이포 에셋 **라이선스 검증** 매트릭스.
4. [`ui-improvement-backlog.md`](./ui-improvement-backlog.md) — 우선순위 개선 백로그(TASK 후보).

## Executive Summary
- Autofolio의 **캔들·KPI·PnL 색 관습은 이미 한국 best-practice와 일치**(상승=빨강 `#F04452` / 하락=파랑 `#3182F6`, Western 토글). 즉 "방향성"은 맞다.
- 진짜 갭은 **상호작용과 일관성**: ① `EquityChart`에 **기간 선택기(1D/1W/1M/3M/1Y/ALL)와 기준선 컬러링 없음** — 모든 레퍼런스 제품의 공통 기본기. ② 숫자 포맷이 컴포넌트마다 제각각(`format.ts`로 일원화 필요, 만/억 단축 추가). ③ 모바일 스크럽·배분 드릴다운·보유 스파크라인 등 인터랙션 부재.
- **차트 팔레트가 ad-hoc**: 현재 categorical 시리즈가 PnL 의미색(브랜드 blue/up red/down blue)을 재사용 → "카테고리 blue"와 "하락 blue"가 충돌. **categorical과 PnL 색 네임스페이스 분리 + 색맹 안전 팔레트(Okabe-Ito)** 권장.
- **에셋**: 아이콘은 이미 설치된 **Lucide(ISC/MIT) 단일화** + **사이드바 이모지 → Lucide 교체** 권장. 빈/에러 상태는 **unDraw(브랜드색 #3182F6로 리컬러)**, 온보딩 캐릭터는 **Open Peeps/Humaaans(CC0)**. 브랜드는 **Pretendard 기반 워드마크** 유지 + 자체 제작 기하 마크(선택). 커스텀 로고/AI 생성 불필요.
- 모든 추천 에셋은 **오픈소스·관대 라이선스 + 자체호스팅(런타임 CDN 0)** — Autofolio의 오프라인 자세와 일치.

## 가장 높은 레버리지 권고 (Top 5)
| # | 권고 | 영역 | 대상 파일 | 우선도 |
|---|---|---|---|---|
| 1 | EquityChart에 기간 선택기 + 기간수익 기준선 컬러링 | 데이터viz | `EquityChart.tsx` (+데이터 레이어) | P1 |
| 2 | 숫자 포맷을 `format.ts`로 일원화 + 만/억 단축(`fmtWonShort`) | 데이터viz | `format.ts`, `HoldingsTable.tsx`, `DataTable.tsx` | P1 |
| 3 | categorical 팔레트를 PnL 의미색과 분리(색맹 안전 Okabe-Ito) | 데이터viz | `design-tokens.ts` | P1 |
| 4 | 사이드바 이모지 → Lucide 아이콘 단일화 | 에셋 | `SidebarNav.tsx` | P2 |
| 5 | 빈/에러 상태 일러스트(unDraw #3182F6) + 친근한 다음단계 마이크로카피 | 에셋/UX | 차트·테이블 컴포넌트, `web/public/illustrations/` | P2 |

## 검증 자세 (중요)
- **라이선스는 각 출처의 실제 LICENSE 파일/공식 라이선스 페이지에서 확인**했고(검증일 2026-06-19, URL은 매트릭스에 인용), 제약은 명시 플래그함. 그래도 **채택 전 최종 재확인 권장**(라이선스는 변경될 수 있음 — 예: Remix Icon은 2024년 Apache-2.0 → 커스텀 v1.0으로 변경됨).
- **제외(라이선스 사유)**: Streamline Free(귀속 강제 + 앱 자산 통합 제한), Glaze/glazestock(작가별 귀속·큐레이션 스톡·도메인 리다이렉트).
- **주의(정상 사용엔 무방하나 준수 필요)**: unDraw·DrawKit은 팩 재배포/AI 학습 금지 → 필요한 SVG만 자체호스팅(핫링크·재패키징 금지). Remix Icon은 아이콘을 로고/브랜드로 사용 금지.
- 일부 시각/수치 디테일(예: Robinhood 라인 리컬러·점선 기준선, Schwab 시각 사양, 토스/카카오 색 토글 부재)은 **공식 페이지 외 출처(티어다운/포럼)** 기반 → 각 문서에 불확실성 플래그 표기.

## 다음 단계 (적용은 별도 승인)
백로그(문서 4)를 보고 P1부터 `docs/design-system.md`의 제안 모드(Light/Standard/Heavy)에 맞춰 구현 웨이브로 진행. 구현 시 `web/AGENTS.md`의 Next.js 16 주의(node_modules/next/dist/docs 선독) 준수, KR PnL 관습·Western 토글 유지.
