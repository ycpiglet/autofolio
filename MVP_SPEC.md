# Autofolio 명세서 초안 (KIS 기반 개인용 국장 자동매매)

버전: `v0.1-draft`  
작성 목적: 한국투자증권 Open API를 활용한 개인용 국장 자동매매 MVP의 요구사항, 기술 설계, 안전정책, 개발 로드맵을 정리한다.  
주의: 본 문서는 소프트웨어 개발 명세서이며, 투자 권유나 수익 보장을 의미하지 않는다.

---

## 1. 프로젝트 개요

### 1.1 프로젝트명

**Autofolio** (KIS 기반 개인용 국장 자동매매)

영문 표기:

**Autofolio**

### 1.2 핵심 목표

한국투자증권 Open API를 이용해 국장 ETF 및 대형주 중심의 화이트리스트 종목을 대상으로, 사용자가 설정한 목표 가격에 도달하면 기본 안전조건을 통과한 경우 소액 자동주문을 실행하고, Streamlit UI와 SQLite 로그를 통해 관제할 수 있는 개인용 자동매매 시스템을 만든다.

### 1.3 장기 비전

본 MVP는 최종적으로 다음과 같은 확장형 시스템으로 발전시키는 것을 목표로 한다.

```text
개인 투자 철학
→ 가드레일
→ 리서치 에이전트
→ 조건 제안
→ 백테스트
→ 반자동/자동 매매
→ 로그 기반 회고
→ 제한적 자가개선
```

최종 지향점은 단순 자동매매 봇이 아니라, **Agentic Quant Portfolio OS**, 즉 **에이전트 기반 개인 투자 운용체계**다.

---

## 2. 목표와 비목표

### 2.1 MVP 목표

MVP에서 반드시 달성해야 하는 목표는 다음과 같다.

1. 한국투자증권 Open API 인증 및 국장 현재가 조회.
2. 국장 ETF 및 대형주 화이트리스트 관리.
3. 종목별 역할 지정.
4. 목표 가격 기반 매수/매도 조건 설정.
5. REST polling 방식의 가격 감시.
6. 기본 안전조건 검사.
7. 소액 자동주문 실행.
8. 지정가 주문 기본 지원.
9. 제한적 시장가 주문 및 시장가 fallback 지원.
10. 미체결 주문 1분 후 취소.
11. 중복 주문 방지.
12. 주문, 체결, 취소, 오류 로그 저장.
13. Streamlit 기반 관제 UI 제공.
14. Telegram 알림 제공.
15. Kill Switch 제공.
16. 모의투자 검증 후 실전 1주 테스트.
17. 리서치 에이전트의 조건 제안 기능 제공. 단, 주문 권한은 없음.

### 2.2 MVP 비목표

다음 항목은 MVP 범위에서 제외하고 Future Roadmap에 보관한다.

1. 미장 자동매매.
2. 백테스트 엔진.
3. WebSocket 실시간 감시.
4. FastAPI + React 정식 웹앱.
5. PostgreSQL 기반 서버형 DB.
6. Docker 및 클라우드 상시 운영.
7. 신규상장주 자동매수.
8. 선물, 옵션 자동매매.
9. 채권, 펀드 통합.
10. 조건검색 기반 종목 자동 편입.
11. 뉴스/공시 실시간 분석.
12. 완전 자가개선 자동매매.
13. AI가 직접 주문을 실행하는 구조.

---

## 3. 핵심 결정사항 요약

| 항목 | 결정 |
|---|---|
| 증권사 API | 한국투자증권 Open API |
| 시장 | 국장 먼저, 미장 나중 |
| 실행 환경 | Windows 노트북 로컬 실행 |
| Python 환경 | Python venv |
| DB | SQLite |
| UI | Streamlit |
| 보안 | `.env` |
| 설정 관리 | `.env + SQLite + config` 혼합 구조 |
| 가격 감시 | REST polling, 기본 3초 주기 |
| 종목 제한 | 화이트리스트 방식 |
| 종목 역할 | 종목별 역할 지정 |
| 매매 조건 | 목표 가격 도달형 |
| 주문 권한 | 소액 자동주문 |
| 주문 방식 | 지정가 기본, 시장가 제한 허용 |
| 미체결 처리 | 1분 대기 후 취소 |
| 시장가 전환 | 조건 만족 시 fallback |
| 중복 방지 | 조건 1회 실행 + 쿨다운 + 보유수량 기준 |
| 자동매매 시간 | 09:10~15:20 기본, 정규장 전체 옵션 |
| 로그 | 표준 로그, 감사 로그 확장 가능 |
| 알림 | Streamlit + Telegram |
| Kill Switch | 자동매매 중단 + 미체결 주문 취소 |
| 테스트 | Unit Test + Mock API + 한투 모의투자 |
| 실전 전환 | 모의 핵심 시나리오 3회 이상 성공 후 실전 1주 |
| 리서치 에이전트 | 조건 제안 가능, 주문 권한 없음 |
| 백테스트 | MVP 제외, Future Roadmap |

---

## 4. 시스템 아키텍처

### 4.1 MVP 아키텍처

```text
Windows 노트북
└── Python venv
    ├── Streamlit UI
    ├── Trading Engine
    ├── Risk / Safety Checker
    ├── KIS Open API Client
    ├── SQLite DB
    ├── Telegram Notifier
    └── Research Agent
```

### 4.2 데이터 흐름

```text
사용자 조건 입력
↓
SQLite에 조건 저장
↓
REST 현재가 조회
↓
조건 평가
↓
안전조건 검사
↓
주문 실행
↓
체결/잔고 확인
↓
SQLite 로그 저장
↓
Streamlit 화면 갱신
↓
Telegram 알림
```

### 4.3 리서치 에이전트 흐름

```text
화이트리스트 종목 선택
↓
리서치 에이전트 분석
↓
목표 매수가 / 목표 매도가 제안
↓
근거 및 리스크 설명
↓
사용자 검토
↓
사용자 승인 시 조건으로 저장
↓
자동주문 기본 OFF
```

---

## 5. 프로젝트 구조 (2026-06-10 현행)

도메인 기반 구조. **신 멀티페이지 셸 = ** (구 는 레거시).

```text
autofolio/
├── app/
│   ├── brokers/
│   │   ├── kis/            # KIS Open API 클라이언트 (5메서드, paper/prod TR ID)
│   │   │   ├── kis_client.py
│   │   │   ├── kis_auth.py
│   │   │   └── kis_models.py
│   │   ├── mock/           # 테스트용 Mock 브로커
│   │   └── factory.py
│   ├── database/
│   │   ├── sqlite_db.py
│   │   ├── schema.sql
│   │   └── repositories.py  # 22+ 메서드 (whitelist/conditions/orders/execution/risk)
│   ├── engine/
│   │   ├── live_trading_engine.py  # 구조화 로깅, Notifier 연동
│   │   ├── order_flow.py    # _poll_fill 포함 PENDING 완전 처리
│   │   └── condition_evaluator.py
│   ├── risk/
│   │   ├── safety_checker.py  # 킬스위치·자동매매·화이트리스트·시간·한도·서킷브레이커
│   │   ├── duplicate_guard.py
│   │   └── trading_window.py
│   ├── agents/
│   │   └── research_agent.py  # IC 제안 생성
│   ├── notification/
│   │   ├── notifier.py        # 통합 Notifier (Telegram+로그 fallback)
│   │   ├── telegram_bot.py    # 명령봇 (/status /pnl /positions /conditions /engine /propose)
│   │   └── telegram_notifier.py  # 레거시
│   ├── ui/
│   │   ├── autofolio_app.py   # ★ 신 멀티페이지 셸 (8화면)
│   │   ├── streamlit_app.py   # 구 단일화면 (레거시·참조)
│   │   ├── backend.py         # UI ↔ 브로커/DB 어댑터 (30+ 함수)
│   │   ├── agents_runtime.py  # 40개 에이전트 Anthropic API 연결
│   │   ├── ic.py              # 투자위원회 워크플로
│   │   ├── views/             # 8화면 (home/portfolio/trade/history/analysis/alerts/settings/agents)
│   │   ├── components/        # ui.py (top_bar·서킷브레이커 배지)
│   │   └── mock/data.py       # 데모 데이터 (라이브 없을 때 폴백)
│   ├── config/
│   │   └── settings.py        # resolve_settings() — 환경별 KIS 자격증명 자동 해석
│   ├── quant/                 # 퀀트팀 (스캐폴딩)
│   └── common/
│       ├── enums.py
│       ├── errors.py
│       └── logger.py          # get_structured_logger / log_event → logs/events.jsonl
├── agents/                    # 40개 에이전트 SKILL.md (개발·자산·퀀트·거버넌스)
│   ├── roles.yml
│   └── <role>/SKILL.md
├── tests/
│   ├── unit/                  # 128 tests
│   └── integration/
├── scripts/                   # 스크립트 30+
│   ├── auto_merge.py          # 자율 PR 머지 게이트
│   ├── run_paper_engine.py    # 모의투자 스케줄러
│   ├── run_retro.py           # 회고 워크플로
│   ├── run_daily_summary.py   # 일일 요약
│   └── tail_events.py         # events.jsonl 모니터링
├── docs/                      # 기획서·스펙·런북
│   ├── PRODUCT_BLUEPRINT.md
│   ├── KIS_API_SPEC.md
│   └── BACKLOG.md
├── .github/workflows/test.yml # CI (pytest + check_agent_docs)
├── .env                       # 시크릿 (gitignore)
└── agent_runtime.yml          # framework v0.1.8 pin
```

---

## 6. 핵심 모듈 책임

### 6.1 `brokers/kis`

한국투자증권 Open API와 직접 통신한다.

책임:

1. 인증 토큰 발급.
2. 현재가 조회.
3. 계좌 잔고 조회.
4. 주문 요청.
5. 주문 취소.
6. 체결 결과 조회.
7. 모의투자/실전 환경 전환.

금지:

1. 투자 판단.
2. 조건 평가.
3. 리스크 판단.
4. UI 로직.

### 6.2 `engine`

자동매매의 실행 흐름을 관리한다.

책임:

1. 감시 대상 조건 로드.
2. 현재가 조회 요청.
3. 조건 충족 여부 판단.
4. 안전조건 검사 요청.
5. 주문 흐름 실행.
6. 로그 저장 요청.
7. 상태 업데이트.

### 6.3 `risk`

안전조건을 검사한다.

책임:

1. 화이트리스트 여부 확인.
2. 자동매매 시간 확인.
3. 주문 한도 확인.
4. 조건 실행 여부 확인.
5. 쿨다운 확인.
6. 보유수량 기준 중복 매수 방지.
7. 미체결 주문 존재 여부 확인.
8. 시장가 전환 가능 여부 확인.

### 6.4 `database`

SQLite 저장소를 관리한다.

책임:

1. 화이트리스트 저장.
2. 매매 조건 저장.
3. 주문 로그 저장.
4. 체결 로그 저장.
5. 시스템 상태 저장.
6. 쿨다운 상태 저장.
7. 자동매매 ON/OFF 상태 저장.

### 6.5 `ui`

Streamlit 기반 관제 UI를 제공한다.

책임:

1. 화이트리스트 관리.
2. 조건 설정.
3. 자동매매 ON/OFF.
4. 현재가 표시.
5. 주문 로그 표시.
6. 보유 포지션 표시.
7. Kill Switch 버튼.
8. 리서치 에이전트 제안 검토.

### 6.6 `agents`

리서치 에이전트 기능을 담당한다.

책임:

1. 화이트리스트 종목에 대한 조건 제안.
2. 목표 매수가/매도가 제안.
3. 제안 근거 설명.
4. 리스크 코멘트 제공.

금지:

1. 조건 자동 저장.
2. 자동주문 ON.
3. 직접 주문 실행.
4. 비화이트리스트 종목 자동 편입.
5. 실전 주문 권한 보유.

---

## 7. 매매 조건 정책

### 7.1 조건 유형

MVP에서는 **목표 가격 도달형 조건**만 지원한다.

매수 조건:

```text
현재가 <= 목표 매수가
```

매도 조건:

```text
현재가 >= 목표 매도가
```

### 7.2 예시

```text
종목: 삼성전자
종목코드: 005930
역할: LARGE_CAP_TEST
매수 목표가: 70,000원
매도 목표가: 76,000원
수량: 1주
주문 방식: LIMIT
자동주문: OFF 기본
```

---

## 8. 주문 정책

### 8.1 주문 방식

MVP에서 지원하는 주문 방식은 다음과 같다.

1. 지정가 주문.
2. 시장가 주문.

기본값은 지정가 주문이다.

```text
기본 주문 방식 = LIMIT
시장가 주문 = 명시적으로 허용된 경우에만 가능
```

### 8.2 지정가 주문

매수 조건 충족 시:

```text
현재가 <= 목표 매수가
→ 목표 매수가로 지정가 매수
```

매도 조건 충족 시:

```text
현재가 >= 목표 매도가
→ 목표 매도가로 지정가 매도
```

### 8.3 시장가 주문

시장가 주문은 다음 조건을 만족할 때만 허용한다.

1. 화이트리스트 종목.
2. 수량 1주 또는 소액 주문.
3. ETF_TEST 또는 LARGE_CAP_TEST 역할.
4. 장 시작 직후 10분 금지.
5. 장 마감 전 10분 금지.
6. 하루 시장가 주문 횟수 제한.
7. 동일 종목 1일 1회 제한.
8. 호가 스프레드가 과도하지 않음.
9. 사용자가 해당 조건에서 시장가 허용을 켠 경우.

---

## 9. 미체결 처리 정책

### 9.1 지정가 미체결 처리

```text
지정가 주문 제출
→ 1분 대기
→ 미체결이면 주문 취소
→ 시장가 전환 조건 확인
→ 조건 만족 시 시장가 주문
→ 조건 불만족 시 종료 및 로그 저장
```

### 9.2 시장가 fallback

시장가 fallback은 무조건 실행되지 않는다.  
다음 조건을 통과해야 한다.

1. 취소 요청 성공.
2. 미체결 주문이 남아 있지 않음.
3. 시장가 주문 허용 조건 통과.
4. 자동매매 시간 조건 통과.
5. 하루 주문 한도 초과 아님.
6. Kill Switch 상태 아님.

---

## 10. 안전정책

### 10.1 화이트리스트

자동주문은 화이트리스트 종목에 대해서만 가능하다.

초기 화이트리스트 예시:

```text
KODEX 200 → ETF_TEST
삼성전자 → LARGE_CAP_TEST
TIGER 미국S&P500 → LONG_TERM_CANDIDATE
```

단, 실제 종목 코드는 구현 시점에 확인한다.

### 10.2 종목별 역할

MVP에서 사용하는 역할은 다음과 같다.

| 역할 | 의미 |
|---|---|
| `ETF_TEST` | ETF 주문 파이프라인 테스트 |
| `LARGE_CAP_TEST` | 개별 대형주 주문 테스트 |
| `LONG_TERM_CANDIDATE` | 장기 적립/리밸런싱 후보 |

### 10.3 주문 한도

초기 정책:

```text
기본 1회 자동주문 한도: 100,000원
기본 1일 자동주문 한도: 300,000원
기본 주문 수량: 1주
```

단, 1주 가격이 기본 한도를 초과하는 화이트리스트 대형주는 1주 테스트 예외를 둘 수 있다.

1주 테스트 예외 조건:

1. 화이트리스트 종목.
2. ETF 또는 대형주.
3. 종목별 1일 1회.
4. 전체 1일 1~2회 이내.
5. 지정가 우선.

### 10.4 자동매매 시간

기본 허용 시간:

```text
09:10 ~ 15:20
```

옵션:

```text
09:00 ~ 15:30 정규장 전체 허용 가능
```

금지:

1. 장전 거래.
2. 장후 거래.
3. 시간외 거래.
4. 장 시작 직후 10분.
5. 장 마감 전 10분.

### 10.5 중복 주문 방지

MVP에서는 다음 정책을 사용한다.

1. 조건 1개는 기본적으로 1회만 실행.
2. 실행 후 `condition_status = TRIGGERED`.
3. 사용자가 다시 활성화하기 전까지 재실행 금지.
4. 같은 종목은 주문 후 기본 30분 쿨다운.
5. 이미 목표 수량을 보유하면 추가 매수 금지.
6. 미체결 주문이 남아 있으면 새 주문 금지.

### 10.6 자동주문 기본 상태

```text
자동주문 기본값 = OFF
사용자가 UI에서 명시적으로 ON
Kill Switch 실행 시 자동으로 OFF
프로그램 재시작 시 기본 OFF
```

---

## 11. Kill Switch 정책

### 11.1 MVP Kill Switch

MVP에서 Kill Switch는 다음을 수행한다.

```text
1. auto_trading_enabled = false
2. 신규 조건 감시 중단
3. 신규 주문 생성 금지
4. 미체결 주문 조회
5. 미체결 주문 취소 요청
6. 취소 결과 확인
7. 로그 저장
8. UI에 긴급정지 상태 표시
9. Telegram 알림 전송
```

### 11.2 금지사항

MVP Kill Switch는 보유 종목을 자동으로 전량 매도하지 않는다.

```text
긴급정지 ≠ 전량 매도
긴급정지 = 시스템의 신규 행동을 멈추는 것
```

### 11.3 Future Roadmap

향후 단계별 Kill Switch를 지원한다.

| 단계 | 기능 |
|---|---|
| Level 1 | 신규 주문 중단 |
| Level 2 | 신규 주문 중단 + 미체결 취소 |
| Level 3 | 특정 종목 자동매매 중단 |
| Level 4 | 특정 전략 중단 |
| Level 5 | 보유 포지션 청산 후보 생성 |
| Level 6 | 강제 전량 청산. 별도 승인 필요 |

---

## 12. 에러 처리 정책

에러는 등급별로 처리한다.

| 에러 종류 | 처리 |
|---|---|
| 현재가 조회 실패 | 최대 3회 재시도 후 해당 종목 감시 정지 |
| 조건 평가 오류 | 해당 조건 비활성화 |
| 주문 요청 실패 | 자동 재주문 금지, 조건 비활성화 |
| 미체결 취소 실패 | 전체 자동매매 정지 |
| 체결 확인 실패 | 전체 자동매매 정지 |
| 잔고 조회 실패 | 전체 자동매매 정지 |
| 인증 실패 | 전체 자동매매 정지 |
| API 제한 초과 | 일정 시간 대기, 반복 시 자동매매 정지 |
| Kill Switch 실패 | 즉시 경고, 수동 계좌 확인 필요 |

핵심 원칙:

```text
조회 실패는 재시도 가능.
주문 실패는 자동 재주문 금지.
계좌/체결 확인 실패는 전체 정지.
인증 실패는 전체 정지.
```

---

## 13. 로그 정책

### 13.1 MVP 표준 로그

MVP에서 반드시 저장할 로그 항목은 다음과 같다.

```text
조건 ID
종목 코드
종목명
현재가
목표가
매수/매도 구분
주문 방식
주문 수량
주문 요청 시간
주문번호
체결 여부
체결가
체결 수량
미체결 여부
취소 여부
시장가 전환 여부
잔고 반영 여부
에러 메시지
```

### 13.2 Future 감사 로그

향후 다음 항목을 확장한다.

1. API 요청/응답 원문.
2. 호가 정보.
3. 조건 평가 전체 이력.
4. 리스크 체크 상세 결과.
5. 사용자 버튼 클릭 기록.
6. 주문 취소/정정 전체 이력.
7. WebSocket 체결 이벤트.
8. LLM 에이전트 판단 근거.
9. 백테스트 결과와 실거래 비교.

---

## 14. 알림 정책

### 14.1 MVP 알림 채널

MVP에서는 다음 알림 채널을 사용한다.

```text
기본 관제: Streamlit
실시간 알림: Telegram
```

### 14.2 알림 이벤트

Telegram 알림은 다음 이벤트에 대해서만 보낸다.

1. 조건 충족.
2. 주문 요청.
3. 주문 성공.
4. 체결 완료.
5. 주문 실패.
6. 미체결 취소.
7. 시장가 전환.
8. Kill Switch 실행.
9. API 오류.
10. 자동매매 정지.

### 14.3 알림 등급

| 등급 | 이벤트 |
|---|---|
| INFO | 조건 충족, 주문 실행, 체결 완료 |
| WARNING | 미체결 취소, 시장가 전환, 가격 조회 반복 실패 |
| ERROR | 주문 실패, 체결 확인 실패, 잔고 조회 실패, 인증 실패, Kill Switch 실행 |

---

## 15. 설정 관리

### 15.1 `.env`

비밀값과 계좌/API 정보를 저장한다.

예시:

```env
KIS_ENV=paper
KIS_APP_KEY=
KIS_APP_SECRET=
KIS_ACCOUNT_NO=
KIS_ACCOUNT_PRODUCT_CODE=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

주의:

1. `.env`는 절대 Git에 commit하지 않는다.
2. `.env.example`만 commit한다.
3. 실전 키와 모의투자 키는 분리한다.
4. 키 유출 의심 시 즉시 폐기/재발급한다.

### 15.2 `config.py` 또는 `config.yaml`

시스템 기본값을 관리한다.

예시:

```python
DEFAULT_POLL_INTERVAL_SEC = 3
DEFAULT_ORDER_TIMEOUT_SEC = 60
DEFAULT_COOLDOWN_MIN = 30
DEFAULT_TRADING_START = "09:10"
DEFAULT_TRADING_END = "15:20"
```

### 15.3 SQLite

사용자가 UI에서 변경하는 운용 설정을 저장한다.

예:

1. 화이트리스트 종목.
2. 매매 조건.
3. 주문 한도.
4. 자동매매 ON/OFF.
5. 조건 실행 상태.
6. 쿨다운 상태.

---

## 16. 데이터베이스 설계 초안

### 16.1 `whitelist_symbols`

화이트리스트 종목을 저장한다.

| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | INTEGER PK | 내부 ID |
| symbol | TEXT | 종목 코드 |
| name | TEXT | 종목명 |
| market | TEXT | 시장. 예: KRX |
| role | TEXT | ETF_TEST, LARGE_CAP_TEST 등 |
| enabled | INTEGER | 활성 여부 |
| created_at | TEXT | 생성 시각 |
| updated_at | TEXT | 수정 시각 |

### 16.2 `trade_conditions`

매매 조건을 저장한다.

| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | INTEGER PK | 조건 ID |
| symbol | TEXT | 종목 코드 |
| side | TEXT | BUY 또는 SELL |
| target_price | REAL | 목표 가격 |
| quantity | INTEGER | 주문 수량 |
| order_type | TEXT | LIMIT 또는 MARKET |
| allow_market_fallback | INTEGER | 시장가 전환 허용 |
| auto_enabled | INTEGER | 자동주문 활성 여부 |
| status | TEXT | ACTIVE, TRIGGERED, DISABLED, ERROR |
| cooldown_until | TEXT | 쿨다운 종료 시각 |
| created_by | TEXT | USER 또는 AGENT |
| rationale | TEXT | 조건 설정 근거 |
| risk_note | TEXT | 리스크 설명 |
| created_at | TEXT | 생성 시각 |
| updated_at | TEXT | 수정 시각 |

### 16.3 `order_logs`

주문 로그를 저장한다.

| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | INTEGER PK | 로그 ID |
| condition_id | INTEGER | 조건 ID |
| symbol | TEXT | 종목 코드 |
| side | TEXT | BUY 또는 SELL |
| order_type | TEXT | LIMIT 또는 MARKET |
| order_price | REAL | 주문 가격 |
| current_price | REAL | 조건 발동 당시 현재가 |
| quantity | INTEGER | 주문 수량 |
| kis_order_id | TEXT | 한투 주문번호 |
| order_status | TEXT | REQUESTED, FILLED, CANCELED, FAILED |
| fallback_to_market | INTEGER | 시장가 전환 여부 |
| error_message | TEXT | 오류 메시지 |
| created_at | TEXT | 생성 시각 |

### 16.4 `execution_logs`

체결 로그를 저장한다.

| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | INTEGER PK | 체결 로그 ID |
| order_log_id | INTEGER | 주문 로그 ID |
| symbol | TEXT | 종목 코드 |
| filled_price | REAL | 체결가 |
| filled_quantity | INTEGER | 체결 수량 |
| filled_at | TEXT | 체결 시각 |
| raw_status | TEXT | 원본 상태 요약 |

### 16.5 `system_state`

시스템 상태를 저장한다.

| 컬럼 | 타입 | 설명 |
|---|---|---|
| key | TEXT PK | 상태 키 |
| value | TEXT | 상태 값 |
| updated_at | TEXT | 수정 시각 |

예시:

```text
auto_trading_enabled = false
kill_switch_active = false
kis_env = paper
```

### 16.6 `risk_limits`

주문 한도를 저장한다.

| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | INTEGER PK | 내부 ID |
| scope | TEXT | GLOBAL, SYMBOL |
| symbol | TEXT | 종목 코드. GLOBAL이면 null 가능 |
| max_order_amount | REAL | 1회 주문 한도 |
| max_daily_amount | REAL | 1일 주문 한도 |
| max_daily_market_orders | INTEGER | 일일 시장가 주문 횟수 제한 |
| allow_one_share_exception | INTEGER | 1주 예외 허용 |
| updated_at | TEXT | 수정 시각 |

---

## 17. Streamlit UI 초안

### 17.1 화면 구성

1. Overview.
2. Whitelist.
3. Conditions.
4. Live Monitor.
5. Orders.
6. Positions.
7. Research Agent.
8. Settings.
9. Kill Switch.

### 17.2 Overview

표시 항목:

1. 현재 환경: 모의투자/실전.
2. 자동매매 ON/OFF.
3. Kill Switch 상태.
4. 오늘 주문 수.
5. 오늘 자동주문 금액.
6. 최근 오류.
7. Telegram 알림 상태.

### 17.3 Whitelist

기능:

1. 종목 코드 추가.
2. 종목명 입력/조회.
3. 역할 지정.
4. 활성/비활성 전환.
5. 자동주문 허용 여부 확인.

### 17.4 Conditions

기능:

1. 종목 선택.
2. 매수/매도 선택.
3. 목표 가격 입력.
4. 수량 입력.
5. 주문 방식 선택.
6. 시장가 fallback 허용 여부 선택.
7. 자동주문 ON/OFF.
8. 조건 저장.
9. 조건 재활성화.

### 17.5 Live Monitor

기능:

1. 화이트리스트 현재가 표시.
2. 목표가 대비 거리 표시.
3. 조건 상태 표시.
4. 쿨다운 상태 표시.
5. 최근 조건 발동 이력 표시.

### 17.6 Orders

기능:

1. 주문 로그 조회.
2. 체결 여부 조회.
3. 미체결/취소/실패 상태 표시.
4. 시장가 전환 여부 표시.
5. 오류 메시지 표시.

### 17.7 Positions

기능:

1. 계좌 잔고 조회.
2. 보유 종목 표시.
3. 보유 수량 표시.
4. 평균단가 표시.
5. 평가금액 표시.

### 17.8 Research Agent

기능:

1. 화이트리스트 종목 선택.
2. 목표 매수가/매도가 제안 요청.
3. 제안 근거 확인.
4. 리스크 코멘트 확인.
5. 사용자 승인 시 조건으로 저장.
6. 저장된 조건은 자동주문 OFF 기본.

### 17.9 Settings

기능:

1. REST 조회 주기 확인.
2. 미체결 대기 시간 확인.
3. 쿨다운 기본값 확인.
4. 자동매매 시간 설정.
5. 주문 한도 설정.
6. Telegram 알림 설정 확인.

### 17.10 Kill Switch

기능:

1. 긴급정지 버튼.
2. 자동매매 OFF.
3. 미체결 주문 취소.
4. 취소 결과 표시.
5. Telegram 알림 발송.

---

## 18. 리서치 에이전트 정책

### 18.1 허용 기능

MVP에서 리서치 에이전트는 다음을 할 수 있다.

1. 화이트리스트 종목에 대한 요약 제공.
2. 목표 매수가 제안.
3. 목표 매도가 제안.
4. 수량 제안.
5. 주문 방식 제안.
6. 근거 설명.
7. 리스크 설명.

### 18.2 금지 기능

리서치 에이전트는 다음을 할 수 없다.

1. 비화이트리스트 종목 자동 추천 및 편입.
2. 조건 자동 저장.
3. 자동주문 ON.
4. 실전 주문 실행.
5. 리스크 한도 변경.
6. Kill Switch 해제.
7. 사용자의 승인 없이 운용 설정 변경.

### 18.3 제안 저장 정책

```text
에이전트 제안
→ 사용자 검토
→ 사용자 승인
→ trade_conditions에 저장
→ auto_enabled = false
```

---

## 19. 테스트 전략

### 19.1 테스트 계층

```text
Level 1. 단위 테스트
Level 2. Mock API 통합 테스트
Level 3. 한투 모의투자 API 테스트
Level 4. 실전 1주 테스트
Level 5. 실전 소액 자동매매
```

### 19.2 단위 테스트 대상

1. 가격 조건 판단.
2. 거래 시간 검사.
3. 화이트리스트 검사.
4. 중복 주문 방지.
5. 쿨다운 검사.
6. 주문 한도 검사.
7. 조건 실행 상태 검사.
8. 시장가 fallback 가능 여부 검사.

### 19.3 Mock API 통합 테스트 대상

1. 현재가 조회.
2. 조건 충족.
3. 안전조건 통과.
4. 주문 요청.
5. 체결 확인.
6. 로그 저장.
7. UI 표시용 데이터 생성.
8. Telegram 알림 호출.

### 19.4 모의투자 검증 기준

실전 1주 테스트 전 다음 항목을 검증한다.

1. 지정가 매수 성공 3회 이상.
2. 지정가 매도 성공 3회 이상.
3. 미체결 주문 취소 성공 3회 이상.
4. 시장가 전환 성공 1회 이상.
5. 체결 결과 조회 성공.
6. 잔고 반영 확인.
7. SQLite 로그 저장 확인.
8. Streamlit 화면 반영 확인.
9. Telegram 알림 수신 확인.
10. Kill Switch 동작 확인.

### 19.5 실전 전환 기준

```text
모의투자 핵심 시나리오 3회 이상 성공
→ 실전 1주 수동 매수 버튼
→ 체결 / 잔고 / 로그 / UI / Telegram 확인
→ 실전 1주 수동 매도 버튼
→ 왕복 거래 검증
→ 조건 충족 + 사용자 승인 방식 3회 이상 성공
→ Kill Switch 확인
→ 사용자가 자동주문 ON
```

---

## 20. 개발 로드맵

### Phase 0. 환경 준비

목표:

1. Windows Python 개발환경 구축.
2. venv 생성.
3. `.env` 설정.
4. Git 저장소 생성.
5. `.gitignore` 설정.

산출물:

1. `requirements.txt`.
2. `.env.example`.
3. 기본 폴더 구조.

### Phase 1. 한투 API 연결

목표:

1. 한투 인증.
2. 토큰 발급.
3. 국장 현재가 조회.
4. 모의투자 환경 확인.
5. 계좌 조회.

산출물:

1. `kis_auth.py`.
2. `kis_client.py`.
3. `scripts/test_kis_price.py`.

### Phase 2. SQLite DB 구축

목표:

1. DB schema 작성.
2. 초기화 스크립트 작성.
3. 화이트리스트 저장.
4. 조건 저장.
5. 로그 저장.

산출물:

1. `schema.sql`.
2. `init_db.py`.
3. `repositories.py`.

### Phase 3. Streamlit 최소 UI

목표:

1. Overview 화면.
2. Whitelist 화면.
3. Conditions 화면.
4. Orders 화면.
5. Kill Switch 버튼.

산출물:

1. `streamlit_app.py`.

### Phase 4. 조건 평가 및 안전검사

목표:

1. 목표가 조건 평가.
2. 화이트리스트 검사.
3. 자동매매 시간 검사.
4. 중복 주문 방지.
5. 쿨다운 검사.
6. 주문 한도 검사.

산출물:

1. `condition_evaluator.py`.
2. `safety_checker.py`.
3. `duplicate_guard.py`.
4. 단위 테스트.

### Phase 5. Mock API 통합 테스트

목표:

1. 가짜 현재가 응답.
2. 가짜 주문 응답.
3. 가짜 체결 응답.
4. end-to-end 흐름 검증.

산출물:

1. `tests/integration/test_mock_order_flow.py`.

### Phase 6. 한투 모의투자 주문

목표:

1. 모의 지정가 매수.
2. 모의 지정가 매도.
3. 미체결 취소.
4. 시장가 fallback.
5. 체결/잔고 확인.
6. 로그 저장.

산출물:

1. `order_flow.py`.
2. 모의투자 검증 체크리스트.

### Phase 7. Telegram 알림

목표:

1. Telegram Bot 연동.
2. 주문/체결/오류 알림.
3. Kill Switch 알림.

산출물:

1. `telegram_notifier.py`.

### Phase 8. 리서치 에이전트 조건 제안

목표:

1. 화이트리스트 종목 기반 조건 제안.
2. 근거 및 리스크 설명.
3. 사용자 승인 후 조건 저장.
4. 자동주문 OFF 기본 적용.

산출물:

1. `research_agent.py`.
2. Research Agent UI 탭.

### Phase 9. 실전 1주 테스트

목표:

1. 실전 1주 수동 매수.
2. 실전 1주 수동 매도.
3. 로그/잔고/UI/알림 확인.
4. 주문 후보 + 승인 방식 3회 검증.
5. 자동주문 ON 조건 충족.

산출물:

1. 실전 전환 리포트.
2. 실전 1주 테스트 로그.

### Phase 10. 소액 자동주문 시작

목표:

1. 자동주문 명시적 ON.
2. 화이트리스트 조건 기반 소액 자동주문.
3. 일일 주문 한도 적용.
4. Kill Switch 검증.
5. 운영 회고.

산출물:

1. 첫 자동주문 운영 리포트.

---

## 21. Future Roadmap

### 21.1 시장 확장

1. 미장 자동매매.
2. 환율 반영.
3. 미국 주식/ETF 화이트리스트.
4. 미장 거래시간 정책.
5. 해외 브로커 API 또는 한투 해외주식 API 연동.

### 21.2 데이터/실시간성 확장

1. WebSocket 실시간 체결가 수신.
2. 실시간 호가 수신.
3. 체결통보 수신.
4. 장애 시 REST fallback.

### 21.3 백테스트

1. 목표가 도달 여부 단순 검증.
2. 매수/매도 조건 기반 손익 계산.
3. 수수료, 세금, 슬리피지 반영.
4. 포트폴리오 단위 성과 분석.
5. Walk-forward test.
6. 리서치 에이전트와 연결.

### 21.4 UI 확장

1. FastAPI + React.
2. 사용자 인증.
3. 실시간 화면 갱신.
4. 주문 승인 워크플로우.
5. 로그 필터링.
6. 일간/주간 리포트.

### 21.5 DB/운영 확장

1. PostgreSQL.
2. Docker.
3. 서버/클라우드 배포.
4. Redis.
5. Celery 작업 큐.
6. Grafana 모니터링.
7. Secret Manager.

### 21.6 주문 기능 확장

1. 분할매수.
2. 분할매도.
3. 정정/취소 고도화.
4. 트레일링 스탑.
5. 시장가 보호 주문.
6. 최우선 호가 기준 지정가.
7. 호가 스프레드 기반 주문 최적화.

### 21.7 전략 확장

1. 수익률 기준 익절/손절.
2. 이동평균.
3. RSI.
4. 거래량 조건.
5. 모멘텀.
6. 평균회귀.
7. 리밸런싱.
8. 포트폴리오 최적화.

### 21.8 상품 확장

1. 채권.
2. 펀드.
3. 선물.
4. 옵션.
5. 레버리지/인버스 ETF.
6. 신규상장주.

### 21.9 에이전트 확장

1. 읽기 전용 리서치 에이전트 고도화.
2. 뉴스/공시 요약.
3. 실적 캘린더 분석.
4. 매크로 분석.
5. 조건 제안 에이전트 고도화.
6. 백테스트 자동 실행.
7. 전략 개선안 제안.
8. 제한적 자가개선 루프.

---

## 22. 운영 원칙

### 22.1 핵심 원칙

```text
수익보다 생존.
자동화보다 통제.
복잡한 전략보다 안전한 실행.
AI 판단보다 사용자 승인.
확장 기능은 버리지 않고 Roadmap에 보관.
```

### 22.2 AI 관련 원칙

1. AI는 제안자다.
2. AI는 주문자가 아니다.
3. AI는 리스크 한도를 바꾸지 못한다.
4. AI는 Kill Switch를 해제하지 못한다.
5. AI 제안은 반드시 사용자 승인 후 저장된다.
6. AI 제안으로 저장된 조건은 자동주문 OFF가 기본이다.

### 22.3 실전 운영 원칙

1. 첫 실전은 수동 버튼 1주 매수/매도.
2. 자동주문은 명시적 ON이 필요하다.
3. Kill Switch 실행 시 자동주문 OFF.
4. 재시작 시 자동주문 기본 OFF.
5. 주문 실패 시 자동 재주문 금지.
6. 체결/잔고 확인 실패 시 전체 정지.
7. 오류는 로그와 Telegram으로 즉시 알림.

---

## 23. 첫 개발 체크리스트

### 23.1 바로 해야 할 일

1. 한투 Open API 계정 및 모의투자 키 준비.
2. Windows Python 3.10+ 확인.
3. 프로젝트 폴더 생성.
4. venv 생성.
5. `.env.example` 작성.
6. `.gitignore` 작성.
7. 한투 인증 테스트.
8. 국장 현재가 조회 테스트.

### 23.2 첫 번째 성공 기준

첫 번째 개발 성공 기준은 다음이다.

```text
한투 Open API로 KODEX 200 또는 삼성전자 현재가를 조회하고,
그 결과를 터미널 또는 Streamlit 화면에 표시한다.
```

이 단계가 성공하면 MVP 구현이 실제로 시작된다.

---

## 24. 미해결 확인사항

구현 단계에서 확인해야 할 사항이다.

1. 한투 모의투자 API에서 국내주식 현재가, 주문, 체결, 잔고 조회가 실제로 원하는 방식으로 지원되는지.
2. 모의투자와 실전 API의 응답 차이.
3. 시장가 주문 파라미터의 정확한 코드.
4. 지정가 주문 파라미터의 정확한 코드.
5. 주문 취소 API의 정확한 필수값.
6. 체결 조회 API의 지연 여부.
7. 잔고 조회 API의 실시간 반영 속도.
8. API 호출 제한.
9. Windows 환경에서 인증/네트워크 이슈.
10. Telegram Bot 토큰/Chat ID 설정.

---

## 25. 결론

본 MVP는 단순한 자동매매 봇이 아니라, 장기적으로 개인 투자 철학을 코드화하고, 가드레일과 리서치 에이전트를 결합해 점진적으로 확장 가능한 개인 투자 운용 시스템의 첫 단계다.

MVP의 핵심은 수익률 극대화가 아니라 다음이다.

```text
안전한 주문 파이프라인 구축
조건 기반 실행 검증
로그와 UI 기반 관제
소액 자동주문 검증
확장 가능한 구조 확보
```

이 문서는 구현 과정에서 계속 업데이트되어야 한다.
