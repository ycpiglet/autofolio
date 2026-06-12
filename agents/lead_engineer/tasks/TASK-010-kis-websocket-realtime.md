---
type: task
id: TASK-010
status: 완료
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
updated_at: 2026-06-12T01:49:50+09:00
completed_at: 2026-06-12T01:49:50+09:00
---

# TASK-010 KIS WebSocket 실시간 (체결통보·현재가·호가)

작업 ID: TASK-010
상태: 완료
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

- [x] `kis_ws_client.py` 생성, 연결 및 구독 로직 구현
- [x] 단위 테스트(mock WebSocket) 추가 — 메시지 파싱·재접속 커버
- [x] Notifier 체결 통보 연동 확인 (paper 모드 mock smoke 테스트)
- [x] `docs/KIS_API_SPEC.md`에 WebSocket 섹션 추가

## 완료 기록

완료 시각: 2026-06-12T01:49:50+09:00

## 요구사항

요청자: Owner
현재 요청: backlog에 등록된 task들 순차적으로 작업 및 마무리

KIS WebSocket API를 이용해 국내주식 실시간 체결가, 호가, 체결통보 수신 경로를 추가하고 기존 REST 폴링 경로와 공존하게 한다.

## 완료 내용

- `app/brokers/kis/kis_ws_client.py`를 새로 추가했다.
  - `/oauth2/Approval` approval key 발급 (`secretkey` payload)
  - `/tryitout` WebSocket 연결 URL 구성
  - 구독 메시지 생성 (`approval_key`, `custtype=P`, `tr_type`, `tr_id`, `tr_key`)
  - 구독 목록 관리 및 최대 40개 제한
  - mock 주입 가능한 async 연결/재접속 루프
  - `PINGPONG` 응답 처리
  - AES-CBC 체결통보 복호화 헬퍼
- TR을 공식 샘플 기준으로 구현했다.
  - 현재가: `H0STCNT0`
  - 호가: `H0STASP0`
  - 체결통보 prod: `H0STCNI0`
  - 체결통보 paper: `H0STCNI9`
- 체결가/호가/체결통보 payload를 dataclass로 파싱한다.
- 체결통보 `CNTG_YN=2` 수신 시 Notifier/NotificationBus의 `send_fill()`을 호출한다.
- `KisWebSocketClient.get_price()`는 WebSocket 최신값을 우선 사용하고, 없으면 주입된 REST fallback client의 `get_current_price()`를 호출한다.
- `Settings`에 `kis_ws_url`, `kis_hts_id`와 환경별 기본 WebSocket URL을 추가했다.
- `websockets>=12.0` 런타임 의존성을 선언했다.
- `docs/KIS_API_SPEC.md`, `docs/references/kis/PROJECT-MAPPING.md`, `docs/BACKLOG.md`를 갱신했다.

## 결과

TASK-010 완료. Autofolio에 KIS WebSocket 실시간 수신 클라이언트, parser, Notifier 연동, REST fallback 공존 경로가 추가됐다.

## 검증

- `pytest tests\unit\test_kis_ws_client.py` — 11 passed

검증 범위:
- approval key 요청 URL/payload 검증
- 구독 메시지 검증
- `H0STCNT0` 현재가 파싱
- `H0STASP0` 호가 10단계 파싱
- `H0STCNI9` paper 체결통보 파싱 및 Notifier `send_fill()` 호출
- `PINGPONG` system message 파싱
- mock WebSocket 구독 전송 및 1회 재접속
- WebSocket 최신가 우선, REST fallback 후순위 가격 조회

## 남은 리스크

- 실제 KIS WebSocket 네트워크 접속은 실행하지 않았다. 실 접속은 KIS secret/HTS ID를 사용하므로 자동 세션에서 수행하지 않고, 운영 투입 전 paper 환경에서 별도 smoke가 필요하다.
- 체결통보 payload는 공식 컬럼 순서 기반 parser로 검증했으며, 실 계좌별 알림 필드 차이는 paper WebSocket smoke에서 재확인해야 한다.
