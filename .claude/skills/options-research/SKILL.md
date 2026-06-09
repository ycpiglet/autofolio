---
name: options-research
description: This skill should be used for options (옵션) analysis — covered calls, cash-secured puts, protective puts, collars, vertical spreads, the Greeks (delta/gamma/theta/vega), and implied vs realized volatility — for hedging or income on equity/ETF/index underlyings. Triggers include "옵션 전략/분석", "covered call/protective put", "변동성/그릭스", options hedge or income. Used by the Autofolio options-specialist agent. High-risk; advisory only.
---

# Options Research (옵션 전문가 지식)

상장 **옵션**을 인컴·헤지 수단으로 분석한다. 개인 계좌에는 **정의된 손실(defined-risk)** 구조만 제안하고, 네이키드 매도는 부적합으로 표시한다. 제안만 하며 옵션은 현 MVP 실행 범위 밖이다(MVP_SPEC §6.6).

## 1. Greeks (반드시 설명)
- **Delta** — 기초자산 1 변화당 옵션가 변화(방향 노출·헤지비율).
- **Gamma** — 델타의 변화율(볼록성). 만기·ATM에서 큼.
- **Theta** — 시간가치 감소(매도자 우호, 매수자 비용).
- **Vega** — 변동성 1%p 변화 민감도.
- **Rho** — 금리 민감도(보통 영향 작음).

## 2. IV vs 실현변동성
- **내재변동성(IV)** 이 비싼지/싼지로 구조 선택. IV 高 → 프리미엄 매도(커버드콜/CSP) 우호. IV 低 → 매수(보호풋·스프레드) 우호.
- IV Rank/Percentile, 스큐(skew), 만기별 텀구조 참고.

## 3. 정의된 손실 구조 (개인 적합)
| 전략 | 목적 | 손익 |
|---|---|---|
| **Covered Call** | 보유주에 인컴 | 상방 제한, 프리미엄 수취 |
| **Cash-Secured Put** | 목표가 매수 + 인컴 | 하락 시 인수, 프리미엄 |
| **Protective Put** | 하락 헤지 | 보험료(프리미엄) 비용, 하방 제한 |
| **Collar** | 저비용 헤지 | 콜 매도로 풋 비용 상쇄, 상하 제한 |
| **Vertical Spread** | 방향성, 정의된 손실 | max손익 한정 |
- **금지/주의**: 네이키드 콜/풋 매도(무한·대형 손실) → 개인 계좌 부적합.

## 4. 매 구조마다 정량화
- **Max profit / Max loss / Breakeven / 주요 Greeks** 를 진입 시점에 명시.
- **배정(assignment)·조기행사** 가능성, 만기 처리.
- 기초자산(보유주·ETF·지수)과 포트폴리오 목표(인컴/헤지) 연결.

## 5. 워크플로
1. 목적 구분: 인컴 / 헤지 / 뷰 표현.
2. 기초자산에 맞는 정의된 손실 구조 선택.
3. max익·max손·BE·Greeks·IV맥락 계산.
4. 제안 + 리스크·배정 노트.

## 출력 형식
- **목적 & 구조**(예: X 커버드콜) · **페이오프**(max익·**max손**·BE·핵심 Greeks) · **변동성 맥락**(IV vs 실현) · **제안 구조 + 리스크 노트·확신도**.

## 가드레일
리서치·교육 제안만. 조건 자동저장·자동매매·주문 금지. **옵션은 현 MVP 실행 범위 밖** — 조언 한정. 개인 계좌에 무한손실 구조 금지. 리스크매니저 협업, 사람 승인.
