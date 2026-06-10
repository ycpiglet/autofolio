---
type: task
id: TASK-020
status: 열림
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Low
difficulty: 중
est_hours: 3
est_tokens: 50000
tags: [kis, disclosure, compliance]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
---

# TASK-020 KIS 공시 정보 조회

작업 ID: TASK-020
상태: 열림
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

상장사 공시(유상증자, 분기보고서, 감사의견 등)는 매매 판단에 중요한 영향을 미친다. 공시 발생 시 Compliance Agent가 해당 종목의 주문을 일시 차단하거나 경고를 발송하면 리스크를 줄일 수 있다.

## 구현 범위

- KIS 공시 API 연동 (`inquire-disclosure` 또는 유사 엔드포인트)
- `KisClient.get_disclosures(symbol, days=1)` 구현
- 공시 유형 분류 (정기공시, 수시공시, 주요사항보고서)
- Compliance Agent 게이트: 중대 공시 발생 시 주문 차단 플래그 설정
- 알림 탭 또는 Telegram 공시 알림 발송

## 완료 기준

- [ ] `get_disclosures()` 구현 및 단위 테스트
- [ ] Compliance Agent 공시 차단 게이트 연동 확인
- [ ] 공시 발생 시 Notifier 발송 smoke 테스트
