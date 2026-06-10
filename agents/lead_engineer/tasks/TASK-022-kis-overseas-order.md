---
type: task
id: TASK-022
status: 대기
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Low
difficulty: 상
est_hours: 8
est_tokens: 50000
tags: [kis, overseas, us-stocks]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
---

# TASK-022 KIS 해외주식 주문 (미국·홍콩 등)

작업 ID: TASK-022
상태: 대기
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

US 에셋(S&P500 구성종목 등)을 화이트리스트에 포함하려면 해외주식 전용 TR셋이 필요하다. KIS는 해외주식 전용 API (`/uapi/overseas-stock/v1/trading/order`, TR `TTTT1002U`)를 별도로 제공한다. 환율 처리가 포함되어 국내주식 대비 복잡도가 높다.

## 구현 범위

- `KisClient.place_overseas_order(symbol, market, side, qty, price)` 구현
- market 파라미터: 'NASD'(나스닥), 'NYSE', 'AMEX', 'SEHK'(홍콩) 등
- TR: `TTTT1002U`(실전 매수), `TTTT1006U`(실전 매도), `VTTT1002U`(paper)
- 환율 처리: KRW→USD 환산, 주문 통화 파라미터 처리
- US 에셋 화이트리스트 지원 (`app/config.py` 확장)
- 해외주식 잔고 조회 및 포트폴리오 통합 (KRW 환산 표시)

## 완료 기준

- [ ] `place_overseas_order()` 구현 및 단위 테스트
- [ ] 환율 처리 로직 검증 (USD/KRW 변환)
- [ ] paper 모드 해외주식 smoke 테스트
- [ ] 포트폴리오 화면 해외주식 잔고 KRW 환산 표시
