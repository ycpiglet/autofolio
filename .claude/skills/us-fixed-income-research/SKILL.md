---
name: us-fixed-income-research
description: This skill should be used for US fixed-income analysis — US Treasuries, TIPS, IG/HY credit, the US yield curve and Fed path, and USD bond ETFs (SHY/IEF/TLT/AGG/LQD/HYG/TIP). Triggers include "미국 채권/국채 분석", "US treasuries/duration", Fed duration views, USD-bond vehicle choice. Used by the Autofolio us-fixed-income-specialist agent. Research proposal only.
---

# US Fixed Income Research (미국채권 전문가 지식)

Fed·금리 뷰를 **USD 듀레이션·커브·크레딧 스탠스**로 옮기고, 글로벌 분산·인컴·완충 역할을 설계한다. 한국채권은 `kr-fixed-income-research`로 분리. 제안만 한다(MVP_SPEC §6.6).

## 1. 채권 기본 (적용)
- 금리↔가격 역관계, **듀레이션**(금리 1%p 변화 민감도), 볼록성, YTM·캐리·롤다운.

## 2. 미국 시장 구조
- **US Treasuries** — 2Y/5Y/10Y/30Y. 글로벌 무위험 벤치마크. 2s10s **역전(inversion)**은 침체 신호로 주시.
- **TIPS** — 물가연동, 실질금리·BEI(기대인플레) 노출.
- **IG credit** — 투자등급 회사채(스프레드 보상).
- **HY credit** — 하이일드, 경기·디폴트 민감.
- **MBS/지방채** — 참고.

## 3. Fed·커브·듀레이션
- **인하 사이클 기대** → 듀레이션 확대(TLT/장기). bull steepener 가능.
- **고금리 장기화/인상** → 듀레이션 축소(SHY/단기), bear flatten 주의.
- **2s10s 역전·정상화** 흐름과 term premium 점검. 한미 금리차는 KR/환에 직접 영향(매크로·FX 협업).

## 4. 비히클 (USD ETF)
| 목적 | 예시 |
|---|---|
| 단기 국채(현금성) | SHY, BIL |
| 중기 국채 | IEF |
| 장기 국채(듀레이션 베팅) | TLT, EDV |
| 종합채권 | AGG, BND |
| IG 회사채 | LQD, VCIT |
| HY | HYG, JNK |
| 물가연동 | TIP, SCHP |
점검: 목표 듀레이션, expense ratio, 유동성, 분배.

## 5. KRW 투자자 레이어
- USD 채권수익 + **USD/KRW** 환수익으로 분해. 안전자산 USD 채권은 위기 시 강달러로 환이 추가 완충이 되기도 함(FX 협업).
- 세제: US 상장 채권ETF 분배·매매차익은 미국 ETF 세제 동일(양도세 22%·배당 원천 15%, 현행 확인).

## 6. 워크플로
1. Fed/인플레 뷰 + 채권의 포트폴리오 역할.
2. USD 목표 듀레이션·커브 위치.
3. Treasury vs credit + 구체 USD 비히클.
4. 제안 비중/조건 + 금리·환 caveat.

## 출력 형식
- **금리뷰 & 스탠스(as-of)**: 듀레이션+커브 · **국채 vs 크레딧** · **비히클**(듀레이션·보수·유동성) · **제안 비중/조건 + 금리·환 리스크·확신도**.

## 가드레일
리서치 제안만. 조건 자동저장·자동매매·주문 금지. 미국 직접 실행은 현 MVP 범위 밖일 수 있음 — 명시. 사람 승인 후 `app/engine`.
