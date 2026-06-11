---
type: evidence
id: EVIDENCE-2026-06-11-006
status: recorded
owner: Research Agent
created: 2026-06-11
created_at: 2026-06-11T12:50:32+09:00
related_taskset: TASKSET-AF-UI-CONTROL-DESK
---

# EVIDENCE-2026-06-11-006 — Autofolio UI design research and taskset basis

## 요청

Owner는 `docs/design` 자료를 다시 첨부한 뒤, 디자인 리서치와 구상을 다시 수행하고
대화 기록 후 UI 개발 계획 및 taskset 등록을 요청했다.

## 확인한 로컬 근거

| 항목 | 결과 |
|------|------|
| `docs/design` 존재 여부 | 복구됨. 현재 git 기준 `?? docs/design/` untracked |
| tracked 이력 | `git ls-files docs/design` 결과 없음 |
| commit 이력 | `git log --all -- docs/design` 결과 없음 |
| stash 포함 여부 | `git stash show --name-only` 전체 확인 결과 `docs/design/` 없음 |
| 기존 UI 기준 | `docs/UI_SPEC.md`의 상단 모드 배지, Auto ON/OFF, 킬스위치, 확인 모달 |
| 안전 기준 | `docs/PRODUCT_BLUEPRINT.md`와 `agents/lead_engineer/SAFETY-RULEBOOK.md`의 fail-closed 운영 |

## 분석한 디자인 후보

| 후보 | Autofolio 적용 판단 |
|------|----------------------|
| Coinbase | 기본 금융 신뢰감, 흰 캔버스, 단일 블루 액센트, 숫자 mono 철학이 적합 |
| IBM / Carbon | 데이터 밀도, 4px grid, semantic 상태색, 엔터프라이즈 운영 UI에 적합 |
| Binance | 거래 표면, 시장 테이블, 가격 방향성 표시에 부분 적용 |
| Linear / Raycast | 에이전트 로그, command-console, incident surface에 부분 적용 |
| Airtable | 설정/연동/빈 상태처럼 workflow SaaS 표면에 부분 적용 |
| Wise / Revolut / Apple | 마케팅/소비자 브랜드 성격이 강해 기본 앱 톤으로는 부적합 |

## 외부 리서치 출처

- Carbon Data Table: https://carbondesignsystem.com/components/data-table/usage/
- Carbon Notification: https://carbondesignsystem.com/components/notification/usage/
- Fluent 2 Web Components: https://fluent2.microsoft.design/components/web/react
- Streamlit Theming: https://docs.streamlit.io/develop/concepts/configuration/theming
- WCAG 2.2 Error Prevention: https://www.w3.org/TR/WCAG22/

## 결정 근거

Autofolio는 자동매매 OS이며, 최근 paper 계좌에서 의도보다 많은 주문이 발생한 사고가
있었다. 따라서 UI는 소비자 핀테크 마케팅 톤보다 운영 관제와 오조작 방지가 우선이다.
기본 방향은 `Autofolio Control Desk`로 정한다.

## 적용 시사점

1. 모든 주문 가능 화면은 환경, 출처, 모드, Auto/Kill, guard 상태를 먼저 보여줘야 한다.
2. Home은 hero/landing이 아니라 control desk 요약이어야 한다.
3. Trade는 주문 입력보다 guard checklist와 확인 흐름이 앞서야 한다.
4. Agents/Alerts는 다크 콘솔 표면을 허용하되, 전체 앱의 기본 톤은 밝게 유지한다.
5. 색상만으로 상태를 전달하지 않는다.
