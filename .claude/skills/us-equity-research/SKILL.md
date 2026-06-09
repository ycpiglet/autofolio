---
name: us-equity-research
description: This skill should be used for fundamental and valuation analysis of US-listed stocks (S&P 500 / Nasdaq mega- and large-caps). Triggers include "미국주식 분석", "US stock/valuation", analyzing AAPL/MSFT/NVDA-type names, comparing US large-caps, and proposing USD target prices. Used by the Autofolio us-equity-specialist agent. Research proposal only.
---

# US Equity Research (미국주식 전문가 지식)

미국 상장 대형주의 **펀더멘털 + 밸류에이션**을 분석하고 USD 목표가를 제안한다. KRW 투자자의 **환(FX) 레이어**를 항상 분리해서 본다. 제안만 한다(MVP_SPEC §6.6).

## 1. 밸류에이션 멀티플 (US 관행)
- **P/E (forward 우선)** — 성장주는 forward·PEG로 본다.
- **EV/EBITDA, EV/Sales** — 자본구조 중립·고성장 비교.
- **P/FCF, FCF yield** — 현금창출력. 자사주매입 여력의 핵심.
- **Rule of 40**(SaaS) — 성장률+마진 ≥ 40.
반드시 **자기 역사 밴드 + peer** 대비. 메가캡은 지수 집중도(상위 7~10종목 비중)도 본다.

## 2. 펀더멘털·드라이버
- 매출성장률, gross/operating margin 추세, **FCF·ROIC**, 순현금/부채.
- **실적시즌(earnings) 반응** — EPS/매출 서프라이즈보다 **가이던스**가 주가를 좌우.
- **자본환원** — 자사주매입(buyback)·배당. 미국은 buyback 비중 큼.
- **금리 민감도** — 고P/E 장기 성장주는 금리(할인율)에 민감. Fed 경로와 연동(매크로 입력).

## 3. 섹터 렌즈
- **Tech/Semis** — AI capex 사이클, 데이터센터, 반도체 수요. 메가캡(Mag7) 주도.
- **Comm Services** — 광고·플랫폼.
- **Financials** — 금리·NIM·자본비율.
- **Energy/Industrials/Healthcare/Staples** — 경기 사이클·방어 성격 구분.
- 지수 집중 리스크: S&P500이 소수 메가캡에 좌우 → 분산 점검.

## 4. KRW 투자자 환·세제 레이어 (필수)
- **총수익 = 주가수익(USD) + 환수익(USD/KRW)**. 강달러는 수익 가산, 원화강세는 차감. FX 전문가와 협업.
- 세제(개인, 현행 확인): **미국주식 매매차익 양도소득세 22%(지방세 포함), 연 250만원 기본공제**, 손익통산·연 1회 신고. **배당은 미국에서 15% 원천징수**(국내 추가세 없음), 금융소득종합과세 합산 대상.

## 5. 목표가 도출
1. forward EPS/FCF 추정(컨센서스 vs 자체).
2. 적정 멀티플 = 역사·peer·성장/리스크.
3. 목표가(USD) = 멀티플 × 지표. 보수/기본/낙관.
4. 현재가 대비 상·하방 + 진입/청산 조건 + **환 시나리오 코멘트**.

## 출력 형식
- **Thesis(as-of)** 2~3문장 · **밸류에이션**(멀티플 vs 역사/peer) · **촉매·리스크 + KRW 환 노트** · **제안 조건**(USD 목표가 + 근거 + 확신도).

## 가드레일
리서치 제안만. 조건 자동저장·자동매매·주문 금지. 미국주식 직접 실행은 현 MVP 엔진 범위 밖일 수 있음 — 해당 시 명시. 사람 승인 후 mandate·`app/engine`.
