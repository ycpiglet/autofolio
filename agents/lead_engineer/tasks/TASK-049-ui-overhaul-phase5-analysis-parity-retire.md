---
type: task
id: TASK-049
status: 보류
owner: UI/UX Designer
assignees: [UI/UX Designer, Backend Engineer, QA]
priority: Medium
difficulty: 상
est_hours: 16
est_tokens: 120000
tags: [ui-overhaul, analysis, parity, streamlit-retire, phase5]
gate: 선행 TASK-048 완료 전 착수 불가; 착수 전 선행 완료 확인 review 필요
trigger_meeting: TASK-048 완료 후 자동 개시
audit_log: AUDIT-2026-06-13-007
created: 2026-06-13
created_at: 2026-06-13T01:33:29+09:00
updated_at: 2026-06-13T01:33:29+09:00
---

# TASK-049 UI 대개편 Phase 5 — 분석 화면 + 패리티 감사 + Streamlit 은퇴

작업 ID: TASK-049
상태: 보류
Owner: UI/UX Designer
요청 시각: 2026-06-13
기록 시각: 2026-06-13T01:33:29+09:00
요청자: Owner
수행자: Lead Engineer
의도: UI 대개편 Phase 5 — 분석 화면 완성, Streamlit 8화면 패리티 감사 통과 후 Streamlit 은퇴
대상: app/ui/views/, docs/superpowers/specs/2026-06-13-ui-overhaul-design.md §Phase 5, docker-compose Streamlit 서비스 (Phase 5 범위)
방법: CandleChart·Sankey·백테스트 폼 구현, 패리티 체크리스트 작성 및 통과, AppTest·Streamlit shim 제거
감사 로그: AUDIT-2026-06-13-007

## 배경 및 목적

UI 대개편 최종 Phase. 분석 화면을 완성하고, Streamlit 8화면과 패리티 체크리스트를 통과한 후 Streamlit을 은퇴시킨다. 이 Phase에서 Phase 0의 역방향 파사드(shim)를 해소하고 진짜 구현 이동을 완료한다.

## 작업 범위

### 분석 화면

- `CandleChart` — lightweight-charts 캔들차트
- Sankey 차트 — Recharts 기반 포트폴리오 구성비
- 백테스트 폼 + 결과 뷰
- VaR 시나리오 분석 폼

### 패리티 감사

- 8화면 Streamlit 대비 기능 패리티 체크리스트 작성 및 통과
  - 홈(대시보드), 포트폴리오, 매매/주문, 내역·손익, 분석, 에이전트, 알림, 설정·연동

### Streamlit 은퇴

- `app/ui/views/` 아카이브
- AppTest 스위트 제거
- docker-compose에서 streamlit 서비스 정리
- `app/services/*` 진짜 구현 이동 (Phase 0 역방향 파사드 해소, `app/ui/backend.py` shim 제거)

## 완료 기준

- 8화면 패리티 체크리스트 100% 통과
- `npm run build && npm run lint` 오류 없음
- Playwright `demo-walkthrough.spec.ts` (게스트 8페이지 순회) green
- `python -m pytest tests/ -q` green (AppTest 제거 후)
- Streamlit 서비스 docker-compose 제거
- CI coverage ≥50% 유지

## 근거 경로

- 디자인 스펙(레포 내 권위 문서): `docs/superpowers/specs/2026-06-13-ui-overhaul-design.md` §Phase 5 (원 플랜은 세션 로컬)
- Phase 0 역방향 파사드 설명: `docs/superpowers/specs/2026-06-13-ui-overhaul-design.md` §5 Phase 0 실행 결과

## Done When

- 패리티 체크리스트 100%
- Streamlit 서비스 제거 완료
- CI green

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-UI-OVERHAUL.md`
- Taskset: `agents/project/initiatives/TASKSET-UI-OVERHAUL.md`
- Unit spec(빌드아웃): `agents/lead_engineer/tasks/units/TASK-049/UNIT-TASK-049-001.md`
- 패리티 감사: `docs/reports/UI-PARITY-AUDIT-2026-06-15.md`

## 진행 현황 (2026-06-15T18:27:03+09:00) — 빌드아웃 완료 / 은퇴 보류

**완료(빌드아웃):**
- 분석 읽기 엔드포인트 4종(backtest/VaR/scenario/whatif, PR #82) + 분석 화면 5섹션(CandleChart·백테스트·VaR·시나리오·Sankey) 구현. 전체 Playwright 29 passed ×2(프로덕션), pytest 1067, check_agent_docs 0 error.
- 8화면 패리티 감사 작성 — **8/8 화면 빌드아웃 완료**, 안전 불변식 패리티 확보.

**보류(은퇴 — Owner 게이트):**
- `app/ui/views` 아카이브 + AppTest 32개 제거 + `backend.py`→`app/services` 역파사드 해소(테스트 26개 재배선) + docker-compose streamlit 제거는 **미실행**.
- 사유: (1) Next.js 앱의 **실 KIS paper 수동 검증(Phase 3 Done-When) 미완** — 검증 전 안전망 UI 제거는 비가역적·임프루던트. (2) 파괴적 규모(커버리지·회귀 위험). (3) Owner 명시 은퇴 승인 필요.
- 진행 조건/절차는 패리티 감사 문서 §"Streamlit 은퇴" 참조. 조건 충족 시 별도 태스크로 분리 실행.

**상태 사유**: 빌드아웃·감사는 완료됐으나 Done-When(패리티 100% + Streamlit 은퇴 + docker-compose 정리)의 은퇴 항목이 Owner 게이트로 남아 **보류**.

