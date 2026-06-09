---
name: kr-fixed-income-research
description: This skill should be used for bond and fixed-income analysis for a Korean investor — duration positioning, yield-curve shape (국고채 3/10/30Y), credit quality and spreads (회사채), and selecting bond ETFs/funds for income and ballast. Triggers include "채권 분석", "듀레이션", "금리커브", "국고채/회사채", "채권 ETF", "fixed income", "credit". Used by the Autofolio fixed-income-specialist agent. Research proposal only.
---

# Fixed Income Research (채권 전문가 지식)

거시·금리 뷰를 **듀레이션·커브·크레딧 스탠스**로 옮기고, 인컴과 포트폴리오 완충(ballast) 역할을 설계한다. 제안만 한다(MVP_SPEC §6.6).

## 1. 채권 기본기 (반드시 적용)
- **금리 ↔ 가격 역관계**: 금리 하락 = 채권가격 상승.
- **듀레이션** = 금리 1%p 변화 시 가격 민감도(근사). 장기채일수록 큼. 금리 인하 기대 시 듀레이션 확대.
- **볼록성(Convexity)**: 큰 금리 변동에서 듀레이션 추정 보정.
- **YTM/캐리·롤다운**: 보유 수익의 원천.

## 2. 한국 채권시장 구조
- **국고채(KTB)** — 3Y/5Y/10Y/30Y가 벤치마크. 무위험 기준금리 커브.
- **통안채** — 한은 발행, 단기.
- **회사채(여전채·은행채 포함)** — 신용위험 → **신용스프레드**(국고채 대비 가산금리)로 보상.
- **신용등급** — AAA~BBB(투자등급) / BB 이하(투기등급). 개인 포트폴리오는 보통 투자등급·우량 위주.

## 3. 커브·듀레이션 포지셔닝
- **금리 인하 사이클 기대** → 듀레이션 확대(장기 국고채/장기채 ETF). bull steepener/flattener 구분.
- **인플레 재점화·인상 기대** → 듀레이션 축소(단기채·통안). bear flattener 주의.
- **커브 전략**: steepener(장단기차 확대 베팅) vs flattener. 한미 금리차·한은 경로가 변수.

## 4. 크레딧 판단
- 스프레드가 **부도·강등 위험 대비 충분히 보상**하는지 본다. 경기 후퇴 국면엔 스프레드 확대 위험.
- 개인은 개별 회사채 분산이 어려워 **채권 ETF/펀드로 분산** 권고.
- 품질 우선: 추가 스프레드가 명백히 보상될 때만 신용 위험 확대.

## 5. 비히클 선택 (개인)
- **직접 국고채/회사채** vs **채권 ETF/펀드**.
- 채권 ETF 점검: 목표 듀레이션, 보수(TER), 유동성, 분배/TR, 만기매칭형(존속기한) 여부.
- 역할 정의: **인컴 + 주식과의 분산/완충**. 사이징은 리스크매니저와 합의.

## 6. 워크플로
1. 금리·인플레 뷰(매크로 입력) + 채권의 포트폴리오 역할 확인.
2. 목표 듀레이션·커브 위치 결정.
3. 국고 vs 크레딧 선택(스프레드 근거).
4. 구체 비히클 + 제안 비중/조건 + 금리리스크 caveat.

## 출력 형식
- **금리뷰 & 스탠스(as-of)**: 듀레이션+커브, 1줄 why · **국고 vs 크레딧** 추천 · **비히클**(듀레이션·TER·유동성) · **제안 비중/조건·리스크·확신도**.

## 가드레일
리서치 제안만. 조건 자동저장·자동매매·주문 금지. 화이트리스트만. 사람 승인 후 `app/engine`.
