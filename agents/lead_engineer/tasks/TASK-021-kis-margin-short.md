---
type: task
id: TASK-021
status: 보류
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Low
difficulty: 상
est_hours: 6
est_tokens: 50000
tags: [kis, margin, short]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
---

# TASK-021 KIS 신용·공매도 주문 (SLL_TYPE)

작업 ID: TASK-021
상태: 보류
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

레버리지 전략 또는 헤지 목적의 신용·공매도 주문을 지원하면 전략 다양성이 높아진다. 다만 고위험 영역이므로 리스크 게이트·안전 분류기와 강하게 결합해야 한다. `SLL_TYPE` 파라미터 확장이 핵심이다.

## 구현 범위

- `SLL_TYPE` 파라미터 확장: 02(임의매매), 05(대차매도)
- `place_order`에 신용/공매도 모드 파라미터 추가
- 리스크 게이트에서 신용/공매도 주문 전용 검증 레이어 추가
- 안전 분류기: L3 이상에서만 신용/공매도 허용
- paper 모드 전용 smoke 테스트 — 실전 계좌 하드가드 필수

주의: 이 태스크는 Owner 명시 승인 후 실전 계좌 적용. Paper 검증 완료 전까지 prod 실행 금지.

## 보류 기록

- 보류 시각: 2026-06-12T09:04:51+09:00
- 사유: 구현 범위가 `app/brokers/kis`의 `place_order` 주문 경로, `SLL_TYPE` 주문 파라미터, `app/risk/**` 안전 게이트, 신용/공매도 안전 분류기를 변경한다. 이는 `AGENTS.md` §16 Autofolio R3 surface에 해당한다.
- 결정: Owner 명시 승인 전에는 코드 변경하지 않고 보류한다.
- 재개 조건: Owner가 신용/공매도 주문 경로 변경을 명시 승인하고, paper-only 범위와 prod 하드가드 검증 계획을 확정한다.

## 완료 기준

- [ ] `SLL_TYPE` 02/05 주문 경로 구현 (paper 전용 초기)
- [ ] 리스크 게이트 신용/공매도 전용 검증 레이어 단위 테스트
- [ ] 안전 분류기 L3 조건 게이트 확인
- [ ] prod 하드가드 코드 리뷰 완료

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-R3-ORDER-SURFACE.md`
- Taskset: `agents/project/initiatives/TASKSET-R3-ORDER-SURFACE.md`
