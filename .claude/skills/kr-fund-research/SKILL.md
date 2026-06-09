---
name: kr-fund-research
description: This skill should be used for mutual fund (공모펀드) selection and due diligence for a Korean investor — comparing active funds, evaluating net-of-fee risk-adjusted performance, share classes/fees, manager track record, and deciding fund-vs-ETF. Triggers include "펀드 분석/선택", "공모펀드 추천", "펀드 vs ETF", "운용사/매니저 실사", "클래스/보수", "fund research". Used by the Autofolio fund-specialist agent. Research proposal only.
---

# Fund Research (펀드 전문가 지식)

공모펀드를 **수수료 차감 후·위험조정** 기준으로 선별하고, 같은 익스포저면 저비용 ETF가 더 나은지 항상 따진다. 제안만 한다(MVP_SPEC §6.6).

## 1. 핵심 원칙
- **원수익률이 아니라 net-of-fee 위험조정 성과**로 본다. 보수가 장기 복리를 갉아먹는다.
- 적절한 **벤치마크·동일유형(peer group)** 대비로 평가한다.
- 액티브가 벤치마크를 *지속적으로* 이기지 못하면 패시브 ETF를 권고한다.

## 2. 펀드 실사 프레임
| 항목 | 보는 것 |
|---|---|
| 성과 | 3/5/10년 net vs 벤치마크·peer, **일관성**(연도별), 하락장 방어(downside capture) |
| 위험 | 변동성, MDD, 샤프/정보비율 |
| 보수 | 총보수(TER), 운용·판매보수, 클래스별 차이 |
| 매니저 | 재직기간(tenure), 운용철학, 스타일 일관성, 교체 이력 |
| 규모 | 설정액·순자산(너무 작으면 청산, 너무 크면 capacity 한계) |
| 스타일 | style drift 여부, 벤치마크 추적/일탈 |

## 3. 한국 펀드 클래스·수수료 (필수)
- **클래스 표기**: A(선취판매보수), C(후취·보수율 높음), **e/온라인 클래스(가장 저렴, 직접 가입)**, P(연금), S(펀드슈퍼마켓) 등.
- 동일 펀드라도 **클래스에 따라 총보수가 크게 다름** → 장기·직접가입이면 온라인(e) 클래스 우선 검토.
- **환매수수료**: 단기 환매 시 부과(예: 90일 이내) — 회전 비용 인식.
- 총보수(TER)에 운용+판매+수탁+사무 보수 합산.

## 4. 펀드 vs ETF 결정
- **ETF 우위**: 광범위 지수 노출, 저비용, 실시간 거래, 세제 효율 → 코어 자산.
- **액티브 펀드 우위**: 비효율 시장(중소형·특정 섹터·일부 채권), 검증된 알파 매니저, ETF가 없는 익스포저.
- 같은 노출이면 *디폴트는 저비용 ETF*. 액티브는 알파 근거가 있어야 채택.

## 5. 선택 워크플로
1. 이 펀드의 포트폴리오 내 역할·벤치마크·peer 정의.
2. 장기 net 성과·일관성·하락방어 스크리닝.
3. 보수/클래스·매니저·규모·스타일 점검.
4. 추천 또는 "ETF X로 대체" 결론 + 근거.

## 출력 형식
- **역할 & 벤치마크** · **숏리스트**(클래스·총보수/TER·규모·3/5y net vs BM) · **추천 & 이유**(또는 ETF 대체) · **리스크/caveat·확신도**.

## 가드레일
리서치 제안만. 조건 자동저장·자동매매·주문 금지. 사람 승인 후 mandate·`app/engine` 내에서만 실행.
