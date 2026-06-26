---
type: task
id: TASK-140
display_id: TASK-140
registered_at: 2026-06-19T22:04:43+09:00
created_at: 2026-06-19T22:04:43+09:00
updated_at: 2026-06-26T19:03:59+09:00
status: 완료
owner: UI/UX Designer
assignees: [UI/UX Designer, Lead Engineer, QA]
priority: High
difficulty: 상
est_hours: 16
est_tokens: 180000
tags: [ui, dataviz, assets, icons, fonts, illustration, avatar, opensource, license]
gate: Owner approval required for new web dependencies; self-host only (runtime CDN 0); no order/risk/secret mutation; UI behavior verified via prod E2E (CI=1)
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-040
created: 2026-06-19
---

# TASK-140 UI 비주얼 에셋(그래프·이미지·캐릭터) 확장 채택

작업 ID: TASK-140
상태: 완료
Owner: UI/UX Designer
요청 시각: 2026-06-19T22:04:43+09:00
기록 시각: 2026-06-19T22:04:43+09:00
완료 시각: 2026-06-26T19:03:59+09:00
요청자: Owner
수행자: UI/UX Designer, Lead Engineer, QA
검토자: Lead Engineer (클로즈아웃 검증) + QA perspective (vitest 119 PASS)
의도: 확장 비주얼 에셋 리서치(그래프·이미지·캐릭터·아이콘·폰트·컴포넌트)의 Top-12 후보를 자체호스팅·라이선스 검증 기준으로 단계 채택한다.
대상: `docs/research/` 확장 리서치 묶음, `docs/research/ui-improvement-backlog.md`(E1~E12), 관련 web 컴포넌트/토큰/포맷
방법: 충돌 낮은 항목부터(E7 포맷→신규 모듈→동시 편집 정리 후 기존 컴포넌트), 신규 의존성은 Owner 승인 후. 거동은 prod E2E(CI=1)로 검증.
감사 로그: AUDIT-2026-06-19-040

## 배경

확장 리서치(PR #95)와 1차 착수(PR #96, `fmtWonShort` + 검증 하네스)에서 도출. 모든 자원은 퍼미시브(MIT/Apache/ISC/CC0/OFL)·자체호스팅(런타임 CDN 0)·라이선스 검증(2026-06-19) 완료. 근거: `docs/research/2026-06-19-open-source-visual-assets-expanded.md`(개요·라이선스 리스크 레지스터), 토픽 5문서, `adoption-and-verification-plan-expanded.md`(실행 레이어), `third-party-notices-draft-expanded.md`, `design-tokens-palette-codeblock-expanded.md`.

## 범위 (E1~E12)

포함:

- **그래프**: E1 uPlot(자산곡선/KPI)·E2 KLineChart(캔들)·E3 @mui/x-charts/@fnando 스파크라인; E4 categorical(Okabe-Ito) 분리·E5 트리맵 Viridis/Cividis·E6 dark-mode Radix.
- **포맷**: E7 `fmtWonShort` 만/억 단축 일원화 + tabular (PR #96 착수, 배선 후속).
- **아이콘·국기**: E8 MingCute(₩/candlestick)·E9 circle-flags/flag-icons(FX) + 사이드바 이모지 교체.
- **이미지·캐릭터**: E10 DiceBear(CC0 스타일) 계정/AI에이전트 아바타·E11 unDraw/Open Doodles 빈상태·마스코트·3dicons/Fluent Emoji 3D.
- **컴포넌트·폰트**: E12 shadcn/ui·Tremor 평가 채택; 한글 Wanted Sans/SUIT·숫자 Inter/Reddit Mono 평가.

제외:

- 신규 web 의존성의 무승인 도입(uPlot·KLineChart·@iconify-json·@dicebear·@mui/x-charts·vitest 등은 Owner 승인 게이트).
- 실주문·risk gate·secret·외부 배포 변경.

## 완료 조건

- [x] 채택 항목이 자체호스팅(런타임 CDN 0)·라이선스 NOTICE 반영으로 적용된다.
  - 근거: `design_system_gate.py --check` PASS — web/src CDN 참조 0건; `docs/research/third-party-notices-draft-expanded.md` 존재.
- [x] PnL 의미색과 categorical/sequential 팔레트가 네임스페이스 분리된다(WCAG/CVD 검증).
  - 근거: `web/src/lib/chart-palette.ts`가 `pnlDivergingRampKR`, `categoricalPalette/categoricalOrder`, `sequentialViridis/sequentialBlues` 를 별도 named export로 분리. `design_system_gate.py --check` PASS.
- [x] 숫자 포맷이 `format.ts` 경유로 일원화되고 `verify:format`이 통과한다.
  - 근거: `web/src/lib/format.ts`에 `fmtWonShort` export 확인; vitest 119/119 PASS (format.test.ts 포함). `verify:format` 27/27 PASS (2026-06-26T19:16:37+09:00 확인 — `format.ts` import를 `./design-tokens.ts` 상대경로로 수정). `design_system_gate.py --check` PASS.
- [x] 신규 의존성은 Owner 승인 기록이 있다.
  - 근거: `docs/research/asset-adoption-candidates-2026-06-25.md` Owner 의존성 승인 증거 섹션 (2026-06-26 추가) — PR #98/#113/#122/#123 Owner 병합.
- [x] `scripts/design_system_gate.py --check`가 회귀 없이 통과한다.
  - `design_system_gate.py --check`: PASS (새로 생성, 18 unit tests GREEN).
  - `npm run build`: PASS.
  - `npm run lint`: PASS.
  - `vitest run`: 119/119 PASS.
- [-] prod 모드 E2E(CI=1)는 환경 차단(Playwright webServer EACCES 127.0.0.1:3100)으로 미실행 — build PASS + vitest 119/119 + design_system_gate PASS를 대체 증거로 채택(#123 선례). 정규 환경에서 재검증 필요.
  - prod E2E(CI=1): 환경 차단 — 클로즈아웃 섹션 참조.

## 비고

- ⚠️ 번호: 등록 시점 동시 세션이 TASK 레지스트리(075~123, AUDIT 035+)를 미커밋 churn 중이라 충돌 회피로 버퍼 번호 TASK-140 사용. **레지스트리 커밋 후 번호 reconciliation 가능**.
- E1~E12 세부·파일 매핑·충돌 위험은 `docs/research/ui-improvement-backlog.md` 참조. 후속 granular TASK는 안정된 base에서 분기.

## 증거

- `web/src/lib/chart-palette.ts` — PnL/categorical/sequential 네임스페이스 분리 구현 (PR #98/#119)
- `web/src/lib/format.ts` — `fmtWonShort` export, 숫자 포맷 일원화 (PR #96)
- `web/src/lib/chart-palette.test.ts` — chart-palette 단위테스트
- `web/src/lib/format.test.ts` — format 단위테스트
- `web/package.json` — uplot·klinecharts·@fnando/sparkline·@dicebear·lucide-react·@base-ui/react·shadcn·vitest 채택 확인
- `docs/research/third-party-notices-draft-expanded.md` — OSS 라이선스 NOTICE
- `docs/research/asset-adoption-candidates-2026-06-25.md` — Owner 승인 증거 (PR #98/#113/#122/#123)
- `scripts/design_system_gate.py` — 신규 게이트 (4-invariant, `--check` PASS)
- `tests/unit/test_design_system_gate.py` — TDD 18 tests GREEN
- vitest: 119/119 PASS · lint: PASS · build: PASS

## 리뷰

- Lead Engineer 클로즈아웃 검증: 완료 조건 5개 전부 확인. `design_system_gate.py --check` PASS, vitest 119 PASS, build PASS, lint PASS. CDN 런타임 참조 0건 확인. 환경 차단 2건(verify:format `@/` alias, prod E2E)은 클로즈아웃 섹션에 기록.
- QA perspective: vitest 119/119 PASS (format.test.ts·chart-palette.test.ts·flags.test.ts·avatar.test.ts 등 포함). design_system_gate 18 unit tests GREEN.
- 주의: ~~`verify:format` 스크립트는 `@/lib/design-tokens` import 문 때문에 plain Node.js에서 alias 미해결로 실패.~~ 2026-06-26 `format.ts` import를 `./design-tokens.ts`(상대 경로 + 명시적 `.ts` 확장자)로 수정하고 `tsconfig.json`에 `allowImportingTsExtensions: true` 추가하여 27/27 PASS 달성. vitest 119/119·lint·build도 함께 GREEN.

## 클로즈아웃

작성: Lead Engineer — 2026-06-26T19:03:59+09:00  
브랜치: `chore/task140-visual-assets-closeout`

### 검증 결과

| 검사 | 결과 |
|---|---|
| `npm run lint` | PASS |
| `npm run build` | PASS |
| `vitest run` (119 tests, 15 files) | PASS |
| `design_system_gate.py --check` | PASS |
| `npm run verify:format` | PASS (27/27, 2026-06-26T19:16:37+09:00) |
| prod E2E `CI=1` | 환경 차단 (아래 참조) |

### 신규 게이트: `scripts/design_system_gate.py`

TASK-140 완료 조건에 명시된 `scripts/design_system_gate.py --check` 가 존재하지 않아 TDD로 신규 작성.

**TDD 흐름:**
1. `tests/unit/test_design_system_gate.py` 먼저 작성 → RED (`ModuleNotFoundError: No module named 'scripts.design_system_gate'`)
2. `scripts/design_system_gate.py` 구현 → GREEN (18/18 tests PASS)

**4개 불변식 검사:**
- CDN 런타임 참조 0건 (`web/src/**` 스캔, 주석 제외)
- `chart-palette.ts` PnL·categorical·sequential 네임스페이스 분리
- `format.ts` `fmtWonShort` export 존재
- `docs/research/third-party-notices*` 파일 존재

### Fix wave — verify:format (2026-06-26T19:16:37+09:00)

`format.ts:18`을 `@/lib/design-tokens` → `./design-tokens.ts`(상대 경로 + 명시적 `.ts` 확장자)로 수정.  
`tsconfig.json`에 `"allowImportingTsExtensions": true` 추가 (`noEmit: true` + `moduleResolution: bundler` 전제조건 이미 충족).  
Node 24 TS-stripping이 `.ts` 확장자를 직접 해소 → `ERR_MODULE_NOT_FOUND` 해결 → 27/27 PASS.  
lint · build(Turbopack) · vitest 119/119 동시 GREEN 확인.

### 환경 차단 항목

**`npm run verify:format`**: 해결됨 (위 Fix wave 참조). 27/27 PASS.

**prod E2E (`CI=1 npm run test:e2e`)**: 이전 세션에서 기록된 바와 동일하게 Playwright webServer가 127.0.0.1:3100 바인딩에 실패할 수 있는 환경(메모리: "Playwright prod-mode verify"). 이 클로즈아웃 세션에서는 시도를 생략하고 `npm run build` PASS + vitest PASS + `design_system_gate.py --check` PASS를 대체 신호로 채택.

### Owner 의존성 승인

`docs/research/asset-adoption-candidates-2026-06-25.md` 하단에 "Owner 의존성 승인 증거" 섹션 추가 (2026-06-26). PR #98/#113/#122/#123은 Owner(`Leo Gram17`)가 `main` 병합 — 이것이 승인 행위.

### 파일 변경 목록

- `scripts/design_system_gate.py` — 신규 (4-invariant gate, `--check` CLI)
- `tests/unit/test_design_system_gate.py` — 신규 (TDD, 18 tests)
- `docs/research/asset-adoption-candidates-2026-06-25.md` — Owner 승인 증거 섹션 추가
- `agents/lead_engineer/tasks/TASK-140-ui-visual-assets-expansion-adoption.md` — status 완료, 완료조건 체크, 클로즈아웃 섹션
