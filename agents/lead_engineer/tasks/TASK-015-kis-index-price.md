---
type: task
id: TASK-015
status: 열림
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Low
difficulty: 하
est_hours: 1
est_tokens: 50000
tags: [kis, index]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
---

# TASK-015 KIS 지수 조회 (KOSPI·KOSDAQ·KRX)

작업 ID: TASK-015
상태: 열림
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

홈 대시보드에 KOSPI·KOSDAQ·KRX 지수를 표시하면 시장 컨텍스트를 즉시 파악할 수 있다. `inquire-index-price` 엔드포인트로 구현 가능하며 난이도가 낮다.

## 구현 범위

- `KisClient.get_index_price(index_code: str)` 추가
- index_code: '0001'(KOSPI), '1001'(KOSDAQ), '2001'(KRX300) 등
- 홈 대시보드 상단 지수 표시 위젯 연결
- 지수 코드 상수를 `app/brokers/kis/constants.py`에 정의

## 완료 기준

- [ ] `get_index_price()` 구현 및 단위 테스트
- [ ] 홈 화면 지수 표시 위젯 확인 (mock 응답 기반)
