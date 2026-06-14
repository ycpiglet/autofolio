---
schema_version: agent-runtime-work-item/v1
work_id: INIT-R3-ORDER-SURFACE
work_uid: 408edb74-25a3-4c09-a709-602e3fe95a69
kind: initiative
status: blocked
owner: Lead Engineer
created_at: 2026-06-14T09:03:29+09:00
updated_at: 2026-06-14T09:03:29+09:00
origin_type: owner_request
origin_ref: AGENTS.md-section-16
created_by: lead_engineer
title: R3 Order Surface — Owner-Gated Order, Risk, and Broker Expansion
summary: AGENTS.md §16 R3 surface에 해당하는 주문 경로·리스크 게이트·브로커 확장 9건. Owner 명시 승인 없이는 코드 변경 금지.
tags: [r3, order, risk, broker, owner-gated, blocked]
priority: P3
---

# INIT-R3-ORDER-SURFACE — R3 주문 서피스 이니셔티브

## ⚠ Owner 승인 필수 — 코드 변경 금지

이 이니셔티브의 모든 태스크는 `AGENTS.md §16` R3 surface에 해당한다.

R3 surface 기준:
- `app/brokers/kis/` 실주문 경로 (`place_order`, `SLL_TYPE`, `ORD_DVSN`) 변경
- `app/risk/**` 안전 게이트 정책 변경
- 시간외 주문 정책, 신용/공매도 안전 분류기 변경
- 해외주식 주문 경로 신설

**Owner가 해당 태스크 번호를 명시하여 진행을 승인하기 전까지 코드 변경을 하지 않는다.**

## 목적

KIS 브로커 주문 기능 확장(시간외·신용·해외주식), 리스크 게이트 강화, 대체상품/파생상품/
고급 주문 유형 지원, 블록/바스켓 실행, 법인 기업 행위 데이터 품질 확보를 포함한다.

## 포함 작업

| ID | 설명 | 보류 사유 |
|----|------|-----------|
| TASK-014 | KIS 시간외 주문 (장전·장후 단일가) | R3: place_order + 거래시간 정책 변경 |
| TASK-021 | KIS 신용·공매도 주문 (SLL_TYPE) | R3: place_order + 안전 분류기 변경 |
| TASK-022 | KIS 해외주식 주문 (미국·홍콩 등) | R3: 해외 주문 경로 신설 |
| TASK-026 | KRX 대체상품 테스트 지원 (채권·REIT·ELW·ETN) | R3: 브로커 order path 닿을 수 있음 |
| TASK-027 | KRX 파생상품 테스트 지원 | R3: 브로커 order path 닿을 수 있음 |
| TASK-028 | 고급 주문 유형 테스트 지원 | R3: order path 확장 |
| TASK-030 | 블록/바스켓 실행 테스트 | R3: 고위험 주문 실행 경로 |
| TASK-031 | 시장 정지/VI 리스크 게이트 | R3: 안전 게이트 정책 변경 |
| TASK-032 | 데이터 품질 및 기업 행위 테스트 | R3: 브로커 데이터 경로 닿을 수 있음 |

## 재개 조건

Owner가 각 태스크 ID를 명시적으로 언급하며 진행을 승인하면, 해당 태스크만 개별적으로
보류 해제하고 실행한다.

## 완료 기준 (승인 후)

- 각 태스크별 paper-only 검증 완료
- 실전 계좌 적용은 별도 Owner 승인 후
- `python scripts/check_agent_docs.py` 0 error
