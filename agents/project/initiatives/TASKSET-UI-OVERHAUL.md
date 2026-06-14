---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-UI-OVERHAUL
work_uid: bd041642-f44d-4d22-91f9-878b855f68ba
kind: taskset
parent_id: INIT-UI-OVERHAUL
status: planned
owner: Lead Engineer
created_at: 2026-06-14T09:03:29+09:00
updated_at: 2026-06-14T09:03:29+09:00
origin_type: owner_request
origin_ref: AUDIT-2026-06-13-007
created_by: lead_engineer
title: UI 대개편 태스크셋 (TASK-045~049)
summary: Next.js + FastAPI 전환 5단계 — 순차 실행; TASK-047(Phase 3)는 Owner 승인 필수
tags: [ui-overhaul, fastapi, next-js, migration, sequential, phase3-owner-gated]
priority: P1
---

# TASKSET-UI-OVERHAUL — UI 대개편 5단계

## 부모 이니셔티브

`INIT-UI-OVERHAUL`

## 포함 태스크

tasks:
  - TASK-045
  - TASK-046
  - TASK-047
  - TASK-048
  - TASK-049

| work_id | 설명 | 상태 | 비고 |
|---------|------|------|------|
| TASK-045 | Phase 1 — FastAPI 기초 + 인증 + 읽기 API / Next.js 스캐폴드 + 로그인 | 대기 | - |
| TASK-046 | Phase 2 — 홈 + 포트폴리오 (읽기 화면) | 대기 | - |
| TASK-047 | Phase 3 — 매매 + 내역 + 설정 (state-changing + 안전 게이트) | 보류 | ⚠ Owner 승인 필수 |
| TASK-048 | Phase 4 — 에이전트/IC + 알림 + SSE | 대기 | - |
| TASK-049 | Phase 5 — 분석 화면 + 패리티 감사 + Streamlit 은퇴 | 대기 | - |

## 순차 의존 관계

TASK-045 → TASK-046 → (Owner 승인) → TASK-047 → TASK-048 → TASK-049

TASK-047(Phase 3)은 Owner가 진행을 명시 승인하기 전까지 보류 상태를 유지하며
코드 변경을 하지 않는다.

## Wave 실행 계획

Wave 1: TASK-045 (Phase 1 완료 후)
Wave 2: TASK-046 (Phase 2 완료 후)
Wave 3: TASK-047 (Owner 승인 획득 후)
Wave 4: TASK-048 (Phase 3 완료 후)
Wave 5: TASK-049 (Phase 4 완료 후)
