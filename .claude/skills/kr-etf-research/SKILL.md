---
name: kr-etf-research
description: This skill should be used for ETF selection and due diligence for a Korean portfolio — comparing same-exposure ETFs (KODEX/TIGER/etc.), evaluating expense ratio, tracking error, liquidity, AUM, premium/discount, structure, and FX hedging. Triggers include "ETF 분석/선택", "어떤 ETF 사", "KODEX vs TIGER", "추적오차/보수/괴리율", "ETF research". Used by the Autofolio etf-specialist agent. Research proposal only.
---

# ETF Research (ETF 전문가 지식)

원하는 **익스포저**를 가장 싸고·유동성 좋고·추적오차 작은 ETF로 매칭한다. 국장 ETF 중심 전략의 핵심 빌딩블록. 제안만 한다(MVP_SPEC §6.6).

## 1. ETF 실사 체크리스트
| 항목 | 보는 것 |
|---|---|
| **총보수(TER)** | 낮을수록 좋음. 동일 지수면 보수가 1차 결정요인 |
| **추적오차(Tracking error)** | 지수와의 괴리. 작을수록 좋음 |
| **순자산(AUM)/설정액** | 너무 작으면 상장폐지·유동성 위험 |
| **괴리율(Premium/Discount)** | 시장가 vs NAV. LP가 관리. 큰 괴리 시 진입 주의 |
| **유동성** | 호가 스프레드, 거래대금, LP 존재 |
| **복제방식** | 실물복제(권장) vs 합성(스왑·거래상대방위험) |
| **분배 방식** | 분배형 vs TR(재투자) |
| **환헤지** | (H) 헤지 vs 비헤지 — 해외자산 ETF의 환노출 결정 |
| **레버리지/인버스** | 일간 복리효과로 장기 보유 부적합 — 주의 |

## 2. 한국 ETF 시장 지형
- 주요 브랜드: **KODEX(삼성), TIGER(미래에셋), KBSTAR/RISE(KB), ACE(한투), SOL(신한), PLUS/ARIRANG** 등.
- 같은 지수(예: KOSPI200, S&P500)를 여러 운용사가 출시 → **보수·추적오차·유동성으로 차별화**.
- 커버리지: 국내주식형, 해외주식형(미국·중국), 채권형, 원자재, 테마(반도체·2차전지·AI·배당).

## 3. 세제 (개인, 현행 확인 필수)
- **국내 주식형 ETF** — 매매차익 비과세(분배금은 배당소득세).
- **기타 ETF(해외·채권·원자재·레버리지 등)** — 매매차익에 배당소득세(15.4%) 과세, 보유기간 과세 방식. 금융소득종합과세 합산 가능.
- ISA/연금 래퍼 활용 시 세후 효율 개선. 정확한 세율·방식은 호출 시점 기준으로 확인하고 명시한다.

## 4. 선택 워크플로
1. 목표 익스포저·제약(통화·세제·만기) 정의.
2. 동일 익스포저 ETF 숏리스트 → TER·추적오차·AUM·괴리율·유동성 비교(표).
3. 구조(실물/합성·환헤지·레버리지) 점검.
4. 1개 추천 + 목표가 조건 제안.

## 5. 흔한 함정
- 보수만 보고 추적오차·유동성 무시.
- 레버리지/인버스를 장기 보유.
- 합성 ETF의 거래상대방위험 간과.
- 해외 ETF 환노출(H 여부) 확인 누락.
- 소형 ETF의 상장폐지·괴리 리스크.

## 출력 형식
- **익스포저 & 숏리스트**(티커·TER·AUM·추적오차·괴리율 표) · **추천 ETF & 이유** · **구조/환/레버리지/세제 caveat** · **제안 조건**(목표가 + 확신도).

## 가드레일
리서치 제안만. 조건 자동저장·자동매매·주문 금지. 화이트리스트만. 사람 승인 후 `app/engine`.
