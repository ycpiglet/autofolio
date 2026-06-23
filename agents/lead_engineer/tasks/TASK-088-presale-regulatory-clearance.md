---
type: task
id: TASK-088
display_id: TASK-088
task_uid: 2a9f7c41-6d83-4e15-b0c7-9e2a4f1d6e8b
registered_at: 2026-06-19T00:20:13+09:00
created_at: 2026-06-19T00:20:13+09:00
updated_at: 2026-06-19T00:20:13+09:00
status: 보류
owner: Lead Engineer
assignees: [Compliance Officer, Lead Engineer, Research Agent]
priority: High
difficulty: 상
est_hours: 16
est_tokens: 120000
tags: [compliance, regulatory, legal, gate, deferred, deploy]
gate: Owner direct request; deferred until product maturity; NO commercial launch before clearance
trigger_meeting: Owner direct request 2026-06-19
deferred_until: 프로덕트가 "판매 가능 수준"으로 성숙(유료 베타/결제 연동 직전)
audit_log: AUDIT-2026-06-19-004
created: 2026-06-19
---

# TASK-088 판매 전 금융규제 클리어런스 (비조치의견서 + 샌드박스)

작업 ID: TASK-088
상태: 보류
Owner: Lead Engineer
요청 시각: 2026-06-19T00:20:13+09:00
기록 시각: 2026-06-19T00:20:13+09:00
요청자: Owner
수행자: Lead Engineer, Compliance Officer, Research Agent
의도: 유료 상용 출시 전, 모델의 금융규제 분류를 공식 통로로 확인해 형사·영업정지 리스크를 차단한다.
대상: KIS OpenAPI 약관, 금융위 비조치의견서, 금융규제 샌드박스/로보 테스트베드 상담, 제품 포지션 문서
방법: 제품 성숙 전에는 기록만 유지하고, 유료 베타/결제 연동 직전 공식 절차와 전문가 검토로 clearance를 확보한다.
감사 로그: AUDIT-2026-06-19-004

## 왜 deferred 인가

Owner 판단(2026-06-19): 현재 프로덕트가 판매 가능 수준으로 성숙하지 않아 지금 신청서를 쓰는 것은 의미가
적다. 따라서 **기록만 남기고**, 성숙 시점에 착수한다. 단, 이 게이트의 **중요성은 상시 유지**한다
(CLAUDE.md "Compliance Gate" 섹션 + 메모리 `compliance-gate-presale` 로 LLM이 항상 인지).

## 트리거 (착수 조건)

- 프로덕트가 유료 베타/결제 연동을 붙일 만큼 성숙했을 때, **또는**
- 불특정 다수에게 돈을 받고 실거래 추천/자동실행을 제공하기로 결정했을 때.
- 그 전 단계라도 KIS OpenAPI 약관(멀티유저·상용 허용 여부)은 **먼저** 확인 가능.

## 범위 (착수 시)

포함:

- 금융위 **비조치의견서(no-action letter)** 신청서 작성·제출 (LLM으로 초안, 사람이 검토·제출).
- **금융규제 샌드박스(혁신금융서비스)** 신청 또는 한국핀테크지원센터/코스콤(로보 테스트베드) 상담.
- 제품 포지션 문서화: "유저 자가운영 SW 판매" — 우리가 추천/운용/일임하지 않음을 구조·약관으로 입증.
- "SW 판매 vs 유사투자자문" 경계, 특히 **추천 기능**에 대한 질의 포함.

제외(이 태스크 아님):

- 실제 배포·결제 연동(TASK-087)과의 코드 작업.
- 변호사 풀리테이너(필요 시 단발 유료 상담으로 보완).

## 완료 조건

- [ ] KIS OpenAPI 약관 검토 결과 기록.
- [ ] 비조치의견서 신청·회신(또는 샌드박스 지정/상담 결과) 확보.
- [ ] 회신에 맞춰 제품 포지션·약관·기능 플래그(추천/자동실행) 조정 완료.
- [ ] 클리어런스 전까지 상용(유료) 출시는 하지 않았음을 확인.

## 참고

- 연계: TASK-087(웹 배포 + 구매자 한정 회원제). 이 게이트를 통과해야 TASK-087의 상용 출시 단계로 간다.
- 항상 인지 장치: CLAUDE.md "Compliance Gate" 섹션, 메모리 `compliance-gate-presale`, `.remember/remember.md`.
