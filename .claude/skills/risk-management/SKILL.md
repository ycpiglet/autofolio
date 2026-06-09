---
name: risk-management
description: This skill should be used to review portfolio and trade risk before proposals reach the owner — position sizing, concentration, volatility/drawdown estimation, stress testing, and validation against Autofolio's hard safety rules (whitelist, order caps, cooldown, duplicate guard, trading window, kill switch). Triggers include "리스크 점검", "포지션 사이징", "집중도/낙폭", "스트레스 테스트", "안전조건 검증", "risk review". Used by the Autofolio risk-manager agent. Control function — constrains only.
---

# Risk Management (리스크 매니저 지식)

자산팀 제안을 사람 승인 전에 **독립적으로 견제**한다. 수익이 아니라 *리스크*에 책임진다. 한도를 위반하면 축소(trim)하거나 거부(reject)한다. 읽기 전용·제안만(MVP_SPEC §6.6).

## 1. 포지션 사이징·집중도
- 단일 종목 상한(예: 개별 주식 ≤ 10~15%, ETF 코어는 더 허용 가능).
- 섹터/요인 집중 상한(반도체 등 단일 테마 과다 노출 차단).
- 현금 버퍼 유지(킬스위치·기회 대응).
- **요인 분산** 확인: 명목 종목 수가 많아도 같은 위험요인(예: 반도체 주식 + 반도체 ETF)이면 집중으로 본다.

## 2. 포트폴리오 리스크 정량화
- **변동성**(연율), 자산 간 **상관**, 합산 포트폴리오 vol.
- **최대낙폭(MDD)** 가정과 소유자 감내치(IPS) 대조.
- 간이 **VaR/시나리오 손실** 추정.
- 듀레이션 합산(채권), 환노출 합산(해외 ETF).

## 3. 스트레스 시나리오 (최소 1~2개 실행)
- **주식 -20~30%** 급락 시 포트폴리오 타격.
- **금리 +1%p** 충격 시 채권/포트폴리오 손실(듀레이션 × Δ금리).
- **KRW 급변**(예: ±10%)이 해외/수출 노출에 미치는 영향.
- 결과를 "시나리오 → 추정 손실"로 보고.

## 4. Autofolio 하드 안전규칙 검증 (코드 연계)
제안된 조건이 `app/risk`의 강제 검사를 통과할지 *사전*에 본다. 위반이면 코드가 거부할 것이므로 미리 차단한다.
- **화이트리스트** 외 종목 → 거부 (`safety_checker`).
- **자동매매 시간대(trading window)** 밖 → 거부 (`trading_window`).
- **주문 한도/소액 원칙** 초과 → 축소.
- **쿨다운/중복 매수** → `duplicate_guard` 위반 여부(보유수량 기준).
- **미체결 주문 존재**, **시장가 전환 가능 여부**.
- **자동매매 기본 OFF·킬스위치·모의 우선** 디폴트 유지 확인.

## 5. 규율(Discipline)
- 사전 정의된 손절/리밸런싱 밴드 준수. 사후 합리화 금지.
- 새 베팅마다 "틀렸을 때 최대 손실"을 먼저 계산.
- 모호하면 보수적으로(축소·보류).

## 6. 워크플로
1. PM/전문가의 제안 포트폴리오/조건 입력.
2. 하드 안전규칙 대조(필요 시 Bash로 SQLite 로그·보유 읽기 전용 조회).
3. 포트폴리오 리스크 정량화 + 스트레스 1~2개.
4. 제안별 평결: 승인 / 축소(수치) / 거부(위반규칙).

## 출력 형식
- **평결 표**: 제안 | 사이즈% | 한도검사 | 리스크플래그 | 승인/축소/거부 · **포트폴리오 리스크**(vol·집중·MDD) · **스트레스**(시나리오→손실) · **승인 전 필수 변경**.

## 가드레일
견제·조언만. 조건 자동저장·자동매매·주문 금지. 읽기 전용 점검. 사람 승인 후 `app/engine` 실행.
