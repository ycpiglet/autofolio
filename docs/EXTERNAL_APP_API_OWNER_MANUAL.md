# External App/API Owner Setup Manual

상태: 운영 매뉴얼
최종 검토: 2026-06-13
관련 기록: TASK-044, TASK-043, EXTERNAL-APP-API-DECISION-RECORD

이 문서는 Autofolio를 Telegram, Kakao, Google, X, Naver, Discord, Notion,
Slack 같은 외부 앱/API와 연결하려면 Owner가 무엇을 직접 준비해야 하는지 정리한다.

핵심 원칙:

1. 실제 계정 생성, 개발자 콘솔 가입, API key 발급, OAuth 동의, 요금제 선택, 검수 신청은 Owner가 직접 한다.
2. Agent는 코드, 설정 템플릿, 검증 스크립트, 안전 게이트, 문서화를 맡는다.
3. 실제 secret/token/key/password는 Git, PR, issue, chat 기록, 로그에 남기지 않는다.
4. 기본 허용 범위는 outbound alert/report, read-only command, selected destination write다.
5. 외부 앱에서 주문, 취소, prod 전환, risk gate 변경, credential 수정, 송금/출금/결제 같은 행동은 기본 기각 또는 R3 Owner 승인 대상이다.

## 0. Owner가 먼저 정해야 할 것

| 결정 | 권장 기본값 | 이유 |
|------|-------------|------|
| 연동 우선순위 | Telegram -> Discord webhook -> Notion/Sheets -> Kakao -> Google/Naver SSO -> X | 낮은 권한부터 검증하기 쉽다. |
| secret 보관 위치 | `.env` 또는 승인된 local vault | Git에 real secret을 넣지 않는다. |
| 알림 채널 | 개인/비공개 채널 | 투자 내역과 계좌 정보가 포함될 수 있다. |
| 외부 명령 범위 | read-only only | 원격 제어가 주문/risk surface로 번지는 것을 막는다. |
| OAuth scope | 최소 scope | 검수, 보안, 유출 피해를 줄인다. |
| 비용 발생 API | 별도 승인 후 | X, Google Cloud 일부 기능, Kakao business messaging 등은 요금제/쿼터가 바뀔 수 있다. |

## 1. 공통 준비 패키지

각 연동을 구현하기 전에 Owner가 아래 표를 채운다. 실제 값은 이 문서에 쓰지 말고,
로컬 `.env`, secret manager, 또는 암호화 vault에 넣는다.

| 항목 | 예시 | Owner 준비 여부 |
|------|------|----------------|
| 서비스명 | Telegram / Kakao / Google / X / Naver / Discord | 직접 선택 |
| 목적 | 체결 알림 / 일일 리포트 / SSO / 포트폴리오 미러 | 직접 선택 |
| 계정 소유자 | Owner 개인 계정 또는 전용 개발자 계정 | 직접 생성 |
| 개발자 앱 이름 | `Autofolio Local` | 직접 등록 |
| 권한 scope | `chat:write`, `talk_message`, `openid email profile` 등 | 직접 승인 |
| redirect URI | `http://localhost:8501/oauth/callback/...` 등 | 구현 전 확정 |
| secret/key/token | 실제 값 | Owner만 발급 |
| 비용/요금제 | 무료/유료/쿼터 | Owner 승인 |
| 폐기 방법 | token revoke, webhook delete, app disable | Owner 확인 |
| 테스트 채널 | 개인 chat, private server, test sheet/page | Owner 생성 |

Agent가 받을 수 있는 것은 "실제 secret 값" 자체보다 다음 형태가 더 안전하다.

- `.env`에 Owner가 직접 넣은 뒤 Agent는 변수명만 확인한다.
- Owner가 로컬 화면에서 붙여넣고 저장한다.
- Agent에게는 masked 값, 예를 들어 앞 4글자와 끝 4글자만 공유한다.
- 실수로 노출되면 즉시 rotate/revoke한다.

## 2. Owner와 Agent의 역할 분리

| 작업 | Owner | Agent |
|------|-------|-------|
| 계정 가입/로그인 | 직접 수행 | 불가 |
| 개발자 콘솔 앱 생성 | 직접 수행 | 가이드 제공 |
| API key/token/client secret 발급 | 직접 수행 | 변수명/보관 경로 안내 |
| OAuth consent 화면에서 동의 | 직접 수행 | auth URL 생성 가능 |
| 유료 플랜 선택/결제 | 직접 수행 | 비용/쿼터 리스크 설명 |
| 검수/심사 신청 | 직접 수행 | 제출 자료 초안 가능 |
| `.env.example` 변수명 추가 | 승인 후 가능 | 수행 가능 |
| 실제 `.env`에 secret 입력 | 직접 수행 | 원칙상 불가 |
| safe smoke test 실행 | secret 입력 후 같이 가능 | 수행 가능 |
| 알림/리포트 어댑터 구현 | 승인 후 가능 | 수행 가능 |
| 주문/취소/prod/risk 원격 명령 | R3 승인 필요 | 기본 구현 금지 |

## 3. 우선순위별 준비 가이드

### 3.1 Telegram

권장 용도:

- 체결/오류/일일 요약 알림
- `/status`, `/pnl`, `/positions`, `/quote` 같은 read-only 명령
- `/kill`은 조건부 승인
- `/approve`, 주문, 취소, prod 전환은 R3

Owner가 직접 할 일:

1. Telegram 계정을 준비한다. 전화번호 인증이 필요하다.
2. Telegram에서 `@BotFather`와 대화를 시작한다.
3. `/newbot`으로 봇을 만들고 이름과 username을 정한다.
4. BotFather가 발급한 bot token을 복사한다.
5. 새 bot에게 `/start`를 보낸다.
6. 개인 chat 또는 private group 중 어느 곳으로 알림을 받을지 정한다.
7. `chat_id`를 확인한다. Autofolio의 `scripts/setup_telegram.py --get-chat-id`를 쓸 수 있다.
8. 허용할 chat ID allowlist를 정한다.

Owner가 준비할 값:

```text
TELEGRAM_BOT_TOKEN=<bot token>
TELEGRAM_CHAT_ID=<owner chat id>
TELEGRAM_ALLOWED_CHAT_IDS=<comma-separated chat ids>
```

Agent가 할 수 있는 일:

- `scripts/setup_telegram.py --verify`로 token 형식을 검증한다.
- `scripts/setup_telegram.py --send "test"`로 테스트 메시지를 보낸다.
- read-only 명령만 열리도록 테스트를 추가한다.
- `/approve`, 주문, 취소 계열은 R3 task 없이는 막아둔다.

Owner 주의사항:

- Bot token은 password와 동일하게 취급한다.
- private group을 쓰면 봇이 들어간 채널의 멤버가 알림을 볼 수 있다.
- BotFather의 command list는 편의 기능일 뿐이다. 실제 권한 검사는 Autofolio가 해야 한다.

공식 근거:

- https://core.telegram.org/bots/features
- https://core.telegram.org/bots/api

### 3.2 Discord

권장 용도:

- private server의 `#alerts`, `#trades`, `#research` 같은 채널에 webhook 알림
- IC/research thread는 bot/slash command로 확장 가능하지만 조건부 또는 R3

Owner가 직접 할 일, webhook 방식:

1. Discord 계정을 준비한다.
2. 개인용 private server를 만들거나 기존 server에서 private channel을 만든다.
3. 채널 설정에서 Integrations 또는 Webhooks를 연다.
4. New Webhook을 만들고 이름을 `Autofolio Alerts`처럼 지정한다.
5. Webhook URL을 복사한다.
6. 해당 채널에 누가 접근할 수 있는지 확인한다.

Owner가 준비할 값:

```text
DISCORD_WEBHOOK_URL=<incoming webhook url>
```

bot/slash command까지 원할 때 Owner가 추가로 할 일:

1. Discord Developer Portal에서 application을 만든다.
2. Bot을 추가하고 token을 발급한다.
3. OAuth2 URL Generator에서 필요한 scope를 선택한다.
4. 최소 scope는 `bot`, `applications.commands`이며, 권한은 읽기/쓰기 목적별로 최소화한다.
5. generated invite URL로 Owner의 server에 직접 초대한다.

Agent가 할 수 있는 일:

- webhook payload를 안전하게 보내도록 `allowed_mentions`를 제한한다.
- message length, embed, rate-limit 실패 처리를 구현한다.
- slash command는 별도 R3/조건부 task로 분리한다.

Owner 주의사항:

- Webhook URL은 인증 없이 메시지를 보낼 수 있는 secret이다.
- public server나 공유 채널에는 투자/계좌 정보가 나가지 않게 한다.
- bot token은 webhook보다 권한이 넓어질 수 있으므로 별도 승인 후 사용한다.

공식 근거:

- https://docs.discord.com/developers/resources/webhook
- https://docs.discord.com/developers/topics/oauth2
- https://docs.discord.com/developers/quick-start/getting-started

### 3.3 Google

Google은 기능별로 준비물이 다르다.

권장 용도:

- Google Sheets: 포트폴리오/저널/리포트 미러
- Google Chat: private space webhook 알림
- Google Calendar: 회고/점검 일정 생성
- Google SSO: 로그인
- Gmail: outbound report만 조건부, mailbox read/modify는 R3

Owner가 공통으로 직접 할 일:

1. Google 계정을 준비한다.
2. Google Cloud Console에서 프로젝트를 만든다.
3. 필요한 API만 enable한다. 예: Google Sheets API, Gmail API, Calendar API.
4. OAuth consent screen을 설정한다.
5. OAuth client 또는 service account 중 어떤 방식을 쓸지 정한다.
6. billing이 필요한 기능이면 Owner가 직접 billing 연결 여부를 결정한다.

Sheets service account 방식, 권장:

1. Google Cloud에서 service account를 만든다.
2. service account key JSON을 생성한다.
3. Autofolio 전용 스프레드시트를 만든다.
4. 스프레드시트를 service account email에 공유한다.
5. spreadsheet ID를 복사한다.
6. JSON key 파일은 Git 밖의 안전한 경로에 저장한다.

Owner가 준비할 값:

```text
GOOGLE_SERVICE_ACCOUNT_JSON=<local path to json key>
GOOGLE_CREDS_JSON=<optional json string, only if vault supports it>
GOOGLE_SHEETS_SPREADSHEET_ID=<spreadsheet id>
```

Google OAuth 방식, SSO/Calendar/Gmail용:

1. OAuth consent screen에서 app name, support email, developer contact를 입력한다.
2. User type을 선택한다. 개인 테스트라면 test users에 Owner 계정을 등록한다.
3. OAuth client ID를 만든다.
4. Authorized redirect URI를 등록한다.
5. client ID와 client secret을 복사한다.
6. 필요한 scope만 선택한다.

Owner가 준비할 값:

```text
GOOGLE_CLIENT_ID=<oauth client id>
GOOGLE_CLIENT_SECRET=<oauth client secret>
GOOGLE_REDIRECT_URI=<registered redirect uri>
```

Google Chat webhook:

1. Google Chat에서 private space를 만든다.
2. Apps and integrations 또는 Manage webhooks에서 incoming webhook을 만든다.
3. webhook URL을 복사한다.

Owner가 준비할 값:

```text
GOOGLE_CHAT_WEBHOOK_URL=<incoming webhook url>
```

Agent가 할 수 있는 일:

- Sheets append/update adapter를 선택된 spreadsheet에만 제한한다.
- Calendar event 생성은 Owner가 허용한 calendar만 쓰게 한다.
- Gmail은 send-only 또는 SMTP fallback을 우선 검토한다.
- broad Drive scope는 MVP에서 사용하지 않는다.

Owner 주의사항:

- Google Workspace API 사용에는 Cloud project가 필요하다.
- 일부 API/기능은 billing이 필요할 수 있다.
- Gmail read/modify, Drive broad access는 privacy/security review가 필요하다.
- service account key JSON은 유출 시 즉시 key delete/rotate한다.

공식 근거:

- https://developers.google.com/workspace/guides/create-project
- https://developers.google.com/identity/protocols/oauth2/web-server
- https://developers.google.com/workspace/gmail/api/auth/scopes
- https://developers.google.com/workspace/sheets/api/guides/authorizing
- https://docs.cloud.google.com/iam/docs/service-accounts-create
- https://developers.google.com/workspace/chat/quickstart/webhooks
- https://developers.google.com/workspace/calendar/api/guides/create-events

### 3.4 Kakao

권장 용도:

- Owner 본인에게 KakaoTalk 메시지 보내기
- Kakao SSO는 조건부
- 친구 메시지, 알림톡, 친구톡, 비즈 메시지는 R3

Owner가 직접 할 일:

1. Kakao 계정으로 Kakao Developers에 로그인한다.
2. 내 애플리케이션에서 새 앱을 만든다.
3. REST API key를 확인한다.
4. Kakao Login을 사용할 경우 Usage settings를 ON으로 바꾼다.
5. Redirect URI를 등록한다.
6. Client secret을 사용할지 정하고 활성화한다.
7. Consent items에서 필요한 권한만 설정한다.
8. "나에게 보내기"가 필요하면 `talk_message` 관련 동의와 OAuth token 발급 흐름을 준비한다.
9. 개인 정보 항목이나 추가 권한이 필요하면 검수 자료를 준비한다.

Owner가 준비할 값:

```text
KAKAO_REST_API_KEY=<rest api key>
KAKAO_CLIENT_SECRET=<client secret if enabled>
KAKAO_REDIRECT_URI=<registered redirect uri>
KAKAO_ACCESS_TOKEN=<owner-consented access token, short lived>
KAKAO_REFRESH_TOKEN=<refresh token if issued>
```

Owner가 직접 해야 하는 검수/비즈 작업:

- 개인 정보 추가 항목 신청
- biz app 전환
- KakaoTalk Channel 연결
- AlimTalk/FriendTalk/business messaging 계약 또는 템플릿 검수
- privacy policy URL 준비
- 수집 목적/항목/보관 기간 명시

Agent가 할 수 있는 일:

- OAuth redirect URL을 생성한다.
- Owner가 로그인/동의 후 받은 code를 local callback으로 교환하는 흐름을 구현한다.
- refresh token 저장/갱신 로직을 구현한다.
- 메시지 템플릿을 안전한 owner-only 알림으로 제한한다.

Owner 주의사항:

- Kakao access token은 만료되므로 refresh token 관리가 필요하다.
- 친구/비즈 메시지는 개인용 "나에게 보내기"와 다르게 검수/계약/요금 이슈가 생길 수 있다.
- 심사 자료에는 개인정보가 포함되지 않게 한다.

공식 근거:

- https://developers.kakao.com/docs/latest/en/getting-started/app
- https://developers.kakao.com/docs/latest/en/kakaologin/prerequisite
- https://developers.kakao.com/docs/latest/en/kakaologin/rest-api
- https://developers.kakao.com/docs/latest/en/message/rest-api

### 3.5 Naver

권장 용도:

- Naver Login SSO
- Papago 번역, Search helper 같은 read-only helper API
- Naver Works 조직 API는 R3

Owner가 직접 할 일:

1. Naver 계정으로 Naver Developers에 로그인한다.
2. Application을 등록한다.
3. 사용할 API를 선택한다. 예: Naver Login, Papago NMT, Search.
4. 서비스 환경을 선택한다. 웹/모바일 웹이면 PCWEB/MOBILEWEB류를 확인한다.
5. 서비스 URL과 callback URL을 등록한다.
6. Client ID와 Client Secret을 복사한다.
7. Naver Login을 외부 공개 서비스로 쓰려면 사전 검수 필요 여부를 확인하고 신청한다.

Owner가 준비할 값:

```text
NAVER_CLIENT_ID=<client id>
NAVER_CLIENT_SECRET=<client secret>
NAVER_REDIRECT_URI=<registered callback url>
NAVER_API_SET=<login,papago,search>
```

Agent가 할 수 있는 일:

- login callback 처리와 profile 최소 수집을 구현한다.
- Papago/Search API는 read-only helper로만 연결한다.
- quota/rate-limit 실패 처리를 구현한다.

Owner 주의사항:

- 로그인 profile scope는 최소화한다.
- 검수가 필요한 서비스 공개 전에는 테스트 사용자/개발 모드로 제한한다.
- Naver Works는 개인 Autofolio MVP와 별도 조직 권한이 필요할 수 있다.

공식 근거:

- https://developers.naver.com/docs/login/devguide/devguide.md
- https://developers.naver.com/docs/login/api/api.md
- https://developers.naver.com/docs/nmt/reference/
- https://developers.naver.com/docs/common/openapiguide/apilist.md

### 3.6 X

권장 용도:

- read-only monitoring, link preview, watch keyword research
- posting, reposting, like/follow, DM은 R3

Owner가 직접 할 일:

1. X 계정을 준비한다.
2. X Developer Platform에서 developer account/project/app을 만든다.
3. 요금제와 access tier를 확인하고 Owner가 직접 승인한다.
4. App permissions를 read-only로 시작한다.
5. OAuth 2.0 client 또는 bearer token을 발급한다.
6. Callback URL과 website URL을 등록한다.
7. rate-limit와 monthly usage limit를 확인한다.

Owner가 준비할 값:

```text
X_BEARER_TOKEN=<bearer token for read-only app auth>
X_CLIENT_ID=<oauth2 client id, if user auth needed>
X_CLIENT_SECRET=<oauth2 client secret, if confidential client>
X_REDIRECT_URI=<registered callback url>
X_ACCESS_TIER=<plan/tier chosen by Owner>
```

Agent가 할 수 있는 일:

- read-only endpoint wrapper를 만든다.
- rate-limit headers를 읽고 429 backoff를 구현한다.
- posting/DM/follow/like/write actions는 R3 승인 전 막는다.

Owner 주의사항:

- X API는 access tier, endpoint access, rate limits가 자주 바뀔 수 있다.
- public posting은 외부 공개/평판/스팸 리스크가 있어 별도 승인 대상이다.
- scraping이나 unofficial API는 사용하지 않는다.

공식 근거:

- https://docs.x.com/x-api/introduction
- https://docs.x.com/x-api/fundamentals/authentication/oauth-2-0/user-access-token
- https://docs.x.com/x-api/fundamentals/rate-limits

### 3.7 Notion

권장 용도:

- selected database/page에 거래 저널, 리포트, 회고 기록 쓰기
- workspace-wide read/write는 R3

Owner가 직접 할 일:

1. Notion 계정과 workspace를 준비한다.
2. Notion Developer Portal에서 internal connection을 만든다.
3. connection capabilities를 최소로 설정한다.
4. installation access token을 복사한다.
5. Autofolio가 쓸 page 또는 database를 만든다.
6. 해당 page/database에서 connection을 직접 초대한다.
7. page ID 또는 database ID를 복사한다.

Owner가 준비할 값:

```text
NOTION_TOKEN=<internal integration token>
NOTION_PAGE_ID=<selected page id>
NOTION_DATABASE_ID=<selected database id, if used>
```

Agent가 할 수 있는 일:

- selected page/database에만 쓰도록 adapter를 제한한다.
- token 미설정 시 no-op fallback을 유지한다.
- Notion rate-limit와 Retry-After를 처리한다.

Owner 주의사항:

- integration token은 소스 코드에 넣지 않는다.
- Notion page를 connection에 공유하지 않으면 API 요청이 실패한다.
- workspace 전체 권한 대신 필요한 page/database만 공유한다.

공식 근거:

- https://developers.notion.com/guides/get-started/quick-start
- https://developers.notion.com/reference/capabilities

### 3.8 Slack

권장 용도:

- incoming webhook alert
- bot/private channel reads는 R3

Owner가 직접 할 일:

1. Slack workspace를 준비한다.
2. Slack API에서 app을 만든다.
3. Incoming Webhooks를 활성화한다.
4. Add New Webhook to Workspace를 누르고 채널을 선택한다.
5. Webhook URL을 복사한다.
6. bot token이 필요한 기능은 scope와 설치 권한을 별도로 확인한다.

Owner가 준비할 값:

```text
SLACK_WEBHOOK_URL=<incoming webhook url>
SLACK_BOT_TOKEN=<only if bot scope is separately approved>
```

Agent가 할 수 있는 일:

- webhook alert adapter를 구현한다.
- bot token scope는 필요 기능별로 문서화한다.
- private channel read/write는 R3 승인 전 막는다.

Owner 주의사항:

- webhook URL은 해당 채널에 메시지를 보낼 수 있는 secret이다.
- Slack app installation과 scope 승인은 workspace 권한에 따라 Owner가 직접 해야 한다.

공식 근거:

- https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks/
- https://docs.slack.dev/authentication/tokens/

### 3.9 Email/SMTP

권장 용도:

- 일일/주간 리포트 fallback
- 긴 보고서 발송

Owner가 직접 할 일:

1. 사용할 메일 계정을 정한다.
2. provider가 app password를 지원하면 2FA를 켜고 app password를 발급한다.
3. SMTP host, port, username, sender, receiver를 확인한다.
4. Gmail API를 쓸 경우 Google OAuth 항목을 따른다.

Owner가 준비할 값:

```text
EMAIL_SMTP_HOST=<smtp host>
EMAIL_SMTP_PORT=<smtp port>
EMAIL_USERNAME=<sender login>
EMAIL_PASSWORD=<app password or smtp token>
EMAIL_FROM=<from address>
EMAIL_TO=<owner address>
```

Owner 주의사항:

- 일반 계정 password 대신 app password 또는 OAuth token을 사용한다.
- Gmail mailbox read/modify 자동화는 R3다.

## 4. 구현 전 승인 체크리스트

아래가 모두 `Yes`일 때만 Agent가 구현 작업에 들어간다.

| 질문 | Yes/No |
|------|--------|
| 목적이 alert/report/read-only/selected write 중 하나인가? | |
| 필요한 scope가 문서에 적혀 있는가? | |
| Owner가 계정과 developer app을 직접 만들었는가? | |
| token/key는 Git 밖에 보관되는가? | |
| 테스트용 private destination이 있는가? | |
| revoke/rotate 방법을 확인했는가? | |
| 비용/쿼터가 확인되었는가? | |
| 실패 시 no-op fallback 또는 log fallback이 있는가? | |
| 주문/취소/prod/risk/secret 변경 명령이 없는가? | |
| public posting 또는 inbound public webhook이 아닌가? | |

## 5. Agent에게 전달할 때 쓰는 양식

실제 secret 값은 이 양식에 적지 않는다.

```text
서비스:
목적:
허용 기능:
금지 기능:
Owner가 만든 계정:
개발자 앱 이름:
사용할 scope:
redirect URI:
secret 보관 위치:
테스트 destination:
비용/쿼터 확인:
revocation 방법:
R3 여부:
```

예시:

```text
서비스: Telegram
목적: 체결/오류 알림 + read-only 조회 명령
허용 기능: outbound alert, /status, /pnl, /positions, /quote
금지 기능: /approve, 주문, 취소, prod 전환
Owner가 만든 계정: Owner 개인 Telegram
개발자 앱 이름: Autofolio Alerts Bot
사용할 scope: bot token only
redirect URI: 없음
secret 보관 위치: local .env
테스트 destination: Owner private chat
비용/쿼터 확인: 무료 범위
revocation 방법: BotFather token revoke/regenerate
R3 여부: 아니오
```

## 6. 금지/보류 기본값

Owner가 별도로 승인하지 않으면 아래는 구현하지 않는다.

- 외부 앱에서 매수/매도/주문 취소.
- 외부 앱에서 `KIS_ENV=prod` 전환.
- 외부 앱에서 auto mode 활성화.
- 외부 앱에서 kill switch 해제.
- 외부 앱에서 broker credential 수정.
- 외부 앱에서 secret/token 조회.
- Gmail/Drive/private message broad read.
- X, Discord, Slack 등 public posting 자동화.
- inbound public webhook endpoint 노출.
- scraping/unofficial API 사용.
- Kakao AlimTalk/FriendTalk/business messaging.
- mass messaging 또는 marketing broadcast.

## 7. 우선 구현 추천

1. Telegram alert/read-only command
   - Owner 준비가 가장 작고 현재 코드가 이미 가깝다.
2. Discord webhook alert
   - webhook URL 하나로 private channel 알림을 검증할 수 있다.
3. Notion selected DB write 또는 Google Sheets mirror
   - report/export 가치가 높고 주문 경로와 분리된다.
4. Kakao "나에게 보내기"
   - 한국 개인 알림 가치가 있지만 OAuth token 갱신이 필요하다.
5. Google SSO 또는 Naver SSO
   - 로그인 UX 개선용. 현재 개인 로컬 도구라 우선순위는 알림보다 낮다.
6. X read-only monitoring
   - 비용/요금제와 rate-limit가 명확할 때만 진행한다.

## 8. 매뉴얼 변경 기준

이 문서는 다음 중 하나가 발생하면 갱신한다.

- provider 공식 문서에서 auth/scopes/pricing/review flow가 바뀐다.
- Autofolio가 connector capability matrix를 구현한다.
- Owner가 특정 connector 구현을 승인한다.
- OAuth token vault나 secrets policy가 바뀐다.
- 외부 API smoke test 또는 provider review에서 실패가 발생한다.

