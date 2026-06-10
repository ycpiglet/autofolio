---
type: task
id: TASK-017
status: 대기
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Low
difficulty: 하
est_hours: 2
est_tokens: 50000
tags: [kis, dividend]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
---

# TASK-017 KIS 배당 정보 조회

작업 ID: TASK-017
상태: 대기
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

포트폴리오 수익 분석에서 배당 수익률은 중요한 요소이지만 현재 화면에 표시되지 않는다. KIS `inquire-dividend` 엔드포인트 또는 `inquire-daily-itemchartprice` 배당 필드를 파싱해 포트폴리오 화면에 배당 수익률을 표시한다.

## 구현 범위

- `KisClient.get_dividend_info(symbol)` 구현
- `inquire-dividend` 또는 일봉 데이터의 배당 필드 활용
- 배당 이력(지급일, 주당 배당금, 배당 수익률) 파싱
- 포트폴리오 화면 종목별 배당 수익률 컬럼 추가
- 총 포트폴리오 예상 연배당 수익률 계산 표시

## 완료 기준

- [ ] `get_dividend_info()` 구현 및 단위 테스트
- [ ] 포트폴리오 화면 배당 수익률 컬럼 표시 확인
