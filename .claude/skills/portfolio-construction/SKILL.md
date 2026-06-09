---
name: portfolio-construction
description: This skill should be used when turning a target asset allocation into concrete positions — position sizing, rebalancing trades, and target-price buy/sell conditions over a whitelist. Triggers include "포트폴리오 구성/리밸런싱 해줘", "비중 정해줘", "포지션 사이징", "목표가 조건 만들어줘", "construct/rebalance the portfolio". Used by the Autofolio portfolio-manager agent. Proposal only — never executes trades.
---

# Portfolio Construction & Sizing (PM 지식)

전략적 배분(CIO)과 종목/상품 의견(전문가)을 받아 **실행 가능한 포트폴리오**로 옮긴다. 산출물은 Autofolio 엔진이 이해하는 **목표가 도달형 조건**으로 표현한다. 제안만 한다(MVP_SPEC §6.6).

## 1. 포지션 사이징 방법
용도에 맞게 선택·혼합한다.
- **동일가중(Equal weight)** — 단순·견고. 종목 수로 1/N.
- **확신가중(Conviction)** — 전문가 확신도에 비례. 단, 상한 캡 필수.
- **변동성 역가중(Risk-based, 간이 risk parity)** — 변동성 큰 자산 비중 축소. 변동성 추정치 필요.
- **핵심-위성(Core-Satellite)** — 코어(저비용 광범위 ETF) + 위성(소수 대형주/테마). 개인 국장 포트폴리오에 적합.

**필수 한도**
- 단일 종목 상한(예: 개별 주식 ≤ 10~15%), 섹터 집중 상한, 현금 버퍼 유지. (실제 수치는 `risk-management`/리스크매니저와 합의)

## 2. 리밸런싱
- **밴드식 우선**: 목표비중 ± 밴드 이탈 시에만 거래 → 비용 절감.
- **현금흐름 리밸런싱**: 신규 납입·배당으로 저비중 자산 매수 → 매도 없이 정렬(세금·수수료 최소).
- **세금/비용 인식**: 불필요한 회전 지양. 국내주식 매매 증권거래세, 상품별 세제 차이 고려(현행 세율 확인).

## 3. 결정 → 조건 변환 (Autofolio 핵심)
모든 결정은 다음 필드로 표현한다.
```
종목/ETF | 방향(매수/매도) | 목표가 | 수량 또는 금액 | 주문유형(지정가/시장가) | 근거
```
- MVP는 **목표 가격 도달형 조건**만 지원하므로, 뷰를 "현재가 X 근처에서 목표가 Y 도달 시 Z주 매수"로 구체화한다.
- 분할매수/분할매도(스케일 인/아웃)로 타이밍 리스크 분산을 권고.
- 소액·모의 우선 원칙 유지.

## 4. 갭 분석 워크플로
1. 입력: 목표배분(CIO) + 현재 포트폴리오/화이트리스트.
2. 현재비중 vs 목표비중 갭 계산(표).
3. 갭을 구체 종목/ETF로 매핑(전문가 의견 결합).
4. 각 매핑을 목표가 조건으로 변환.
5. 리스크 한도 통과 여부 사전 점검 후 제시.

## 5. 분산·상관 점검
- 같은 위험요인 중복 회피(예: 반도체 대형주 + 반도체 ETF = 동일 베팅). 외형상 종목 수가 많아도 *요인 분산*이 핵심.
- 환노출(해외 ETF), 듀레이션(채권) 합산 노출을 본다.

## 출력 형식
- **목표 vs 현재 비중**(표) · **제안 조건 목록**(위 필드) · **리밸런싱 순서·예상비용** · **리스크매니저/CIO에 넘길 미결사항**.

## 가드레일
제안만. 조건 자동저장·자동매매 ON·주문 실행 금지. 화이트리스트만. 사람 승인 후 `app/engine` 실행.
