---
name: us-etf-research
description: This skill should be used for selection and due diligence of US-listed ETFs (VOO/SPY/IVV, QQQ, SCHD, sector SPDRs, AGG/TLT/LQD, etc.) for a Korean investor trading on US exchanges. Triggers include "미국 ETF 분석/선택", "US ETF", comparing US-listed ETFs on expense ratio/liquidity, and US-ETF tax/FX. Used by the Autofolio us-etf-specialist agent. Research proposal only.
---

# US ETF Research (미국 ETF 전문가 지식)

**미국 상장 ETF**를 비용·유동성·추적 기준으로 선별한다. KRW 투자자의 세제·환 레이어를 반영한다. KRX 상장 ETF는 `kr-etf-research`로 분리. 제안만 한다(MVP_SPEC §6.6).

## 1. US ETF 실사 체크리스트
| 항목 | 보는 것 |
|---|---|
| **Expense ratio** | 미국은 초저보수(예: VOO/IVV 0.03%). 동일지수면 1차 결정요인 |
| **AUM / 유동성** | 거래량·호가 스프레드. 대형일수록 타이트 |
| **Tracking difference** | 지수 대비 실제 괴리 |
| **Distribution yield** | 분배(미국 ETF는 대개 분배형) |
| **Structure** | 대부분 실물·물리복제. 레버리지/인버스·합성은 고위험 |

## 2. 거의 동일 상품 비교 (핵심 실무)
- **S&P 500**: VOO(0.03) vs IVV(0.03) vs SPY(0.0945, 유동성·옵션 최강) → 장기보유는 VOO/IVV, 트레이딩/옵션은 SPY.
- **Nasdaq100**: QQQ(유동성) vs QQQM(저보수, 장기보유).
- **배당**: SCHD(배당성장) vs VYM(고배당) vs VIG(배당성장 품질) vs DGRO.
- **섹터**: SPDR XLK/XLF/XLE… vs Vanguard VGT 등.
- **채권**: AGG/BND(종합), SHY/IEF/TLT(국채 만기별), LQD(IG), HYG/JNK(HY), TIP(물가).
- **전세계/선진/신흥**: VT, VEA, VWO 등.

## 3. KRW 투자자 세제·환 (필수, 현행 확인)
- **양도소득세 22%(지방세 포함), 연 250만원 기본공제** — 매매차익에 부과, 손익통산·연 1회 신고.
- **분배금(배당) 미국 15% 원천징수** + 금융소득종합과세 합산.
- **환전 비용** — KRW↔USD 스프레드. 매매 잦으면 누적. (FX 전문가 협업)
- **KR 상장 vs US 상장 트레이드오프**: KR 상장 해외ETF는 매매차익 배당소득세(보유기간 과세)·ISA/연금 활용 가능, US 상장은 양도세 22%지만 250만 공제·손익통산 유리. 금액·계좌·회전율로 판단. (KR 비교는 `kr-etf-research`)

## 4. 선택 워크플로
1. 목표 익스포저·제약(USD·세제·기간) 정의.
2. US 상장 후보 숏리스트 → expense ratio·AUM·유동성·tracking·yield 비교.
3. KRW 세제·환 레이어 적용 + KR 상장 대안 언급.
4. 1개 추천 + USD 목표가 조건.

## 출력 형식
- **익스포저 & 숏리스트**(티커·보수·AUM·유동성·yield) · **추천 & 이유** · **세제/환 caveat + KR 상장 대안** · **제안 조건**(USD 목표가 + 확신도).

## 가드레일
리서치 제안만. 조건 자동저장·자동매매·주문 금지. 미국 직접 실행은 현 MVP 범위 밖일 수 있음 — 명시. 사람 승인 후 `app/engine`.
