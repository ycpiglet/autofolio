---
type: task
id: TASK-021
status: 열림
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Low
difficulty: 상
est_hours: 6
est_tokens: 50000
tags: [kis, margin, short]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
---

# TASK-021 KIS 신용·공매도 주문 (SLL_TYPE)

작업 ID: TASK-021
상태: 열림
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

레버리지 전략 또는 헤지 목적의 신용·공매도 주문을 지원하면 전략 다양성이 높아진다. 다만 고위험 영역이므로 리스크 게이트·안전 분류기와 강하게 결합해야 한다. `SLL_TYPE` 파라미터 확장이 핵심이다.

## 구현 범위

- `SLL_TYPE` 파라미터 확장: 02(임의매매), 05(대차매도)
- `place_order`에 신용/공매도 모드 파라미터 추가
- 리스크 게이트에서 신용/공매도 주문 전용 검증 레이어 추가
- 안전 분류기: L3 이상에서만 신용/공매도 허용
- paper 모드 전용 smoke 테스트 — 실전 계좌 하드가드 필수

주의: 이 태스크는 Owner 명시 승인 후 실전 계좌 적용. Paper 검증 완료 전까지 prod 실행 금지.

## 완료 기준

- [ ] `SLL_TYPE` 02/05 주문 경로 구현 (paper 전용 초기)
- [ ] 리스크 게이트 신용/공매도 전용 검증 레이어 단위 테스트
- [ ] 안전 분류기 L3 조건 게이트 확인
- [ ] prod 하드가드 코드 리뷰 완료
