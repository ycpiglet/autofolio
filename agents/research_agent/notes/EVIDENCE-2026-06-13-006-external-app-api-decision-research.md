---
type: evidence
id: EVIDENCE-2026-06-13-006
date: 2026-06-13
recorded_at: 2026-06-13T02:06:53+09:00
author: Research Agent (Codex)
related_task: TASK-043
related_catalog: EXTERNAL-APP-API-DECISION-RECORD
scope: external app/API integration approval and rejection research
---

# EVIDENCE-2026-06-13-006 External App/API Integration Research

## Question

Telegram, Kakao, Google, X, Naver, Discord and similar external applications/APIs can
extend Autofolio. Which integrations should be approved, conditionally approved, held
for R3 approval, or rejected?

## Sources

Official or primary sources reviewed:

- Telegram Bot API: https://core.telegram.org/bots/api
- KakaoTalk Message API: https://developers.kakao.com/docs/en/kakaotalk-message/common
- KakaoTalk Message REST API: https://developers.kakao.com/docs/latest/en/kakaotalk-message/rest-api
- Kakao i Connect Message AlimTalk: https://docs.kakaoi.ai/kakao_i_connect_message/bizmessage_eng/api/api_reference/at/
- Google OAuth scopes: https://developers.google.com/identity/protocols/oauth2/scopes
- Google Gmail API scopes: https://developers.google.com/workspace/gmail/api/auth/scopes
- Google Sheets API scopes: https://developers.google.com/workspace/sheets/api/scopes
- Google Sheets values append: https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets.values/append
- Google Calendar events: https://developers.google.com/workspace/calendar/api/guides/create-events
- Google Chat incoming webhooks: https://developers.google.com/workspace/chat/quickstart/webhooks
- Discord OAuth2: https://docs.discord.com/developers/topics/oauth2
- Discord webhooks: https://docs.discord.com/developers/resources/webhook
- Discord API reference: https://docs.discord.com/developers/reference
- X Developer Platform overview: https://docs.x.com/overview
- X API introduction: https://docs.x.com/x-api/introduction
- X API rate limits: https://docs.x.com/x-api/fundamentals/rate-limits
- Naver Login API: https://developers.naver.com/docs/login/api/api.md
- Naver Login developer guide: https://developers.naver.com/docs/login/devguide/devguide.md
- Naver Papago NMT API: https://developers.naver.com/docs/nmt/reference/
- Notion API overview: https://developers.notion.com/guides/get-started/overview
- Notion capabilities: https://developers.notion.com/reference/capabilities
- Slack incoming webhooks: https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks
- Slack incoming-webhook scope: https://docs.slack.dev/reference/scopes/incoming-webhook

## Local Context

Autofolio already has partial channel adapters and UI placeholders:

- Telegram notification and command bot exist under `app/notification/telegram_*`.
- Discord webhook notifier exists under `app/notification/discord_notifier.py`.
- Email, Notion, and Google Sheets notifiers exist under `app/notification/`.
- Settings UI exposes channel connection forms, but Kakao/Naver are still generic token inputs.
- `TASK-038` covers watchlist/screener/alert expansion but excludes real-time push delivery.
- `TASK-041` covers capability flags and should absorb external-app/API capability vocabulary.

## Decision Vocabulary

| Status | Meaning |
|--------|---------|
| 승인 | Safe for local/mock/read-only/outbound notification/reporting without new external write authority beyond an already configured token. |
| 조건부 승인 | Allowed only with least-privilege scope, encrypted token storage, rate-limit handling, opt-in channel, and no order/money movement authority. |
| 보류/R3 | Requires Owner approval because it uses OAuth write scopes, public posting, inbound internet webhooks, account/private data, paid/billing, production publishing, or state-changing commands. |
| 기각 | Do not build for MVP because it creates public spam/automation, scraping/TOS risk, custody/money/order authority, broad private-data access, or irreversible external action. |

## Approval/Rejection Matrix

| Integration or API surface | Decision | Rationale |
|----------------------------|----------|-----------|
| Telegram outbound alerts | 승인 | Current code already supports token/chat based message sending. Keep for fills, errors, daily summary, watchlist alerts. |
| Telegram read-only commands | 승인 | Existing command bot supports status, PnL, positions, conditions, quote, and summaries with chat allowlist. |
| Telegram safety-direction command `/kill` | 조건부 승인 | Safe direction only, allowlist required, auditable event required. |
| Telegram `/approve`, auto-mode, order-like commands | 보류/R3 | State-changing remote control can enable automation; must require explicit Owner approval, confirm phrase, audit trail, and no live order shortcut. |
| Discord incoming webhook alerts | 승인 | Webhooks are simple outbound channel posts; current notifier already supports this shape. |
| Discord bot, slash commands, private channel reads | 조건부 승인 | Useful for IC/research threads, but OAuth scopes, bot permissions, and private data reads must be explicit. |
| Google Sheets portfolio/report mirror | 조건부 승인 | Useful for portfolio/journal mirroring; limit to selected spreadsheet and service account/OAuth with minimum scope. |
| Google Chat incoming webhook | 조건부 승인 | Good outbound alert target; hold if Workspace admin, private-space data, or inbound interaction is required. |
| Google Calendar review/reminder events | 조건부 승인 | Calendar event creation requires user OAuth write scope; OK only for owner-owned calendar and explicit schedule actions. |
| Gmail outbound report email | 조건부 승인 | Report sending is useful, but Gmail scopes can be sensitive or restricted; prefer SMTP/app password or minimal send-only path where available. |
| Gmail read/modify mailbox automation | 보류/R3 | Private email access and restricted scopes create high privacy/security review burden. |
| Google Drive broad access | 기각 for MVP | Broad Drive scopes are unnecessary for current product and increase data exposure. |
| KakaoTalk "send to me" notifications | 조건부 승인 | Kakao Message API supports self messaging; use `talk_message`, owner-only OAuth, and token refresh handling. |
| Kakao friend messaging | 보류/R3 | Friend messaging has service-user and permission constraints; avoid until multi-user or social features are approved. |
| Kakao AlimTalk/FriendTalk/business messaging | 보류/R3 | Business channel, template, contract, review, or paid provider requirements can apply. |
| Naver social login/profile | 조건부 승인 | Naver Login is OAuth based and useful for SSO; profile scope must be minimal. |
| Naver Papago/Search/news helper APIs | 조건부 승인 | Read-only research/translation/search helper is acceptable with API key limits and source attribution. |
| Naver Works organization APIs | 보류/R3 | Organization/workspace admin authorization is outside personal MVP. |
| X read-only monitoring or link preview | 조건부 승인 | X API is pay-per-use and rate-limited; useful only if cost/rate plan is explicit. |
| X automated posting/reposting/DMs | 보류/R3 | Public publishing and messaging are external irreversible actions with spam/reputation risk. |
| X scraping or unofficial API use | 기각 | TOS and reliability risk; use official API only. |
| Notion journal/report write to selected DB | 조건부 승인 | Current adapter shape is useful, but Notion capabilities and page/database permissions must be explicit. |
| Slack incoming webhook alerts | 조건부 승인 | Similar to Discord webhooks; approve only if workspace/channel is explicitly configured. |
| Public REST API for local Autofolio state | 조건부 승인 | Read-only local API can support dashboards and automation; internet exposure, auth, and rate limits are required before remote access. |
| Inbound webhooks from external services | 보류/R3 | Public callback endpoints require signature verification, replay protection, auth, and abuse handling. |
| Any external app command that places/cancels orders, changes broker credentials, toggles prod, moves money, or writes secrets | 기각 by default / R3 exception only | Crosses Autofolio R3 surfaces and may trigger irreversible financial action. |

## Implementation Implications

1. Build a channel capability matrix before adding more connectors.
2. Model each connector by capability, not by brand:
   - outbound notification
   - read-only command
   - state-changing command
   - report export
   - public publishing
   - OAuth login
   - OAuth user-data read
   - OAuth user-data write
   - inbound webhook
3. Require metadata for each connector:
   - auth type
   - scopes
   - secret storage location
   - rate-limit policy
   - payload sensitivity
   - user-visible destination
   - cost/billing exposure
   - audit log path
   - revocation path
4. Keep default MVP path:
   - Telegram + Discord + Email + Notion + Sheets outbound/reporting first.
   - Kakao/Naver/Google SSO only after OAuth/vault flow is explicit.
   - X only as catalog/optional read-only until cost and publishing policy are approved.

## Must Not Build Without Explicit Owner Approval

- External commands that submit/cancel broker orders.
- External commands that enable prod/live mode or disable safety gates.
- OAuth broad scopes for Gmail, Drive, private messages, or workspace admin data.
- Public social posting automation.
- Mass messaging, spam-like broadcasting, or marketing messages.
- Any connector that stores secrets outside the approved vault/env path.
- Any inbound webhook exposed to the internet without signature verification and replay defense.

## Uncertainty

- Exact X pricing, endpoint access, and free/paid limits change frequently.
- Kakao business messaging requirements differ by product and provider contract.
- Google OAuth verification requirements depend on selected scopes and publication model.
- Naver developer products are split across Naver Developers, Naver Cloud, and Naver Works.
- No external credentials were used or tested in this task.
