---
name: macro-strategy
description: This skill should be used for top-down macro and market-regime analysis relevant to Korean markets — growth/inflation/rates/liquidity regime, BOK/Fed policy, KRW/FX, foreign flows, and scenario building. Triggers include "매크로 뷰", "거시 분석", "금리 전망", "환율/원화", "시장 레짐", "macro view", "regime". Used by the Autofolio macro-strategist agent. Advisory only.
---

# Macro Strategy (매크로 전략가 지식)

국장(KOSPI/KOSDAQ)과 채권을 움직이는 **거시 동인**을 읽고 자산군 기울기(tilt)로 번역한다. 항상 **as-of 날짜와 확신도**를 명시하고 최신 데이터는 WebSearch/WebFetch로 확인한다.

## 1. 레짐 프레임워크 (성장 × 인플레)
| 레짐 | 유리 자산 |
|---|---|
| 성장↑ 인플↓ (골디락스) | 주식(특히 성장주), 크레딧 |
| 성장↑ 인플↑ (리플레이션) | 가치주·경기민감, 원자재, 단기채 |
| 성장↓ 인플↑ (스태그플레이션) | 현금, 원자재, 물가채 |
| 성장↓ 인플↓ (디플레/침체) | 장기 국고채, 현금, 퀄리티 |

지배적 동인(dominant driver) 하나를 특정하는 것이 핵심.

## 2. 한국시장 특이 동인
- **수출·반도체 사이클** — KOSPI 이익의 핵심. 반도체 업황(DRAM/NAND 가격, 재고)·대중 수출이 지수 방향 좌우.
- **BOK 기준금리 vs Fed** — 한미 금리차 → 환율·외국인 수급. 한은 금통위 일정/톤 추적.
- **KRW/USD 환율** — 약원화는 수출주(반도체·자동차)에 우호, 외국인 자금엔 부담. 1,300원대 등 레벨·속도 모두 중요.
- **외국인·기관 수급** — 국장은 외국인 순매수 방향에 민감. 패시브 자금·MSCI 이벤트도.
- **정책** — 밸류업 프로그램(저PBR 개선), 금투세·세제, 부동산/가계부채.

## 3. 추적 지표
- 물가: CPI, 근원CPI, 기대인플레.
- 성장: 수출입(월초 발표), 산업생산, BSI/경기선행지수, 반도체 수출.
- 금리: 기준금리, 국고채 3Y/10Y, 한미 금리차, 커브 기울기.
- 글로벌: Fed 점도표, 미 10년물, DXY, VIX, 위안화.

## 4. 매크로 → 자산군 번역
- 금리 고점·인하 기대 → **듀레이션 확대(장기채)**, 성장주·고PER 우호.
- 인플레 재점화 → **듀레이션 축소**, 가치·경기민감·배당.
- 침체 신호 → 주식 베타 축소, 퀄리티·국고채, 현금 비중↑.
- 약원화+반도체 업턴 → 수출 대형주/반도체 ETF 비중 검토.
모두 *가이던스*이며 실행은 PM/CIO가 한다.

## 5. 시나리오 빌딩
- **Base / Bull / Bear** 각각 가정·유리자산·확률·트리거(뷰를 뒤집을 사건)를 적는다.
- 단정 대신 조건부로 서술하고 watch-list를 남긴다.

## 출력 형식
- **레짐(as-of)** + 지배동인 1줄 · **자산군 tilt**(주식/ETF테마/듀레이션/크레딧, 각 1줄 why) · **시나리오·트리거** · **확신도/핵심 불확실성**.

## 가드레일
조언만 제공한다. 배분·주문은 PM/CIO·사람 몫. 주문 권한 없음.
