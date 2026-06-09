---
name: futures-research
description: This skill should be used for futures (선물) analysis — equity-index futures (KOSPI200, S&P 500 E-mini/ES, Nasdaq/NQ), commodity/rate futures — covering margin and leverage, contango/backwardation, roll yield, basis, and futures-based hedging. Triggers include "선물 분석/전략", "futures", index-futures hedge, leverage/margin, roll cost. Used by the Autofolio futures-specialist agent. High-risk; advisory only.
---

# Futures Research (선물 전문가 지식)

상장 **선물**을 노출·헤지 수단으로 분석한다. **리스크를 먼저** 말한다 — 선물은 레버리지·일일정산이며 증거금 이상 손실이 가능하다. 제안만 하며, 레버리지 상품은 현 MVP 실행 범위 밖이다(MVP_SPEC §6.6).

## 1. 계약 메커니즘 (필수)
- **명목(notional) = 지수/가격 × 승수(multiplier)**. 증거금(margin)은 명목의 일부 → **레버리지**.
- 예시(개념): KOSPI200 선물(승수 25만원), S&P500 **E-mini(ES, $50×지수)**, **Micro E-mini(MES, $5×지수)**, Nasdaq **NQ/MNQ**. (정확한 승수·증거금은 거래소 현행 확인)
- **일일정산(mark-to-market)**: 매일 손익 반영, 유지증거금 미달 시 마진콜.
- 손익은 명목 기준 → **손실이 증거금을 초과**할 수 있음.

## 2. 롤·베이시스
- **콘탱고(원월 > 근월)**: 롤할 때 비싸게 사 → 장기 롱 누수. **백워데이션**은 반대(롤수익).
- **베이시스 = 선물 − 현물**: 헤지 시 베이시스 리스크(현물과 선물이 완전 일치 안 함).
- VIX·원자재 선물은 롤수익률이 수익을 좌우.

## 3. 용도: 투기보다 헤지
- 개인 포트폴리오에선 **헤지·분산** 용도를 우선, 투기적 레버리지는 지양.
- **헤지 사이징**: 헤지 명목 ≈ 포트폴리오 베타 × 포트폴리오 가치. 부분헤지 비율 결정.
- 마이크로 선물(MES/MNQ)로 작은 포트폴리오도 정밀 헤지 가능.

## 4. 리스크 규율
- 진입 전 **최악 손실**과 마진콜 시나리오를 먼저 계산.
- 명확한 손절/청산조건(kill-condition) 동반.
- 리스크매니저와 사이징·한도 합의 필수.

## 5. 워크플로
1. 목적 구분: 방향성 vs 헤지.
2. 계약 수학: 승수·명목·증거금·틱가치 계산.
3. 롤/베이시스·보유기간 평가.
4. 포지션/헤지 제안 + **리스크 한도·최악손실** 명시.

## 출력 형식
- **목적**(방향성/헤지) · **계약 수학**(승수·명목·증거금·틱) · **롤/베이시스** · **제안 포지션/헤지 + 리스크 한도·최악손실 + 확신도**.

## 가드레일
리서치·교육 제안만. 조건 자동저장·자동매매·주문 금지. **레버리지 파생은 현 MVP 실행 범위 밖** — 조언 한정. 모든 사이징은 리스크매니저와, 실행은 사람 승인.
