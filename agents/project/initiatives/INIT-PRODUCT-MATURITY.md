---
schema_version: agent-runtime-work-item/v1
work_id: INIT-PRODUCT-MATURITY
work_uid: a43c69f6-0216-486c-b447-0177a3c47ee6
kind: initiative
status: active
owner: Lead Engineer
created_at: 2026-06-14T09:03:29+09:00
updated_at: 2026-06-14T09:03:29+09:00
origin_type: owner_request
origin_ref: AUDIT-2026-06-14-001
created_by: lead_engineer
title: Product Maturity — Bug Fixes and Quality Uplift
summary: 2026-06-14 성숙도 감사에서 도출된 버그·dead-feature·안전 이슈 15건을 수정하여 제품 성숙도를 UI 8+/10, 백엔드 7+/10으로 끌어올린다.
tags: [bug, safety, quality, maturity, coverage, ops]
priority: P1
---

# INIT-PRODUCT-MATURITY — 제품 성숙도 버그 수정 및 품질 향상 이니셔티브

## 목적

2026-06-14 제품 성숙도 감사(AUDIT-2026-06-14-001)에서 식별된 버그·dead-feature·안전 이슈
15건을 체계적으로 수정한다. 현재 UI 6.5/10, 백엔드 5.5/10, 테스트 커버리지 ~50%를
각각 8+/10, 7+/10, 60%+로 개선하는 것이 목표다.

## 포함 작업

| ID | 설명 | 우선순위 |
|----|------|----------|
| TASK-053 | 제품 성숙도 평가 지표 문서 등록 | High |
| TASK-054 | fix: 알림 채널 토글/규칙 설정 미저장 (alerts.py) | High |
| TASK-055 | fix: 홈 화면 IC 제안 승인/거부 버튼 no-op | High |
| TASK-056 | fix: backend.allocation_gap() 미구현 → mock fallback | High |
| TASK-057 | fix: 일손익률/누적손익률 KPI 0.0 하드코딩 | High |
| TASK-058 | fix: history.py 라이브 모드 조기 return으로 탭 미렌더 | Medium |
| TASK-059 | fix: logout() 미완전 세션 상태 초기화 (security) | High |
| TASK-060 | SQLite WAL 모드 + FK 제약 적용 | Medium |
| TASK-061 | feat: 가격 알림 엔진 평가 루프 구현 (dead feature 해소) | Medium |
| TASK-062 | feat: KRX 휴장일 캘린더 연동 (safety) | High |
| TASK-063 | fix: 서킷브레이커 일손실 기준 로직 오류 (안전 버그) | High |
| TASK-064 | fix: 주문 조건 TOCTOU 레이스 — 중복 주문 위험 (Critical) | Critical |
| TASK-065 | feat: 로그 로테이션 + 절대 경로 (ops) | Low |
| TASK-066 | feat: 테스트 커버리지 60%+ — 누락 35개 케이스 구현 | High |
| TASK-067 | fix: 분석 탭 _intraday_section try/except 누락 크래시 | Medium |

## 실행 파도

이 이니셔티브의 태스크들은 대부분 독립적이며 병렬 실행 가능하다. 상세 실행 계획은
TASKSET-PRODUCT-MATURITY를 참조한다.

## 완료 기준

- TASK-053 ~ TASK-067 모두 완료
- `python -m pytest tests/ -q` green (목표: 커버리지 60%+)
- `python scripts/check_agent_docs.py` 0 error
- `python scripts/work_schema_gate.py --items --check` findings=0
