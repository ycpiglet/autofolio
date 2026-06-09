# Autofolio 제품·시스템 설계서 (PRODUCT_BLUEPRINT)

> 상태: **기획 확정 / 구현 단계별 진행**
> 본 문서는 *무엇을·어떻게(제품/시스템/기능/연동/아키텍처)* 를 정의한다. *누가(조직)* 는 [ORG_PLAN.md](ORG_PLAN.md) 참고.

한 줄 비전: **에이전트 팀이 운용하는 개인용 멀티에셋 자동매매 OS** — 평상시엔 사람이 결정하고, 원할 땐 가드레일 안에서 스스로 돈다. 어디서든(Telegram/Discord/Google) 알림받고 원격으로 조종하며, 증권사 앱이 주는 모든 것 + 미래/과거 분석을 제공한다.

---

## 1. 설계 원칙
1. **Safety-first** — 기본값 mock·자동매매 OFF·화이트리스트·킬스위치. 모든 자동화 위에 하드리밋.
2. **Human-in-the-loop이 기본, auto는 옵트인** — 자율성은 *레벨*로 조절(§2). 업계 베스트프랙티스. ([FxPro 2026 가이드](https://www.fxpro.com/help-section/education/beginners/articles/auto-trade-basics-a-complete-beginners-guide-for-2026))
3. **멀티채널·원격 우선** — 로컬 UI 없이도 폰에서 전부 가능.
4. **확장 가능한 어댑터 구조** — 브로커(KIS→타사), 채널(Telegram/Discord/Google), 시장(국장→미장)을 플러그인처럼.
5. **모든 것은 기록된다** — 결정·거래·회고가 DB/문서로 남아 학습 루프를 돌린다.

---

## 2. 운영 모드 — 자율성 레벨 (L0–L4)

자율주행처럼 **단계별 자율성**을 둔다. 사용자가 종목·전략별로 레벨을 지정한다.

| 레벨 | 이름 | 에이전트 권한 | 사람 개입 | 비유 |
|---|---|---|---|---|
| **L0** | Observer / 관찰 | 정보 제공만 | 사람이 전부 실행 | 백미러 |
| **L1** | Advisory / 자문 **(현 MVP 기본)** | 제안 생성 | **건건이 승인** | 내비 안내 |
| **L2** | Co-pilot / 반자동 | 사전승인 플레이북 내 주문 *대기* 생성 | 임계치에서 확인 | 크루즈 컨트롤 |
| **L3** | **Supervised Auto / 감독형 자동** ("auto 사냥 모드") | mandate·예산 내 **자율 실행** | 모니터 + 거부/킬 | 오토파일럿 |
| **L4** | Full Auto / 완전자동 | 하드리밋 내 완전 자율 | **예외만** 보고·승인 | 자율주행 |

- **"auto 사냥 모드" = L3.** 정의한 화이트리스트·전략 안에서 에이전트가 스스로 감시→판단→(게이트 통과 시) 주문→알림. 사람은 대시보드/폰에서 감독하고 언제든 정지.
- 자율성은 **종목/전략 단위**로 분리 지정 가능 (예: 코어 ETF는 L3, 개별주는 L1).
- 반자동(semi-auto)은 *알림/시그널/주문안 생성 + 사람 승인*의 절충 — 속도와 판단을 결합. ([Semi-Automated Trading](https://algobot.com/semi-automated-trading/))

### 🛡️ Auto 모드 안전장치 (L3+ 필수, §7 상술)
킬스위치 · 화이트리스트 전용 · **일일 예산/주문수 한도** · **서킷브레이커(손실 한도 도달 시 자동 정지)** · 거래시간 창 · 쿨다운·중복방지 · mock→paper→prod 단계 승급 · **모든 자동 행동 즉시 알림**.

---

## 3. 기능 범위 — 증권사 앱 패리티

증권사 앱/홈페이지가 주는 기능을 도메인별로 정의하고 `app/` 모듈·구현 단계에 매핑한다.

| 도메인 | 기능 | 코드 매핑 | 단계 |
|---|---|---|---|
| **시세·조회** | 실시간 현재가·호가, 차트(분/일/주/월), 관심종목 와치리스트, 종목검색, **스크리너** | `brokers/kis`, `ui` | P1~P2 |
| **주문·매매** | 매수/매도, 지정가/시장가/조건부·예약, 정정/취소, 미체결, **목표가 자동매매 조건**, 분할매매 | `engine`, `brokers` | P0~P1 |
| **계좌·포트폴리오** | 보유종목·수량·평단, **평가손익/실현손익**, 비중·자산배분, 예수금·증거금 | `database`, `engine`, `ui` | P1 |
| **손익·기록** | 거래내역·체결내역, 일/월별 손익, **수수료·세금**, 배당내역, 손익 리포트 | `database/repositories`, `ui` | P1 |
| **환율·해외** | 실시간 환율, 환전, 해외주식 잔고·통화별 손익, 환헤지 상태 | `brokers`, `agents/fx` | P2~P3 |
| **알림·리포트** | 가격/체결/조건 알림, 뉴스·공시, **일일/주간 요약 리포트** | `notification`, scheduler | P1~P2 |
| **관리·설정** | 화이트리스트, 리스크 한도, **운영 모드(L0–L4)**, 킬스위치, 채널 설정 | `config`, `risk`, `ui` | P0~P1 |

> 표준 트래커 기능 참고: Daily/Unrealized/Realized/Total Gain, 와치리스트, 가격알림, 차트(50+ 지표 MACD·RSI·볼린저), 스크리너, 거래유형(Buy/Sell/Dividend/Split). ([Fidelity](https://www.fidelity.com/trading/trading-platforms) · [Best Portfolio Trackers](https://stockanalysis.com/article/best-stock-portfolio-tracker/))

---

## 4. 분석 — 과거 탭 & 미래 탭

증권앱을 넘어서는 차별점. 에이전트 조직과 직결된다.

### 📉 과거 분석 탭 (Retrospective)
- **거래 기록·저널** — 거래별 진입/청산 이유, A~F 등급(계획 준수도).
- **손익 기여 분석(Attribution)** — 수익이 *어느 결정·어느 에이전트/자산군*에서 났는지 분해.
- **회고(`/retro`)** — 주/월 승률·평균 R·MDD·규율점수, 패자 부검(post-mortem), 교훈.
- **백테스트 결과** — 전략/조건의 과거 성과(퀀트팀 ③, look-ahead 방어).
- **패턴·습관 진단** — 반복 실수·감정적 일탈 플래그.

### 🔮 미래 분석 탭 (Forward)
- **시나리오 분석** — base/bull/bear, 매크로 레짐별 포트폴리오 반응.
- **리스크 시뮬레이션** — 스트레스(주가 −20%, 금리 +1%p, 환 ±10%), 몬테카를로 분포, VaR/MDD 추정.
- **목표·리밸런싱 플랜** — 목표배분 대비 갭, 제안 리밸런싱 경로·예상비용.
- **예측 시그널** — 퀀트 시그널·매크로 뷰 기반 확률적 전망 (단정 아님, 가드레일·확신도 표기).
- **What-if** — "이 종목 비중 2배면?" 같은 가상 포트폴리오 영향.

---

## 5. 인터페이스 & 원격 연동 (멀티채널)

```
                         ┌──────────────── Autofolio Core ────────────────┐
   사람(어디서든)  ⇄    │  Notification/Command Bus (채널 어댑터 추상화)   │
        │               └───────┬───────────┬───────────┬─────────────────┘
   ┌────┴────┐                  │           │           │
   │ Streamlit│  (로컬 관제)     │           │           │
   │   UI     │                 ▼           ▼           ▼
   └─────────┘            Telegram      Discord      Google
                          (알림+명령+    (채널별·     (Gmail 리포트·
                           에이전트챗)    embed·       Sheets 미러·
                                          IC 스레드)   Calendar 리뷰)
```

### 채널별 역할
- **Streamlit UI** — 로컬 풀 관제(이미 `app/ui/streamlit_app.py`).
- **Telegram** — *이미 `app/notification/telegram_notifier.py` 스캐폴드 존재*. 알림 + 원격 명령 + **자연어로 에이전트와 채팅**. ([EODHD Telegram bot](https://eodhd.com/financial-academy/building-stocks-apps-examples/create-a-telegram-trading-bot))
- **Discord** — 주제별 채널(#alerts #trades #research #risk #ic), embed 카드, **IC 토론은 스레드**로. 에이전트가 채널에 포스팅 → "에이전트들과 소통". ([TradingView Webhook Bot](https://github.com/fabston/TradingView-Webhook-Bot))
- **Google** — Gmail(일일/주간 리포트), **Sheets(포트폴리오/저널 미러·자동 ROI·주간 리포트)**, Calendar(회고 일정), Chat(메시징). ([n8n 포트폴리오+Sheets+Telegram](https://n8n.io/workflows/6317-track-multi-broker-investment-portfolio-with-google-sheets-and-telegram-alerts/) · [Sheets 파이낸스 봇](https://medium.com/@apes.finance/creating-the-ultimate-finance-telegram-bot-using-google-sheets-424e19e0a87e))
- **KakaoTalk** — 한국 개인 무료 루트는 **"나에게 보내기"**(Kakao Login + `talk_message`). 알림톡/친구톡은 사업자·유료라 제외. ([Kakao Message API](https://developers.kakao.com/docs/latest/en/kakaotalk-message/common) · [PyKakao 예제](https://wooiljeong.github.io/python/pykakao-message/))
- **Notion** — 공식 무료 API(`notion-client`). 실시간 알림보다 **기록·저널·결정로그·대시보드** 면(面). ([notion-sdk-py](https://github.com/ramnes/notion-sdk-py))
- **Email(SMTP)** — 가장 단순한 무료 폴백. 리포트·요약용.

### 원격 명령어 카탈로그 (채널 공통)
| 명령 | 동작 |
|---|---|
| `/status` | 시스템·모드·자동매매 ON/OFF·킬스위치 상태 |
| `/positions` `/pnl` | 보유·평가손익 / 일·누적 손익 |
| `/watch` `/quote <종목>` | 와치리스트 / 현재가 |
| `/alert <종목> <가격>` | 가격 알림 설정 |
| `/propose` `/approve <id>` `/reject <id>` | 제안 조회 / 승인 / 거부 (L1·L2) |
| `/mode <종목> <L0..L4>` | 자율성 레벨 변경 |
| `/pause` `/resume` `/kill` | 자동매매 일시정지 / 재개 / **킬스위치** |
| `/ask <agent> <질문>` | 특정 에이전트와 대화 (예: `/ask etf-specialist 반도체 ETF 추천`) |
| `/ic <종목>` `/retro` | 투자위원회 소집 / 회고 리포트 |

### 알림 트리거
체결·미체결·취소 / 가격·조건 도달 / 일일·주간 요약 / 리스크 한도·서킷브레이커 발동 / 뉴스·공시 / auto 모드의 모든 행동.

### 채널 비교 — 비용·간편·Python·보안 (선정 기준)
| 채널 | 비용 | 난이도 | Python 라이브러리 | 안정성 | 보안 | 추천 용도 |
|---|---|---|---|---|---|---|
| **Telegram** | 무료 | ★쉬움 | `python-telegram-bot`(성숙) | 높음 | 봇 토큰 | **실시간 알림·원격 명령(주력)** |
| **Notion** | 무료 | ★쉬움 | `notion-client`(공식) | 높음 | integration 토큰(스코프) | **기록·저널·결정로그·대시보드** |
| **Discord** | 무료 | 쉬움 | `discord.py`/webhook | 높음 | 봇 토큰/웹훅 | 에이전트 채널·IC 토론 |
| **KakaoTalk(나에게)** | 무료 | 보통(OAuth) | `requests`/PyKakao | 높음(공식) | OAuth(`talk_message`) | **한국 개인 알림** |
| **Email(SMTP)/Gmail** | 무료 | ★쉬움 | 표준 lib | 높음 | 앱비밀번호/OAuth | 리포트 폴백 |
| **Google Sheets** | 무료 | 보통 | `gspread` | 높음 | OAuth | 포트폴리오/저널 미러 |

**선정:** 주력 **Telegram(알림·명령) + Notion(기록·대시보드)**, 한국 개인 알림 **Kakao 나에게**, 에이전트 토론 **Discord**, 리포트 **Email/Sheets**. 전부 무료·공식 API·Python 친화. 모두 **채널 어댑터**로 추상화해 끼웠다 뺐다 한다.

### 5.5 SSO · 계정 연동 (UI에서 바로) — 3종을 구분하라
실제 배포 앱처럼 **설정 화면에서 클릭으로** 연동하되, 기술적으로 셋은 다르다:

**(A) 앱 로그인 SSO — Google·Kakao·Naver 소셜 로그인**
- Streamlit 내장 `st.login()` = **OIDC 기반**. → **Google = OIDC, 가장 간단·무료(1순위)**. ([Streamlit auth](https://docs.streamlit.io/develop/concepts/connections/authentication) · [st.login](https://docs.streamlit.io/develop/api-reference/user/st.login))
- **Kakao** = OIDC 지원 → 커스텀 metadata로 `st.login` 연결 가능. **Naver** = OAuth2(OIDC 아님) → `st.login` 직접 불가.
- 권장: ① Google 내장 OIDC → ② Kakao·Naver는 무료 `streamlit-oauth` 컴포넌트, 또는 아이덴티티 브로커(Keycloak 자체호스팅 무료 / Auth0 무료티어)로 페더레이션 후 OIDC 연결.

**(B) 알림 채널 연동 — OAuth/토큰**
Telegram(봇토큰)·Kakao(Kakao Login+`talk_message`)·Notion(integration 토큰)·Discord(웹훅/봇)·Google(OAuth). UI "연동" 토글 → 토큰/OAuth 발급 → **암호화 저장**.

**(C) 증권계좌 연동 — 입력 → [연동하기] → 즉시 검증 (소셜 SSO ❌, 자격증명 ⭕)**
- KIS Open API = **appkey + appsecret + 계좌번호**(KIS Developers 발급, 계좌 8+2 형식) → 앱이 access token 발급(1분당 1회). 소셜 리다이렉트가 아니라 **자격증명 방식**.
- UI 흐름: **ID · App Key · App Secret · 계좌번호 입력 → [연동하기] 클릭** → 토큰 발급 + **잔고조회 테스트 호출** → 성공 시 즉시 "✅ 연동 완료"(실패 시 사유 표시). 성숙한 Python 래퍼 존재. ([KIS Developers](https://apiportal.koreainvestment.com/intro) · [python-kis](https://github.com/Soju06/python-kis))
- **다계좌·다ID 지원**: 여러 증권계좌/키를 별칭으로 등록·전환·합산. 연동별 환경(mock/모의/실전) 개별 지정.
- 자격증명은 **암호화 보관**(§5.6·§5.7). 오픈뱅킹·마이데이터식 자동연동은 기관 인가 필요 → 범위 밖.

### 5.6 보안 모델
- 시크릿 **코드/DB 평문 금지** → `.env`(로컬) / OS keyring / 암호화 저장(`cryptography` Fernet). 아키텍처에 **Auth & Secrets Vault** 컴포넌트 추가.
- OAuth 토큰 암호화·자동 갱신, **최소권한 스코프**(Kakao `talk_message`만, Notion 특정 DB만, Telegram 봇 1개).
- 배포 시 리다이렉트 URI **HTTPS 필수**, state/CSRF 검증. **로컬-퍼스트** 옵션(모든 시크릿 사용자 기기).
- 브로커 **mock 기본**, 실전 승급은 단계 검증 + 명시 동의. 읽기 우선.

### 5.7 사용자 계정 & 연동 보관함 (Connections Vault)
**"플랫폼 자체 계정을 만들고, 거기에 SNS·증권사 연동을 저장해 한곳에서 관리"** — 실제 앱들의 표준이고 권장 방향이다. 데이터 모델:
```
User (플랫폼 계정)               ← SSO(Google/Kakao/Naver) 또는 로컬 email+pw
 ├─ Identities[]     소셜 로그인 연결 (여러 SNS)
 ├─ Channels[]       알림 채널 (Telegram/Kakao/Notion/Discord/Email) — 토큰
 └─ BrokerAccounts[]  증권 연동 (여러 개)
        · 별칭 · 증권사(KIS…) · appkey/secret(암호화) · 계좌번호 · 환경 · 상태 · 기본계좌여부
```
- **다계좌**: 계좌별 별칭·기본계좌 지정, 전체 합산 뷰 ↔ 계좌별 뷰 전환.
- **단일 관리**: 로그인 한 번 → 내 모든 연동(SNS·채널·증권)을 설정 화면에서 추가/수정/삭제/전환.
- **저장 위치**: 로컬-퍼스트(기기 vault) 기본, 서버 동기화는 옵트인(종단 암호화, §5.6).

### 5.8 '1원 인증'으로 계좌 인증 — 가능할까? → 개인 앱엔 부적합·불필요
- **1원 송금 인증**(예금주 대조 + 입금자명 코드 확인)은 *비대면 본인·계좌 실소유 확인(eKYC)* 용이고, 직접 구현하려면 **계좌인증 API(useB·CODEF·금융결제원 오픈뱅킹 등) + 이용기관(사업자) 등록 + 금융보안 규격 준수 + 유료 계약**이 필요하다 → 개인용 앱엔 과하고 사실상 불가. ([useB 1원인증](https://blog.useb.co.kr/1won) · [금결원 계좌실명조회](https://developers.kftc.or.kr/dev/openapi/open-banking/account) · [CODEF 1원이체](https://developer.codef.io/products/bank/common/etc/accountTransferAuthentication))
- **게다가 불필요하다.** 증권 연동의 검증은 1원이 아니라 **API 테스트 호출**로 한다: appkey/secret/계좌번호로 **토큰 발급 + 잔고조회가 성공**하면 그게 곧 *유효성·접근권한·실소유 증명*이다. 무료·즉시·안전.
- 즉 '실제 증권사처럼 즉시 연동' 경험은 **[연동하기] → 테스트 호출 성공 = 인증 완료**로 동일하게 구현된다. (은행 계좌까지 실명확인할 일이 생기면 그때 useB/CODEF 같은 유료 eKYC를 붙이면 됨.)

---

## 6. 목표 아키텍처

```
┌─ Interface Layer ──────────────────────────────────────────────┐
│  Streamlit UI │ Telegram Bot │ Discord Bot │ Google(Gmail/Sheets)│ REST API
└──────┬──────────────┬──────────────┬───────────────┬───────────┘
       └──────────────┴──────┬───────┴───────────────┘
                   ┌──────────▼──────────┐
                   │  Notification/Command Bus  │  ← 채널 어댑터 추상화
                   └──────────┬──────────┘
        ┌─────────────────────┼─────────────────────────┐
   ┌────▼────┐         ┌───────▼────────┐        ┌────────▼────────┐
   │Scheduler │        │  Orchestrator   │        │  Agent Layer     │
   │/Daemon   │  ←──→  │ (모드·게이트·   │  ←──→  │ ②자산 ③퀀트 ④거버넌스│
   │(auto·알림)│        │  승인 흐름)     │        └────────┬────────┘
   └────┬────┘         └───────┬────────┘                 │
        └───────────────┬──────┘                          │
                ┌────────▼─────────┐               ┌───────▼────────┐
                │  Engine + Risk    │  ←─ 게이트 ─→ │ Decision/Journal │
                │ (조건·안전검사·    │               │  Store (기록)    │
                │  주문흐름)        │               └────────────────┘
                └────────┬─────────┘
              ┌──────────▼───────────┐        ┌────────────────────┐
              │  Broker Adapters      │        │  Data Layer         │
              │  KIS │ (Mock) │ 미래:타사│      │ 시세·대체데이터·환율 │
              └──────────┬───────────┘        └────────────────────┘
                         ▼
                  External: KIS Open API ...
```

**신규 핵심 컴포넌트 (현 MVP 대비 추가)**
- **Scheduler/Daemon** — auto 모드 실행 루프 + 주기 알림/리포트 (현 MVP는 수동 REST 폴링).
- **Orchestrator** — 모드(L0–L4)에 따라 제안→게이트→승인/자동→실행 흐름 제어, 에이전트 호출 조율.
- **Notification/Command Bus** — 채널 무관 단일 인터페이스(어댑터로 Telegram/Discord/Google 연결).
- **Decision/Journal Store** — IC 결정·트레이드 저널·회고(학습 루프).
- **Data Layer** — 시세·환율·대체데이터(퀀트팀 ③).

---

## 7. Auto 모드 안전장치 (상세)

L3+ 자동 실행 시 **항상** 적용되는 하드 게이트(우회 불가):

1. **킬스위치** — 1버튼/`/kill`로 전체 자동매매 즉시 중단.
2. **화이트리스트 전용** — 비화이트리스트 종목 자동 편입 불가.
3. **예산·주문 한도** — 일일 매매금액·주문수·종목당 비중 상한.
4. **서킷브레이커** — 일/주 손실 한도 도달 시 자동 정지 + 알림 + 사람 승인 전까지 재개 불가.
5. **거래시간 창** — 지정 시간대 밖 자동주문 금지(`risk/trading_window`).
6. **쿨다운·중복방지** — `risk/duplicate_guard`.
7. **단계 승급** — `mock → paper(모의투자) → prod`, 각 단계 검증 후에만 다음 단계. 실전은 소액·수동 1주 테스트 선행.
8. **전수 알림·감사로그** — 자동 행동 100% 기록·통지, 사후 회고 가능.

> 자동화의 속도 + 사람의 판단을 결합하되, **통제권은 항상 사람에게**. ([Manual vs Automated](https://www.ssa.group/blog/manual-vs-automated-trading-which-is-better-for-you/))

---

## 8. 단계별 로드맵

| Phase | 목표 | 주요 산출물 | 모드 |
|---|---|---|---|
| **P0 (현재)** | MVP 스캐폴드 | mock 브로커, 엔진/리스크 골격, Streamlit, Telegram 스캐폴드, 자산팀 에이전트 | L1(mock) |
| **P1** | 실거래 기반 + 앱 패리티 | KIS 실연동(paper), 포트폴리오/손익/기록/환율 UI, 알림 레이어, 명령 봇(Telegram) | L1 |
| **P2** | 분석 + 거버넌스 + 멀티채널 | ③퀀트팀·백테스트 모듈, 과거 분석 탭, `/ic`·`/retro`, Discord, 에이전트 챗 | L1→L2 |
| **P3** | Auto 모드 + 미래분석 + Google | Scheduler/Daemon, **L3 감독형 자동**, 서킷브레이커, 미래 분석 탭(시나리오/예측), Google(Gmail/Sheets) | L2→L3 |
| **P4** | 자율·확장 | L4 지향, 자가개선 루프, 멀티브로커, 미장 실행, 모바일/PWA | L3→L4 |

---

## 9. 리서치 근거 (Sources)
- 자율성/자동화 레벨: [FxPro 2026](https://www.fxpro.com/help-section/education/beginners/articles/auto-trade-basics-a-complete-beginners-guide-for-2026) · [Semi-Automated](https://algobot.com/semi-automated-trading/) · [Manual vs Automated](https://www.ssa.group/blog/manual-vs-automated-trading-which-is-better-for-you/)
- 앱 기능셋: [Fidelity Trader+](https://www.fidelity.com/trading/trading-platforms) · [Trading App Features](https://www.jploft.com/blog/stock-trading-app-features) · [Best Portfolio Trackers](https://stockanalysis.com/article/best-stock-portfolio-tracker/)
- 채널·봇 연동: [TradingView Webhook Bot](https://github.com/fabston/TradingView-Webhook-Bot) · [EODHD Telegram bot](https://eodhd.com/financial-academy/building-stocks-apps-examples/create-a-telegram-trading-bot) · [n8n + Sheets + Telegram](https://n8n.io/workflows/6317-track-multi-broker-investment-portfolio-with-google-sheets-and-telegram-alerts/)
- AI 시장: [Two Sigma 2026](https://www.twosigma.com/articles/ai-in-investment-management-2026-outlook-part-i/) · [TradingAgents](https://arxiv.org/html/2412.20138v5) · [Look-Ahead-Bench](https://arxiv.org/pdf/2601.13770)
