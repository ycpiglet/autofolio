---
type: task
id: TASK-012
status: 대기
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Medium
difficulty: 하
est_hours: 2
est_tokens: 50000
tags: [kis, history]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
---

# TASK-012 KIS 장기 거래내역 조회 (3개월+, CTSC9215R)

작업 ID: TASK-012
상태: 대기
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

현재 `inquire-daily-ccld`는 최근 3개월 이내 거래내역만 제공한다. 3개월 이전 내역은 TR `CTSC9215R`(실전) / `VTSC9215R`(paper)로 별도 조회해야 한다. 장기 손익 분석 및 세금 신고 지원을 위해 필요하다.

## 구현 범위

- `KisClient.get_order_history(start_date, end_date)` 구현
- 3개월 이내: 기존 `inquire-daily-ccld` 경로 사용
- 3개월 초과: TR `CTSC9215R` / `VTSC9215R` 자동 전환
- 응답 정규화 — 두 TR의 컬럼을 동일 스키마로 매핑
- 내역·손익 탭에서 날짜 범위 선택 시 연결

## 완료 기준

- [ ] `get_order_history()` 구현 및 TR 자동 전환 로직
- [ ] 단위 테스트 (3개월 경계 케이스 포함)
- [ ] 내역·손익 탭 날짜 범위 필터 연결 확인
