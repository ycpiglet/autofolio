---
name: commodities-research
description: This skill should be used for commodities and physical/spot (현물) asset analysis — gold/silver, crude oil (WTI/Brent), copper, agriculture — and choosing how to access them (physical, spot ETF, or futures-based ETF). Triggers include "현물/원자재 분석", "금/은/원유 전망", "commodity view", inflation hedge, real-asset allocation. Used by the Autofolio commodities-specialist agent. Research proposal only.
---

# Commodities / Real-Asset Research (원자재·현물 전문가 지식)

**현물(physical/spot) 원자재**의 동인을 읽고 적절한 비히클로 매핑한다. 포트폴리오에서 인플레이션 헤지·실물 분산 역할로 *소량* 편입한다. 제안만 한다(MVP_SPEC §6.6).

## 1. 자산별 핵심 동인
- **금(Gold)** — **실질금리(역관계)·달러(역관계)·안전자산 수요**·중앙은행 매입. 무이자 자산이라 실질금리 하락 국면에서 강세. 위기 헤지.
- **은(Silver)** — 금 + 산업수요(태양광 등). 변동성 더 큼.
- **원유(WTI/Brent)** — 공급(OPEC+ 감산/증산, 지정학)·수요(글로벌 성장)·재고. 변동성 큼.
- **구리(Copper)** — 경기·전기화/그리드 수요. "Dr. Copper" 경기 선행.
- **농산물** — 날씨·작황·재고. 계절성.

## 2. 비히클과 함정 (가장 중요)
| 방식 | 특징 / 함정 |
|---|---|
| **실물(현물)** | KRX **금 현물(KRX 금시장)**, 골드뱅킹, 실물 골드바. 보관·스프레드. KRX 금현물 매매차익 비과세 혜택(현행 확인) |
| **Spot-tracking ETF** | 금 현물 보유 ETF(예: 금 실물형). 현물가 추종, 보수 |
| **Futures-based ETF** | 선물 보유 → **콘탱고(contango) 시 롤비용으로 장기 손실 누수**. 원유 ETF가 대표적 함정 |
| **레버리지/인버스** | 일간복리 → 장기 부적합 |

→ 장기 보유는 **실물/현물 추종**을 선호, 선물기반은 롤수익률(콘탱고/백워데이션)을 반드시 확인.

## 3. 포트폴리오 역할
- **인플레이션·실물 헤지 + 분산자**(주식·채권과 낮은 상관, 특히 금). 무이자/음의 캐리·고변동.
- 코어 인컴 자산 아님 → **소량(예: 한 자릿수 %)**, 리스크매니저와 사이징.
- 금은 위기 헤지, 원유·구리는 경기/인플레 베팅 성격으로 구분.

## 4. 워크플로
1. 어떤 원자재·뷰의 지배동인(실질금리·달러·공급·성장) 식별(매크로/FX 협업).
2. 실물/spot ETF/선물기반 중 선택 — 롤·보관·환 함정 명시.
3. 분산자로서 소량 사이징 제안.
4. 제안 조건 + 리스크.

## 출력 형식
- **View(as-of)**: 원자재 + 지배동인 1줄 · **비히클**(실물/spot/선물기반 + 콘탱고·보관·환 caveat) · **역할·사이징**(분산자, 소량) · **제안 조건 + 리스크·확신도**.

## 가드레일
리서치 제안만. 조건 자동저장·자동매매·주문 금지. 실물·선물 원자재 실행은 현 MVP 엔진 범위 밖 — 조언 한정, 명시. 사람 승인 필요.
