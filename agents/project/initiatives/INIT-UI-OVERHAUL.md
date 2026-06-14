---
schema_version: agent-runtime-work-item/v1
work_id: INIT-UI-OVERHAUL
work_uid: 4c081772-cea8-4261-8812-9149db643f72
kind: initiative
status: planned
owner: Lead Engineer
created_at: 2026-06-14T09:03:29+09:00
updated_at: 2026-06-14T09:03:29+09:00
origin_type: owner_request
origin_ref: AUDIT-2026-06-13-007
created_by: lead_engineer
title: UI 대개편 — Streamlit → Next.js + FastAPI 전환
summary: Streamlit 스트랭글러 패턴으로 Next.js + FastAPI 기반 UI를 5단계(Phase 1~5)로 전환. Phase 3는 Owner 승인 필수.
tags: [ui-overhaul, fastapi, next-js, migration, phase3-owner-gated]
priority: P1
---

# INIT-UI-OVERHAUL — UI 대개편 이니셔티브

## 목적

Streamlit 기반 UI를 Next.js + FastAPI 아키텍처로 단계적 전환한다. Streamlit 스트랭글러
패턴을 유지하며 5단계로 진행하고, Phase 3(매매·설정·안전 게이트)는 Owner 명시 승인 후에만
실행한다.

## 포함 작업

| ID | 설명 | 순서 | 비고 |
|----|------|------|------|
| TASK-045 | Phase 1 — FastAPI 기초 + 인증 + 읽기 API / Next.js 스캐폴드 + 로그인 | 1 | - |
| TASK-046 | Phase 2 — 홈 + 포트폴리오 (읽기 화면) | 2 | - |
| TASK-047 | Phase 3 — 매매 + 내역 + 설정 (state-changing + 안전 게이트) | 3 | ⚠ Owner 승인 필수 (보류) |
| TASK-048 | Phase 4 — 에이전트/IC + 알림 + SSE | 4 | - |
| TASK-049 | Phase 5 — 분석 화면 + 패리티 감사 + Streamlit 은퇴 | 5 | - |

## 순차 의존 관계

Phase 1 → Phase 2 → (Owner 승인) → Phase 3 → Phase 4 → Phase 5

Phase 3(TASK-047)는 Owner 승인 전까지 보류 상태를 유지한다. Phase 4/5는 Phase 3
완료 후 진행하되, Phase 3 보류 기간 중에는 Phase 2 완료 후 대기한다.

## 완료 기준

- Streamlit 화면이 Next.js로 완전 대체되고 Streamlit 프로세스가 은퇴됨
- Phase 3 안전 게이트 및 매매 기능 Owner 승인 + 검증 완료
- E2E 테스트(Playwright) green
- `python scripts/check_agent_docs.py` 0 error
