---
type: capability-matrix
id: BROKER-CAPABILITY-PARITY-MATRIX
status: active
owner: Lead Engineer
created: 2026-06-14
created_at: 2026-06-14T17:28:16+09:00
updated_at: 2026-06-17T09:03:57+09:00
task: TASK-041
related:
  - agents/qa/test_cases/ASSET-UNIVERSE-DECISION-RECORD.md
  - agents/qa/test_cases/EXTERNAL-APP-API-DECISION-RECORD.md
  - agents/qa/test_cases/FEATURE-LANDSCAPE-CATALOG.md
prod_boundary: "R3 order/risk support is mock/paper-first with explicit prod hardguards; no secret, schema migration, or prod mutation"
---

# Broker / Platform Capability Parity Matrix

이 문서는 Autofolio가 지원하는 브로커(KIS, mock, paper)와 참조 플랫폼 기능군을 비교한다.
UI·전략 코드가 지원되지 않는 기능을 노출하지 않도록 명시적 status label을 정의한다.

## Status Legend

| Label | 의미 |
|-------|------|
| `SUPPORTED` | 현재 Autofolio에서 동작하며 테스트 증거가 있음 |
| `MOCK-ONLY` | mock/paper에서만 동작; KIS live 미지원 |
| `PAPER-ONLY` | KIS 모의투자(paper) 환경에서만 허용; 실전 미지원 |
| `CONDITIONAL` | 자산군 Decision Record 조건부 승인 — read-only/manual 범위에 한정 |
| `R3-HOLD` | R3 보류 태스크에 매핑됨; 구현 전 Owner 승인 필요 |
| `PROD-GUARDED` | mock/paper 또는 정책 검증은 구현됨; prod 실행은 명시 override 없이는 차단 |
| `REJECTED` | 기각; 자동/실행 지원 없음; 교육·read-only 메모만 허용 |
| `NOT-IMPL` | 범위 내이나 아직 구현 없음 |

---

## 1. Asset Class Capability

자산군별 현재 Autofolio 지원 상태. 근거: `ASSET-UNIVERSE-DECISION-RECORD.md`.

| Asset Class | KIS Live | Mock / Paper | External Connector | Decision Record Status | Autofolio Status | Blocking Task |
|-------------|----------|--------------|-------------------|------------------------|------------------|---------------|
| 국내 주식 (KOSPI/KOSDAQ) | SUPPORTED | SUPPORTED | — | 승인 | `SUPPORTED` | — |
| 국내 ETF/ETN/REIT | SUPPORTED | SUPPORTED | — | 승인 | `SUPPORTED` | — |
| 국내 ELW proxy | PROD-GUARDED | MOCK-ONLY | — | 승인(proxy) | `PROD-GUARDED` | TASK-026 |
| 해외주식 (US/HK 등) | PROD-GUARDED | PAPER-ONLY order payload + KRW valuation | FX valuation 조건부 | 조건부 승인 (read-only/manual) | `PROD-GUARDED` | TASK-022 |
| 글로벌 ETF | PROD-GUARDED | PAPER-ONLY order payload + KRW valuation | FX valuation 조건부 | 조건부 승인 (read-only/manual) | `PROD-GUARDED` | TASK-022 |
| 코인 Spot | NOT-IMPL | NOT-IMPL | read-only import 조건부 | 조건부 승인 (read-only) | `CONDITIONAL` | — |
| 코인 Futures/Options | NOT-IMPL | NOT-IMPL | 불가 | 보류/R3 | `R3-HOLD` | — |
| 금 (KRX/CME/ETP) | NOT-IMPL | NOT-IMPL | 가격추적 조건부 | 조건부 승인 (tracking/manual) | `CONDITIONAL` | — |
| 은 (CME/ETP) | NOT-IMPL | NOT-IMPL | 가격추적 조건부 | 조건부 승인 (tracking/manual) | `CONDITIONAL` | — |
| 오일 (ETF/ETN) | NOT-IMPL | NOT-IMPL | 가격추적 조건부 | 조건부 승인 (tracking/manual) | `CONDITIONAL` | — |
| 달러 현금/환율 (USD/KRW) | NOT-IMPL | NOT-IMPL | 수동 환율 조건부 | 조건부 승인 (rate/manual) | `CONDITIONAL` | — |
| FX Futures/Options | PROD-GUARDED | MOCK-ONLY contract/margin model | 불가 | 보류/R3 | `PROD-GUARDED` | TASK-027 |
| 부동산 listed (REIT ETF) | NOT-IMPL | NOT-IMPL | REIT/ETF 조건부 | 조건부 승인 (listed only) | `CONDITIONAL` | — |
| 부동산 조각투자 | NOT-IMPL | NOT-IMPL | 불가 | 보류/R3 | `R3-HOLD` | — |
| 저작권/음원 royalty | NOT-IMPL | NOT-IMPL | 수동 cashflow 기록만 | 보류/R3 | `R3-HOLD` | — |
| 상품 옵션 (Commodity Options) | PROD-GUARDED | MOCK-ONLY contract/margin model | education/scenario만 | 보류/R3 | `PROD-GUARDED` | TASK-027/028 |
| 레버리지/인버스 ETP | 차단 | 차단 | 불가 | 기각 | `REJECTED` | — |
| 실물 원자재 logistics | 불가 | 불가 | 불가 | 기각 | `REJECTED` | — |
| DeFi/P2P/Yield/Lending | 불가 | 불가 | 불가 | 기각 | `REJECTED` | — |

**규칙**: UI에 `CONDITIONAL` 자산을 표시할 때 반드시 `read-only / manual / no-auto-execution` 라벨을 붙인다.
`R3-HOLD` 및 `REJECTED` 자산은 UI 실행 버튼/경로를 노출하지 않는다.

---

## 2. Trading Session

| Session | KIS Support | KIS TR | Mock Support | Paper Support | Autofolio Engine | Blocking Task |
|---------|-------------|--------|--------------|---------------|------------------|---------------|
| 정규장 (09:00–15:30 KST) | SUPPORTED | `TTTC0012U`/`TTTC0011U` | SUPPORTED | SUPPORTED | `SUPPORTED` (09:10–15:20 window) | — |
| 장전 단일가 (08:30–09:00) | PROD-GUARDED | ORD_DVSN `05` | MOCK/POLICY | PAPER payload | `PROD-GUARDED` | TASK-014 |
| 장후 단일가 (15:40–16:00) | PROD-GUARDED | ORD_DVSN `06` | MOCK/POLICY | PAPER payload | `PROD-GUARDED` | TASK-014 |
| 시간외 종가 (16:00–18:00) | NOT-IMPL | 별도 TR | NOT-IMPL | NOT-IMPL | `R3-HOLD` | TASK-014 |
| 야간 선물/야간장 | NOT-IMPL | — | NOT-IMPL | NOT-IMPL | `R3-HOLD` | — |
| 해외장 (US/HK 마켓시간) | PROD-GUARDED | 해외주식 별도 | MOCK/PAPER payload | PAPER payload | `PROD-GUARDED` | TASK-022 |
| KRX 휴장일 차단 | SUPPORTED | `is_krx_holiday()` | SUPPORTED | SUPPORTED | `SUPPORTED` | — |

**SafetyChecker 근거**: `app/risk/trading_window.py` — 정규장 09:10–15:20 KST와
`ORDER_SESSION_WINDOWS`를 분리한다. 시간외/R3 주문은 `app/risk/order_policy.py`와
KIS client prod hardguard를 통과해야 한다.

---

## 3. Order Type

| Order Type | KIS ORD_DVSN | Mock Support | Paper Support | Autofolio Engine | Blocking Task |
|------------|--------------|--------------|---------------|------------------|---------------|
| 지정가 (Limit) | `00` | SUPPORTED | SUPPORTED | `SUPPORTED` | — |
| 시장가 (Market) | `01` | SUPPORTED | SUPPORTED | `SUPPORTED` | — |
| 최유리지정가 | `03` | SUPPORTED | PAPER payload | `PROD-GUARDED` | TASK-028 |
| 최우선지정가 | `04` | SUPPORTED | PAPER payload | `PROD-GUARDED` | TASK-028 |
| 조건부지정가 | `02` | SUPPORTED | PAPER payload | `PROD-GUARDED` | TASK-028 |
| Stop / Stop-Limit | mock trigger | SUPPORTED | MOCK/PAPER policy | `PROD-GUARDED` | TASK-028 |
| Trailing Stop | mock trigger | SUPPORTED | MOCK/PAPER policy | `PROD-GUARDED` | TASK-028 |
| IOC / FOK | mock immediate-fill policy | SUPPORTED | MOCK/PAPER policy | `PROD-GUARDED` | TASK-028 |
| MOO / MOC | `05`/`07` | SUPPORTED | PAPER payload | `PROD-GUARDED` | TASK-028 |
| OCO / OTO / OTOCO | NOT-IMPL | NOT-IMPL | NOT-IMPL | `R3-HOLD` | TASK-028 |
| 장전 단일가 주문 | `05` | SUPPORTED | PAPER payload | `PROD-GUARDED` | TASK-014 |
| 장후 단일가 주문 | `06` | SUPPORTED | PAPER payload | `PROD-GUARDED` | TASK-014 |

**근거**: `app/common/enums.py`, `app/risk/order_policy.py`, `app/brokers/kis/kis_client.py`.
고급 주문 유형과 해외/신용/파생/바스켓 표면은 mock/paper-first이며 prod는 기본 차단한다.

---

## 4. Order Lifecycle

| Lifecycle State | Mock | KIS Paper | Autofolio Engine | Notes |
|-----------------|------|-----------|------------------|-------|
| 주문 제출 (OrderResult.REQUESTED) | SUPPORTED | SUPPORTED | `SUPPORTED` | `order_flow.py` |
| 체결 (FILLED) | SUPPORTED | SUPPORTED | `SUPPORTED` | — |
| 대기 (PENDING) | SUPPORTED | SUPPORTED | `SUPPORTED` (limit) | — |
| 취소 (CANCELED) | SUPPORTED | SUPPORTED | `SUPPORTED` | — |
| 실패 (FAILED) | SUPPORTED | SUPPORTED | `SUPPORTED` | — |
| 정정 (MODIFY) | NOT-IMPL | SUPPORTED (`TTTC0013U` ORD_DVSN=01) | `NOT-IMPL` | KIS API 있으나 engine 미연결 |
| 부분체결 추적 | NOT-IMPL | SUPPORTED | `NOT-IMPL` | mock은 전체 체결만 |
| OCO 연동 취소 | NOT-IMPL | NOT-IMPL | `R3-HOLD` | TASK-028 |
| Block/Basket 다중 주문 | MOCK-ONLY | NOT-IMPL | `PROD-GUARDED` | TASK-030 |
| 연속 주문 실패 서킷브레이커 | SUPPORTED (≥3) | SUPPORTED | `SUPPORTED` | `SafetyChecker` |
| 일손실 서킷브레이커 | SUPPORTED | SUPPORTED | `SUPPORTED` | `today_realized_pnl()` |
| Kill switch | SUPPORTED | SUPPORTED | `SUPPORTED` | `kill_switch_active` state |

---

## 5. Fee / Slippage / Fill Model

| Dimension | KIS Live | Mock Broker | Paper Broker | Reference Platforms |
|-----------|----------|-------------|--------------|---------------------|
| 거래 수수료 (fee_rate) | 실제 KIS 요율 (미적용) | `fee_rate` 파라미터 (default 0.0) | KIS 모의 요율 | 증권사마다 다름 |
| 슬리피지 (slippage_bps) | 실제 체결가 | `slippage_bps` 파라미터 (default 0.0) | 미지원 | 실제 거래량/호가 기반 |
| 증권거래세 (transaction tax) | 미적용 | 미적용 | 미적용 | 실전은 적용 필요 |
| 부분체결 모델링 | 실제 체결 | NOT-IMPL | NOT-IMPL | LOB 기반 |
| 최대 포지션 비중 제한 | NOT-IMPL | `max_position_weight` 파라미터 | NOT-IMPL | — |
| 일일 주문 금액 한도 | `max_daily_amount` (SafetyChecker) | `max_daily_amount` | `max_daily_amount` | — |
| 단일 주문 금액 한도 | `max_order_amount` | `max_order_amount` | `max_order_amount` | — |

**주의**: 백테스트·모의에서 `fee_rate=0.0`, `slippage_bps=0.0` 기본값은 over-optimistic 결과를 낸다.
보고서에 "Zero-fee, zero-slippage assumption" 경고를 포함해야 한다 (TASK-039 범위).

---

## 6. Data Source

| Data Type | KIS API TR | Mock Source | Supported? | Notes |
|-----------|-----------|-------------|------------|-------|
| 현재가 (spot price) | `FHKST01010100` | `mock_client.prices` dict | `SUPPORTED` | |
| 복수 종목 현재가 | `FHKST11300006` | 개별 조회 반복 | `SUPPORTED` | TASK-013 |
| 분봉 (intraday OHLCV) | `FHKST03010200` | NOT-IMPL | `SUPPORTED` (KIS) / `NOT-IMPL` (mock) | TASK-011 |
| 일봉 차트 (daily OHLCV) | `FHKST03010100` | NOT-IMPL | `SUPPORTED` (KIS) / `NOT-IMPL` (mock) | |
| 지수 (KOSPI/KOSDAQ/KOSPI200) | `FHPUP02100000` | NOT-IMPL | `SUPPORTED` (KIS) | TASK-015 |
| 업종 시세 | `FHKST01010100` (업종별) | NOT-IMPL | `SUPPORTED` (KIS) | TASK-019 |
| 기업 재무정보 (PER/PBR/EPS) | `FHPST01750000` | NOT-IMPL | `SUPPORTED` (KIS) | TASK-016 |
| 배당 정보 | `HHKDB669102C0` | NOT-IMPL | `SUPPORTED` (KIS) | TASK-017 |
| 호가창 10단계 | `FHKST01010200` | NOT-IMPL | `SUPPORTED` (KIS) | TASK-018 |
| 공시 정보 | `FHKST01011800` | NOT-IMPL | `SUPPORTED` (KIS) | TASK-020 |
| WebSocket 실시간 (현재가/호가/체결) | KIS ws | NOT-IMPL | `SUPPORTED` (KIS) | TASK-010 |
| 잔고/포지션 | `TTTC8434R` | `mock_client._positions` | `SUPPORTED` | |
| 주문 내역 (단기 ≤3개월) | `TTTC0081R` | NOT-IMPL | `SUPPORTED` (KIS) | TASK-012 |
| 주문 내역 (장기 >3개월) | `CTSC9215R` | NOT-IMPL | `SUPPORTED` (KIS) | TASK-012 |
| 해외 시세/외환 | 해외주식 별도 TR | NOT-IMPL | `R3-HOLD` | TASK-022 |
| 신용/공매도 잔고 | 별도 TR | NOT-IMPL | `R3-HOLD` | TASK-021 |

---

## 7. Alert / Backtest Feature Flags

| Feature | Current State | Autofolio Status | Blocking Task |
|---------|---------------|------------------|---------------|
| 조건부 자동 주문 (condition engine) | `condition_evaluator.py` + `order_flow.py` | `SUPPORTED` | — |
| 알림 탭 (UI) | `web/src/app/alerts/page.tsx` | `SUPPORTED` | — |
| Telegram 알림 발송 | Notifier (approved outbound) | `SUPPORTED` | — |
| 가격 경보 규칙 확장 | 현재 기본 조건만 | `NOT-IMPL` | TASK-038 |
| 저장 스크리너/워치리스트 | 없음 | `NOT-IMPL` | TASK-038 |
| 백테스트 전략 보고서 | 기본 틀 있음 | `NOT-IMPL` (보고 thin) | TASK-039 |
| 슬리피지/수수료 가정 명시 | 없음 | `NOT-IMPL` | TASK-039 |
| 포트폴리오 성과 attribution | `web/src/app/analysis/page.tsx` + `app/services/perf_report.py` | `SUPPORTED` | TASK-040 |
| 세금 lot 스타일 보고 | 없음 | `NOT-IMPL` | TASK-040 |
| Discord 알림 | incoming webhook approved | `CONDITIONAL` | TASK-043 |
| Notion 리포트 쓰기 | selected DB 조건부 | `CONDITIONAL` | TASK-043/044 |
| Google Sheets 리포트 | 조건부 (특정 sheet만) | `CONDITIONAL` | TASK-043/044 |
| Telegram `/kill` 명령 | safety-direction 조건부 | `CONDITIONAL` | TASK-043/044 |
| Telegram 주문 명령 (`/approve` 등) | 기각 by default | `REJECTED` | — |
| Inbound webhook (임의 발신) | R3-hold | `R3-HOLD` | — |
| 고급 차트 드로잉 알림 | NOT-IMPL | `R3-HOLD` | — |

---

## 8. External Connector / API Permission Classes

근거: `EXTERNAL-APP-API-DECISION-RECORD.md`.

| Capability Class | Default Status | Autofolio Exposed? | Notes |
|-----------------|----------------|--------------------|-------|
| Outbound notification | approved | YES | Telegram/Discord/Email/Notion/Sheets 알림 |
| Read-only command | approved | YES (`/status`, `/pnl`, `/positions`) | allowlist 필수 |
| Safety-direction command (`/kill`) | conditional | CONDITIONAL | audit path 필요 |
| State-changing automation command | r3-hold | NO | `/approve`, auto-mode toggle 등 |
| Broker order/cancel via channel | rejected | NO | 채널 연동으로는 절대 불가 |
| Report export/write | conditional | CONDITIONAL | least-privilege scope 및 명시적 destination |
| OAuth social login (minimal scope) | conditional | CONDITIONAL | Google/Kakao/Naver profile/email만 |
| OAuth private data read/write | r3-hold | NO | Gmail/Drive/workspace admin 등 |
| Public social posting | r3-hold | NO | X, Discord public, Slack workspace |
| Inbound webhook | r3-hold | NO | signature/replay 검증 전까지 |
| Scraping/unofficial API | rejected | NO | — |
| Mass messaging/marketing | rejected | NO | — |

**앱별 현재 상태 요약**:

| App | Approved Today | Conditional (구현 전 Owner 확인) | R3 / Rejected |
|-----|----------------|----------------------------------|---------------|
| Telegram | outbound alerts, `/status` read-only | `/kill` with allowlist | `/approve`, order, broadcast |
| Discord | incoming webhook alerts | bot/slash owner server | state-changing, private reads |
| Google Sheets | — | portfolio mirror (specific sheet) | broad Drive access |
| Google Calendar | — | owner reminders | broad write, background mutation |
| Gmail | — | outbound reports (minimal send) | read/modify scopes |
| KakaoTalk | — | "send to me" notification | AlimTalk, friend messaging |
| Notion | — | selected DB journal write | workspace-wide sync |
| Slack | — | incoming webhook | bot, private channel |
| X (Twitter) | — | read-only monitoring (if paid) | posting, DM, scraping |
| Naver | — | social login, Papago helper | Naver Works, unofficial |

---

## 9. Margin / Short / Advanced Account Types

| Feature | KIS Support | Autofolio Engine | Blocking Task |
|---------|-------------|------------------|---------------|
| 신용 매수 (margin buy) | 별도 SLL_TYPE | `R3-HOLD` | TASK-021 |
| 공매도 (short sale) | 별도 SLL_TYPE | `R3-HOLD` | TASK-021 |
| 공매도 uptick rule | 규정 적용 | `R3-HOLD` | TASK-021 |
| 해외주식 현지화 주문 | 해외 TR | `R3-HOLD` | TASK-022 |
| FX 자동 환전 | NOT-IMPL | `REJECTED` | — (manual only) |

---

## 10. Market Microstructure / Safety

| Feature | Implementation | Autofolio Status |
|---------|---------------|------------------|
| KRX 호가단위 (tick size) | `_tick_size()` in `kis_client.py` | `SUPPORTED` |
| 거래 정지 / VI / 서킷브레이커 감지 | NOT-IMPL | `R3-HOLD` (TASK-031) |
| 정지 후 재개 시간 추적 | NOT-IMPL | `R3-HOLD` (TASK-031) |
| 데이터 품질 (OHLCV 결측 / 분할) | validator 있음; order-flow hook 없음 | `R3-HOLD` (TASK-032) |
| 배치 조회 최대 심볼 수 (`_MAX_MULTPRICE_SYMBOLS`) | 30 | `SUPPORTED` |
| Rate-limit 재시도 (`EGW00201`) | `_DEFAULT_MAX_RETRIES=2` | `SUPPORTED` |
| 중복 주문 방지 (duplicate guard) | `app/risk/duplicate_guard.py` | `SUPPORTED` |
| 자율도 레벨 (L0/L1/L2+) | `SafetyChecker` symbol_mode | `SUPPORTED` |

---

## 11. Reference Platform Comparison

Autofolio vs 주요 참조 플랫폼 고수준 비교.

| Dimension | KIS OpenAPI (공식) | 키움증권 HTS | Interactive Brokers | Backtrader / Zipline | Autofolio v현재 |
|-----------|--------------------|-------------|--------------------|-----------------------|----------------|
| 지원 자산 | KRX 주식/ETF/선물/옵션 | KRX+해외 | 글로벌 다자산 | 시뮬레이션 전용 | 국내 주식/ETF (SUPPORTED); 나머지 R3/조건부 |
| 주문 유형 | 지정가, 시장가, 시간외, IOC 등 | 광범위 | 광범위 (40+) | limit/market | limit/market only |
| 세션 | 정규장 + 시간외 | 정규장 + 시간외 | 24h/pre-after | 정규장 가정 | 정규장 (09:10–15:20) only |
| 실시간 데이터 | WebSocket (체결/호가/현재가) | DDE/SDK | TWS API | NOT-IMPL | WebSocket (TASK-010) |
| 백테스트 | NOT-IMPL | NOT-IMPL | NOT-IMPL | 핵심 기능 | 기초 패턴만 |
| 수수료 모델 | 실제 요율 | 실제 요율 | Tiered/Fixed | 설정 가능 | 파라미터 (default=0) |
| 포트폴리오 성과 | 기본 | 기본 | 상세 | 상세 | 기초 (TASK-040 확장 예정) |
| 외부 알림 | NOT-IMPL | NOT-IMPL | NOT-IMPL | NOT-IMPL | Telegram/Discord 승인 |
| 해외주식 | SUPPORTED (별도 TR) | SUPPORTED | SUPPORTED | 데이터 소스 의존 | R3-HOLD (TASK-022) |

---

## 12. UI Exposure Rules (요약)

UI 또는 전략 코드가 지원 상태별로 지켜야 할 규칙:

| Rule | 적용 대상 |
|------|---------|
| `SUPPORTED` 기능만 실행 버튼/조건을 노출한다 | 주문 제출, 자동 실행, 실시간 데이터 구독 |
| `CONDITIONAL` 자산은 read-only/manual 라벨과 함께만 표시한다 | 해외주식, 코인, 금/은/오일 |
| `R3-HOLD` 기능은 UI에서 비활성화(grayed out) 또는 노출 금지 | 시간외 주문, 신용/공매도, 해외주문, 고급 주문 |
| `REJECTED` 자산/기능은 UI에서 완전 숨김 또는 교육 텍스트만 | 레버리지/인버스 ETP, DeFi, 실물 원자재 |
| `CONDITIONAL` 외부 커넥터는 scope/destination/auth 명시 후에만 활성화 | Discord, Sheets, Calendar, Notion |
| `R3-HOLD` 커넥터는 연결 카드 자체를 "R3 / 미지원" 배지로만 표시 | inbound webhook, 주문 채널 명령 |

---

## 13. Task Cross-Reference

이 매트릭스와 연결된 태스크:

| Task | 상태 | 대상 기능 |
|------|------|---------|
| TASK-014 | R3-보류 | 시간외 주문 (장전·장후 단일가) |
| TASK-021 | R3-보류 | 신용/공매도 주문 (SLL_TYPE) |
| TASK-022 | R3-보류 | 해외주식 주문 |
| TASK-026 | R3-보류 | KRX alternative products (ELW, ETN 고급) |
| TASK-027 | R3-보류 | KRX derivatives (선물/옵션) |
| TASK-028 | R3-보류 | Advanced order types (Stop, IOC, OCO 등) |
| TASK-030 | R3-보류 | Block/Basket execution |
| TASK-031 | R3-보류 | Market halt / VI / circuit breaker 감지 |
| TASK-032 | R3-보류 | Data quality / corporate actions order-flow hook |
| TASK-038 | 대기 | 스크리너/워치리스트/알림 규칙 확장 |
| TASK-039 | 대기 | 백테스트/리서치 리포트 수수료·슬리피지 가정 |
| TASK-040 | 대기 | 포트폴리오 성과/세금-lot 보고 |
| TASK-042 | 완료 | Asset Universe Decision Record (이 매트릭스 입력) |
| TASK-043 | 완료 | External App/API Decision Record (이 매트릭스 입력) |

---

## Evidence

- `agents/qa/test_cases/ASSET-UNIVERSE-DECISION-RECORD.md` — asset class 승인/기각 근거
- `agents/qa/test_cases/EXTERNAL-APP-API-DECISION-RECORD.md` — 커넥터/API 권한 클래스 근거
- `agents/qa/test_cases/FEATURE-LANDSCAPE-CATALOG.md` — feature family 분류 근거
- `app/brokers/base.py` — BrokerClient Protocol (지원 메서드 목록)
- `app/brokers/kis/kis_client.py` — KIS TR ID, endpoint, session 상수
- `app/brokers/mock/mock_client.py` — fee_rate, slippage_bps, fill model
- `app/common/enums.py` — OrderType(LIMIT/MARKET), Side, OrderStatus
- `app/risk/safety_checker.py` — 거래 윈도우, kill switch, 서킷브레이커
- `app/risk/trading_window.py` — 09:10–15:20 KST window
- `tests/integration/test_capability_matrix.py` — 매트릭스 존재 + 필수 섹션 검증
