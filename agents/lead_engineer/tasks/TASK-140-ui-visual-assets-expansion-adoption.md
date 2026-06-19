---
type: task
id: TASK-140
display_id: TASK-140
registered_at: 2026-06-19T22:04:43+09:00
created_at: 2026-06-19T22:04:43+09:00
updated_at: 2026-06-19T22:04:43+09:00
status: 대기
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
상태: 대기
Owner: UI/UX Designer
요청 시각: 2026-06-19T22:04:43+09:00
기록 시각: 2026-06-19T22:04:43+09:00
요청자: Owner
수행자: UI/UX Designer, Lead Engineer, QA
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

- [ ] 채택 항목이 자체호스팅(런타임 CDN 0)·라이선스 NOTICE 반영으로 적용된다.
- [ ] PnL 의미색과 categorical/sequential 팔레트가 네임스페이스 분리된다(WCAG/CVD 검증).
- [ ] 숫자 포맷이 `format.ts` 경유로 일원화되고 `verify:format`이 통과한다.
- [ ] 신규 의존성은 Owner 승인 기록이 있다.
- [ ] prod 모드 E2E(CI=1)와 `scripts/design_system_gate.py --check`가 회귀 없이 통과한다.

## 비고

- ⚠️ 번호: 등록 시점 동시 세션이 TASK 레지스트리(075~123, AUDIT 035+)를 미커밋 churn 중이라 충돌 회피로 버퍼 번호 TASK-140 사용. **레지스트리 커밋 후 번호 reconciliation 가능**.
- E1~E12 세부·파일 매핑·충돌 위험은 `docs/research/ui-improvement-backlog.md` 참조. 후속 granular TASK는 안정된 base에서 분기.
