---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-R3-ORDER-SURFACE
work_uid: 81aa8a50-14d4-4e3b-be0e-7064b9a934c2
kind: taskset
parent_id: INIT-R3-ORDER-SURFACE
status: blocked
owner: Lead Engineer
created_at: 2026-06-14T09:03:29+09:00
updated_at: 2026-06-14T09:03:29+09:00
origin_type: owner_request
origin_ref: AGENTS.md-section-16
created_by: lead_engineer
title: R3 주문 서피스 태스크셋 (TASK-014,021,022,026,027,028,030,031,032)
summary: Owner 승인 없이 실행 불가 — R3 surface (주문 경로·리스크 게이트·브로커 확장) 9건
tags: [r3, order, risk, broker, owner-gated, blocked]
priority: P3
---

# TASKSET-R3-ORDER-SURFACE — R3 주문 서피스 9건

## ⚠ Owner 승인 전 코드 변경 금지

이 태스크셋의 모든 태스크는 `AGENTS.md §16` R3 surface에 해당한다.
Owner가 각 태스크 번호를 명시하여 승인하기 전까지 어떠한 코드 변경도 하지 않는다.

## 부모 이니셔티브

`INIT-R3-ORDER-SURFACE`

## 포함 태스크

tasks:
  - TASK-014
  - TASK-021
  - TASK-022
  - TASK-026
  - TASK-027
  - TASK-028
  - TASK-030
  - TASK-031
  - TASK-032

| work_id | 설명 | R3 사유 | 현재 상태 |
|---------|------|---------|-----------|
| TASK-014 | KIS 시간외 주문 (장전·장후 단일가) | place_order + 거래시간 정책 변경 | 보류 |
| TASK-021 | KIS 신용·공매도 주문 (SLL_TYPE) | place_order + 안전 분류기 변경 | 보류 |
| TASK-022 | KIS 해외주식 주문 (미국·홍콩 등) | 해외 주문 경로 신설 | 보류 |
| TASK-026 | KRX 대체상품 테스트 지원 | 브로커 order path 닿을 수 있음 | 보류 |
| TASK-027 | KRX 파생상품 테스트 지원 | 브로커 order path 닿을 수 있음 | 보류 |
| TASK-028 | 고급 주문 유형 테스트 지원 | order path 확장 | 보류 |
| TASK-030 | 블록/바스켓 실행 테스트 | 고위험 주문 실행 경로 | 보류 |
| TASK-031 | 시장 정지/VI 리스크 게이트 | 안전 게이트 정책 변경 | 보류 |
| TASK-032 | 데이터 품질 및 기업 행위 테스트 | 브로커 데이터 경로 닿을 수 있음 | 보류 |

## 의존 관계

각 태스크는 Owner 개별 승인을 받아야 진행 가능하며, 일부는 선행 태스크 완료 후 가능:
- TASK-026, TASK-027, TASK-028: 독립 (각각 Owner 승인 후 실행)
- TASK-030, TASK-031: 독립 (각각 Owner 승인 후 실행)
- TASK-021: TASK-014 이후 권장 (기초 시간외 주문 로직 이해 후)
- TASK-022: 독립 (해외 주문 경로 별도)
- TASK-032: 독립

## 재개 조건

Owner가 특정 TASK-ID를 명시하며 진행 승인 시 해당 태스크만 보류 해제.
전체 일괄 승인이 아닌 태스크별 개별 승인 원칙.
