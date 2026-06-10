---
type: task
id: TASK-014
status: 대기
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Medium
difficulty: 중
est_hours: 3
est_tokens: 50000
tags: [kis, order, after-hours]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
---

# TASK-014 KIS 시간외 주문 (장전·장후 단일가)

작업 ID: TASK-014
상태: 대기
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

현재 `place_order`는 정규장 주문(ORD_DVSN 00/01)만 지원한다. 장전(08:30~09:00) 단일가(05)와 장후(15:40~16:00) 단일가(06) 주문을 지원하면 전략의 유연성이 높아진다. 거래시간 가드를 함께 조정해야 안전하다.

## 구현 범위

- ORD_DVSN 코드 확장: 05(장전 단일가), 06(장후 단일가)
- `place_order`에 `after_hours: bool` 파라미터 또는 `OrderType` enum 확장
- 거래시간 가드 로직 조정 — 시간외 창 (08:30~09:00, 15:40~16:00) 허용
- 리스크 게이트에서 시간외 주문 플래그 인식
- paper 모드에서 시간외 주문 smoke 테스트 시나리오 추가

## 완료 기준

- [ ] ORD_DVSN 05/06 주문 경로 구현
- [ ] 거래시간 가드 시간외 창 허용 확인 (단위 테스트)
- [ ] 리스크 게이트 연동 테스트
- [ ] `examples/kis/` 에 시간외 주문 payload 예제 추가
