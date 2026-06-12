---
type: task
id: TASK-041
status: 대기
owner: UI/UX Designer
assignees: [UI/UX Designer, Backend Engineer, QA]
priority: Medium
difficulty: 상
est_hours: 16
est_tokens: 120000
tags: [ui-overhaul, analysis, parity, streamlit-retire, phase5]
gate: 선행 TASK-040 완료 전 착수 불가; 착수 전 선행 완료 확인 review 필요
trigger_meeting: TASK-040 완료 후 자동 개시
audit_log: AUDIT-2026-06-13-001
created: 2026-06-13
created_at: 2026-06-13T01:33:29+09:00
updated_at: 2026-06-13T01:33:29+09:00
---

# TASK-041 UI 대개편 Phase 5 — 분석 화면 + 패리티 감사 + Streamlit 은퇴

작업 ID: TASK-041
상태: 대기
Owner: UI/UX Designer
기록 시각: 2026-06-13T01:33:29+09:00

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
