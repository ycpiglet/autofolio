---
type: task
id: TASK-010
status: 대기
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: High
difficulty: 상
est_hours: 8
est_tokens: 50000
tags: [kis, websocket, realtime]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
---

# TASK-010 KIS WebSocket 실시간 (체결통보·현재가·호가)

작업 ID: TASK-010
상태: 대기
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

현재 KisClient는 REST 폴링 방식으로 현재가를 조회한다. 폴링은 레이트리밋 소모가 크고 체결 즉시 반응이 불가능하다. KIS WebSocket API를 이용하면 구독 종목의 현재가·호가·체결통보를 서버 푸시로 수신할 수 있어 실시간성이 크게 향상된다.

## 구현 범위

- `app/brokers/kis/kis_ws_client.py` 신규 생성 — KIS WebSocket 연결·재접속·구독 관리
- TR 코드: H0STCNT0(현재가), H0STASP0(호가), H0STCNI0(체결통보)
- 연결 시 approval key 발급 → 종목 구독 → 수신 콜백 처리
- 체결통보 수신 시 Notifier를 통해 즉시 발송
- 기존 `KisClient` 폴링 경로와 공존 (WebSocket 우선, fallback REST)

## 완료 기준

- [ ] `kis_ws_client.py` 생성, 연결 및 구독 로직 구현
- [ ] 단위 테스트(mock WebSocket) 추가 — 메시지 파싱·재접속 커버
- [ ] Notifier 체결 통보 연동 확인 (paper 모드 smoke 테스트)
- [ ] `docs/KIS_API_SPEC.md`에 WebSocket 섹션 추가
