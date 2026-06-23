# 확장 비주얼 에셋 — 채택·검증 실행 플랜 (2026-06-19)

> 리서치/큐레이션 묶음의 **실행 레이어.** [개요](./2026-06-19-open-source-visual-assets-expanded.md)·[백로그 후보 E1~E12](./ui-improvement-backlog.md)가 *무엇을* 채택할지라면, 이 문서는 *어떻게 안전하게 착수·검증*하고 *동시 세션 경합을 어떻게 다루는지*다. 코드·의존성 변경 0.

## 0. 이번 세션 착수 현황 (참조)

- **PR #95** (docs): 확장 리서치 6문서 + 백로그 후보 E1~E12. docs-only.
- **PR #96** (code): `format.ts`에 `fmtWonShort`/`fmtWonShortSigned`(E7 1차). 검증: node 동작 오라클 11/11 + tsc(format.ts) + eslint clean. **테이블/차트 배선은 후속**(아래 §3).

## 1. 동시성 좌표 (반드시 먼저 읽기 — 2026-06-19 관측)

작업 시작 시 이 레포의 실제 상태는 **커밋된 main보다 한참 앞서 있고, 그 차이가 미커밋으로 공유 작업트리에 떠 있다**:

| 관측 | 값 | 함의 |
|---|---|---|
| `main` 커밋 tip | TASK-**074**까지 | 정식 TASK 레지스트리의 committed base가 stale |
| 작업트리(공유) 실제 | TASK-**119**까지(075~119 **미커밋**) + INDEX/AUDIT-LOG/BACKLOG/STATUS/tasks.index.json **dirty** | 동시 세션 다수가 거버넌스·web·backend를 동시 편집 |
| web `package.json` 스크립트 | `lint`(eslint)·`test:e2e`(playwright)만 | **단위 테스트 러너(vitest/jest) 없음** |

**결론(좌표 규칙):**
- 격리가 필요하면 **`git worktree`는 `HEAD`(현재 브랜치) 기준으로** 만들 것. `main` 기준은 075~119가 없어 대규모 충돌을 만든다.
- **정식 TASK 승격(E*→TASK-120+)은 동시 세션이 075~119 + 거버넌스 파일을 커밋해 레지스트리가 안정될 때까지 보류.** 그 전엔 [백로그 후보](./ui-improvement-backlog.md)가 발견 가능한 보관소(COMPOUND-032 취지). 승격은 안정된 base 위에서 INDEX(수기)+AUDIT-LOG(append)+`scripts/generate_views.py` 재생성으로.
- **fresh worktree에는 `node_modules`가 없다** → 그 안에서 tsc/eslint/vitest/next build 불가. 순수 함수는 `node`(zero-dep) 동작 검증만 가능. 툴체인 검증은 `node_modules`가 있는 메인 트리에서.

## 2. 검증 전략 (레이어별) — 이번 세션 실증

| 변경 유형 | 검증 가능 방법(무방해) | 한계/선결조건 |
|---|---|---|
| **순수 포맷/로직 함수**(format.ts 등) | ① node 동작 오라클(zero-dep) ② `npx tsc --noEmit`(format.ts 한정 grep) ③ `npx eslint <file>` — 전부 읽기전용, install 0 | 충분. PR #96이 이 패턴으로 검증됨 |
| **web 단위 테스트(영속/CI)** | (선결) **vitest 도입 필요** — Next 16 호환 config + 배치 결정 | ⚠️ node 내장 `node:test`는 `.ts` 확장자에서 **tsc(확장자 금지)↔node(확장자 필수)** 충돌 → 깨끗치 않음. **vitest가 정답이며 별도 TASK**(`npm i -D vitest` + config). dev 환경 비경합 시점에. |
| **UI 컴포넌트 변경(배선·차트·팔레트)** | tsc/eslint(타입/스타일) + **prod 모드 E2E(CI=1)·브라우저 스모크**(거동) | ⚠️ 거동 검증은 **dev/build 환경 실행**이 필요한데 동시 세션이 포트/공유빌드 점유 → **경합 해소 후**. |
| **신규 의존성**(uPlot·DiceBear·vitest 등) | 격리 worktree + 전체 `npm ci` | ⚠️ 메인 트리 `npm install`은 동시 dev를 깨뜨림 → **금지**. worktree 설치(분 단위·디스크)로 격리. |

## 3. 착수 순서 (충돌 위험 오름차순)

**지금 가능(무승인·무충돌·검증가능):**
1. **E7 잔여** — `fmtWonShort`는 PR #96에 착수됨. 추가 순수 포맷 헬퍼는 *소비처가 확정될 때만*(speculation 회피).

**선결 충족 후 가능:**
2. **E9/E10/E11 신규 모듈·에셋**(국기 피커·아바타·일러스트) — 신규 파일이라 충돌은 낮지만, 아바타(DiceBear)·E1(uPlot)은 **의존성 추가 → 격리 worktree 설치** 필요. 일러스트는 **외부 SVG 다운로드+라이선스 준수**(실사용분만 self-host) 필요.
3. **web 단위 테스트 인프라(vitest)** — 위 모든 web 변경의 거동 검증을 영속화하는 선결 인프라. dev 비경합 시점 별도 TASK.

**동시 세션 정리 후 가능(현재 경합):**
4. **E1~E6·E8 기존 컴포넌트 수정**(EquityChart/CandleChart/AllocationChart/HoldingsTable/SidebarNav/globals.css/design-tokens.ts) — 대상 파일 다수가 **현재 동시 편집 중**. 정리(커밋) 후 착수하고 prod E2E로 거동 검증.

## 4. 항목별 수용 기준 (요약)

- **E7(포맷)**: 모든 금액 셀이 `format.ts` 경유, `fmtWonShort` 만/억 단축 + `tabular-nums`; 라이브 갱신 시 자릿수 지터 0. 검증=단위테스트(vitest 후) + 시각.
- **E4~E6(컬러)**: `categoricalPalette`(Okabe-Ito) ≠ PnL 의미색 네임스페이스 분리; 히트맵 RdBu·트리맵 Viridis/Cividis; dark-mode Radix blue-9/10/11. 검증=대비(WCAG 3:1/4.5:1) + 색맹 시뮬.
- **E1~E3(그래프)**: uPlot 자산곡선·KLineChart 캔들·@mui/x-charts 스파크라인; 캔버스 차트엔 숨김 데이터테이블 a11y 병행.
- **E8~E11(아이콘·국기·캐릭터)**: MingCute ₩·candlestick, circle-flags/flag-icons FX, DiceBear(CC0 스타일 한정) 계정/에이전트 아바타, unDraw/Open Doodles 빈상태. 전부 자체호스팅(런타임 CDN 0)·귀속/상표 게이트 준수.

## 5. 공통 준수

- `web/AGENTS.md`(Next.js 16: `node_modules/next/dist/docs` 선독) · KR PnL 관습(상승=빨강/하락=파랑)+Western 토글 · 자체호스팅 · 라이선스 채택 전 재확인(특히 CC-BY 귀속·브랜드 상표) · 판매 전 금융규제 게이트와 함께 상표 검토.
- 거버넌스 쓰기는 **안정된 레지스트리 base** 위에서만. 공유 dirty 파일에 직접 append 후 커밋 금지(동시 세션 미커밋 작업 혼입).
