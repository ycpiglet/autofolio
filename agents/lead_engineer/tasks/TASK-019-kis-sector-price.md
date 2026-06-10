---
type: task
id: TASK-019
status: 대기
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Low
difficulty: 하
est_hours: 2
est_tokens: 50000
tags: [kis, sector]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
---

# TASK-019 KIS 업종별 시세 조회

작업 ID: TASK-019
상태: 대기
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

분석 탭에서 업종 히트맵 또는 업종별 퍼포먼스를 보여주면 포트폴리오 섹터 노출을 시장 업종 흐름과 비교할 수 있다. `inquire-upjong-price` 엔드포인트로 업종별 시세를 수신한다.

## 구현 범위

- `KisClient.get_sector_price(sector_code: str)` 구현
- 주요 업종 코드 상수 정의 (반도체, 자동차, 금융 등)
- 업종별 등락률·거래대금 파싱
- 분석 탭에 업종 퍼포먼스 테이블 또는 히트맵 추가

## 완료 기준

- [ ] `get_sector_price()` 구현 및 단위 테스트
- [ ] 분석 탭 업종 퍼포먼스 표시 확인 (mock 응답 기반)
