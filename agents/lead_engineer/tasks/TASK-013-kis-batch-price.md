---
type: task
id: TASK-013
status: 대기
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Medium
difficulty: 하
est_hours: 2
est_tokens: 50000
tags: [kis, price, performance]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
---

# TASK-013 KIS 복수 종목 현재가 배치 조회 (inquire-price-2)

작업 ID: TASK-013
상태: 대기
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

화이트리스트 종목이 여러 개일 때 현재가를 개별 REST 호출로 조회하면 레이트리밋을 빠르게 소모하고 응답 지연이 누적된다. `inquire-price-2` 배치 API를 활용하면 한 번의 호출로 복수 종목 가격을 수신할 수 있어 성능과 안정성이 향상된다.

## 구현 범위

- `KisClient.get_prices_batch(symbols: list[str])` 구현
- 최대 배치 크기(KIS 제한) 초과 시 자동 청크 분할
- 기존 단일 종목 `get_current_price()` 호출을 배치 경로로 대체 (option)
- 엔진 및 포트폴리오 화면 가격 갱신 경로에 연결

## 완료 기준

- [ ] `get_prices_batch()` 구현 및 단위 테스트
- [ ] 청크 분할 경계 테스트 (1종목, 배치 한도 정확히, 한도+1)
- [ ] 기존 단일 호출 대비 레이트리밋 소모 절감 확인 (로그 기반)
