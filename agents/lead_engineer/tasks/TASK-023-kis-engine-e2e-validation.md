---
type: task
id: TASK-023
status: 열림
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: High
difficulty: 중
est_hours: 2
est_tokens: 50000
tags: [kis, engine, e2e, validation]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
---

# TASK-023 UI 엔진 → KIS 실주문 E2E 검증 (체결 테스트)

작업 ID: TASK-023
상태: 열림
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

현재 KIS 연동은 단위 테스트와 paper 읽기 검증까지만 완료된 상태다. 실제 주문 생애주기 전체(UI 라이브 모드 → 엔진 1회 실행 → KIS paper 실주문 → SQLite 로그 기록 → UI 보유종목 표시)를 사람이 직접 확인하는 E2E 검증이 필요하다. 이 과정이 완료되어야 prod 전환 승인의 근거가 된다.

## 구현 범위

- 장 개시 후 `python scripts/kis_paper_order_smoke.py --market-test` 실행
- Autofolio UI를 라이브 모드로 실행 후 포트폴리오 잔고 확인
- 엔진 1회 수동 실행 (`python scripts/run_paper_engine.py --once`)
- KIS paper 계좌에서 주문 접수·체결 확인
- SQLite `orders` 테이블에 로그 기록 확인
- UI 포트폴리오 화면에서 보유종목 반영 확인
- 결과를 `agents/lead_engineer/AUDIT-LOG.md`에 기록

## 완료 기준

- [ ] paper 계좌에서 1주 주문 체결 확인 (KIS HTS 또는 앱 교차확인)
- [ ] SQLite 주문 로그에 체결 레코드 존재
- [ ] UI 포트폴리오 화면에서 보유종목 표시 확인 (스크린샷 또는 로그)
- [ ] AUDIT-LOG에 검증 결과 기록
- [ ] prod 전환 요건 충족 여부 판단 및 Owner 보고
