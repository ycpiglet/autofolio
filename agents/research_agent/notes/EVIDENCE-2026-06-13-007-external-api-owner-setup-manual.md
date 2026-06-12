---
type: evidence
id: EVIDENCE-2026-06-13-007
date: 2026-06-13
recorded_at: 2026-06-13T07:58:00+09:00
author: Doc Steward + Research Agent (Codex)
related_task: TASK-044
related_manual: docs/EXTERNAL_APP_API_OWNER_MANUAL.md
scope: owner setup requirements for external app/API integrations
---

# EVIDENCE-2026-06-13-007 External API Owner Setup Manual

## Question

What must the Owner personally prepare before Autofolio uses external applications
and APIs such as Telegram, Kakao, Google, X, Naver, Discord, Notion, Slack, and
email?

## Sources

Official or primary sources reviewed:

- Telegram Bot Features: https://core.telegram.org/bots/features
- Telegram Bot API: https://core.telegram.org/bots/api
- Kakao app setup: https://developers.kakao.com/docs/latest/en/getting-started/app
- Kakao Login prerequisites: https://developers.kakao.com/docs/latest/en/kakaologin/prerequisite
- Kakao Login REST API: https://developers.kakao.com/docs/latest/en/kakaologin/rest-api
- Kakao Message REST API: https://developers.kakao.com/docs/latest/en/message/rest-api
- Google Cloud project setup: https://developers.google.com/workspace/guides/create-project
- Google OAuth web server flow: https://developers.google.com/identity/protocols/oauth2/web-server
- Gmail API scopes: https://developers.google.com/workspace/gmail/api/auth/scopes
- Google Sheets authorization: https://developers.google.com/workspace/sheets/api/guides/authorizing
- Google service accounts: https://docs.cloud.google.com/iam/docs/service-accounts-create
- Google Chat incoming webhooks: https://developers.google.com/workspace/chat/quickstart/webhooks
- Google Calendar event creation: https://developers.google.com/workspace/calendar/api/guides/create-events
- Discord webhooks: https://docs.discord.com/developers/resources/webhook
- Discord OAuth2: https://docs.discord.com/developers/topics/oauth2
- Discord bot quick start: https://docs.discord.com/developers/quick-start/getting-started
- X API introduction: https://docs.x.com/x-api/introduction
- X OAuth 2.0 user access token: https://docs.x.com/x-api/fundamentals/authentication/oauth-2-0/user-access-token
- X API rate limits: https://docs.x.com/x-api/fundamentals/rate-limits
- Naver Login developer guide: https://developers.naver.com/docs/login/devguide/devguide.md
- Naver Login API: https://developers.naver.com/docs/login/api/api.md
- Naver Papago NMT API: https://developers.naver.com/docs/nmt/reference/
- Naver Open API list: https://developers.naver.com/docs/common/openapiguide/apilist.md
- Notion quickstart: https://developers.notion.com/guides/get-started/quick-start
- Notion capabilities: https://developers.notion.com/reference/capabilities
- Slack incoming webhooks: https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks/
- Slack tokens: https://docs.slack.dev/authentication/tokens/

## Summary

- Owner-only work is account creation, developer console registration, API key/token
  issuance, OAuth consent, provider review, billing/plan selection, and secret entry.
- Agent-safe work is manual creation, variable naming, `.env.example` updates,
  adapter implementation after approval, local validation, and tests.
- Low-risk first lane is Telegram outbound/read-only and Discord webhook alerts.
- OAuth write scopes, mailbox/drive/private-data reads, public posting, inbound
  public webhooks, and remote trading control remain R3.
- No external credentials were created, requested, stored, or tested in this task.

## Implication

`docs/EXTERNAL_APP_API_OWNER_MANUAL.md` is the Owner-facing preflight manual for
future connector work. Future connector TASKs should link it and require a filled
Owner preparation packet before implementation starts.

## Uncertainty

Provider pricing, quotas, review requirements, and API access tiers can change.
Before implementing a specific connector, re-check that provider's current official
console and docs.
