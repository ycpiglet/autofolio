---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-PRODUCT-MATURITY
work_uid: 3fbd54a0-f68b-4cea-bb60-55badaa83c7a
kind: taskset
parent_id: INIT-PRODUCT-MATURITY
status: active
owner: Lead Engineer
created_at: 2026-06-14T09:03:29+09:00
updated_at: 2026-06-14T09:03:29+09:00
origin_type: owner_request
origin_ref: AUDIT-2026-06-14-001
created_by: lead_engineer
title: 제품 성숙도 태스크셋 (TASK-053~067)
summary: 2026-06-14 감사에서 도출된 버그·dead-feature·안전 이슈 15건 — 병렬 실행 가능
tags: [bug, safety, quality, maturity, coverage, ops]
priority: P1
---

# TASKSET-PRODUCT-MATURITY — 제품 성숙도 버그 수정 15건

## 부모 이니셔티브

`INIT-PRODUCT-MATURITY`

## 포함 태스크

tasks:
  - TASK-053
  - TASK-054
  - TASK-055
  - TASK-056
  - TASK-057
  - TASK-058
  - TASK-059
  - TASK-060
  - TASK-061
  - TASK-062
  - TASK-063
  - TASK-064
  - TASK-065
  - TASK-066
  - TASK-067

| work_id | 설명 | 파일/대상 |
|---------|------|-----------|
| TASK-053 | 제품 성숙도 평가 지표 문서 등록 | docs/reports/PRODUCT-MATURITY-ASSESSMENT-2026-06-14.md |
| TASK-054 | fix: 알림 채널 토글/규칙 설정 미저장 | app/ui/views/alerts.py |
| TASK-055 | fix: 홈 화면 IC 제안 승인/거부 버튼 no-op | app/ui/views/home.py |
| TASK-056 | fix: backend.allocation_gap() 미구현 | app/ui/backend.py |
| TASK-057 | fix: 일손익률/누적손익률 KPI 0.0 하드코딩 | app/ui/backend.py |
| TASK-058 | fix: history.py 라이브 모드 조기 return | app/ui/views/history.py (또는 portfolio.py) |
| TASK-059 | fix: logout() 미완전 세션 상태 초기화 | app/ui/backend.py |
| TASK-060 | SQLite WAL 모드 + FK 제약 적용 | app/database/ |
| TASK-061 | feat: 가격 알림 엔진 평가 루프 | app/engine/ 또는 app/services/ |
| TASK-062 | feat: KRX 휴장일 캘린더 연동 | app/engine/ 또는 app/brokers/ |
| TASK-063 | fix: 서킷브레이커 일손실 기준 로직 오류 | app/engine/order_flow.py 또는 app/risk/ |
| TASK-064 | fix: 주문 조건 TOCTOU 레이스 (Critical) | app/engine/order_flow.py |
| TASK-065 | feat: 로그 로테이션 + 절대 경로 | logs/, app/ 설정 |
| TASK-066 | feat: 테스트 커버리지 60%+ (35개 케이스) | tests/ |
| TASK-067 | fix: _intraday_section try/except 누락 | app/ui/views/analysis.py |

## 의존 관계

대부분 독립적이며 병렬 실행 가능하다. TASK-064(TOCTOU Critical)는 가장 높은 우선순위로
선행 처리 권고.

## Wave 실행 계획

Wave 1 (Critical/High, 병렬): TASK-064, TASK-063, TASK-059, TASK-062
Wave 2 (High, 병렬): TASK-053, TASK-054, TASK-055, TASK-056, TASK-057, TASK-066
Wave 3 (Medium/Low, 병렬): TASK-058, TASK-060, TASK-061, TASK-065, TASK-067
