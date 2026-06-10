---
type: task
id: TASK-018
status: 대기
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Low
difficulty: 중
est_hours: 3
est_tokens: 50000
tags: [kis, orderbook, realtime]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
---

# TASK-018 KIS 호가창 10단계 조회 (inquire-asking-price-exp-ccn)

작업 ID: TASK-018
상태: 대기
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

매매 화면에서 호가창이 없으면 주문 진입 시 슬리피지 예측이 어렵다. `inquire-asking-price-exp-ccn` 엔드포인트로 매수/매도 10단계 호가와 잔량을 조회해 매매 결정 품질을 높인다.

## 구현 범위

- `KisClient.get_order_book(symbol)` 구현
- 매수 10단계·매도 10단계 호가(price) 및 잔량(qty) 파싱
- 매매 화면에 호가창 위젯 추가 (테이블 또는 시각화)
- 주문 전 슬리피지 추정 계산 헬퍼 추가 (예상 체결가 vs 현재가)
- TASK-010 WebSocket 구독(H0STASP0)과 연동 옵션

## 완료 기준

- [ ] `get_order_book()` 구현 및 단위 테스트
- [ ] 매매 화면 호가창 위젯 표시 확인
- [ ] 슬리피지 추정 헬퍼 단위 테스트
