---
type: qa_decision_record
id: EXTERNAL-APP-API-DECISION-RECORD
status: active
created: 2026-06-13
created_at: 2026-06-13T02:06:53+09:00
owner: QA
related_task: TASK-043
automation: catalog-only
---

# EXTERNAL-APP-API-DECISION-RECORD

This record governs external application/API integration decisions for Autofolio.

## Policy

External integrations are approved by capability and permission class, not by app name.
No connector is "fully supported" unless every required capability has an evidence link,
scope boundary, secret-storage plan, rate-limit behavior, audit path, and revocation path.

## Capability Classes

| Capability | Default Status | Notes |
|------------|----------------|-------|
| Outbound notification | approved | Telegram/Discord/Email/Notion/Sheets-style alert or report delivery. |
| Read-only command | approved | Status, PnL, positions, quotes, conditions, reports. Requires allowlist for chat apps. |
| Safety-direction command | conditional | `/kill` or pause-like safe actions only; audit required. |
| State-changing automation command | r3-hold | `/approve`, auto-mode toggle, prod toggle, strategy activation, or risk setting changes. |
| Broker order or cancel command | rejected-by-default | R3 exception only; never enabled by channel integration by default. |
| Report export/write | conditional | Sheets, Notion, Calendar, Email write paths require least privilege and explicit destination. |
| OAuth social login | conditional | Google/Kakao/Naver login must use minimal profile/email scopes. |
| OAuth private data read/write | r3-hold | Gmail, Drive, private messages, workspace admin, and broad profile scopes. |
| Public social posting | r3-hold | X, Discord public channel, Slack workspace posting beyond owner-controlled channels. |
| Inbound webhook | r3-hold | Requires signature verification, replay defense, auth, and abuse handling. |
| Scraping/unofficial API | rejected | Use official APIs only. |
| Mass messaging/marketing | rejected | Outside personal MVP and creates compliance/spam risk. |

## App Decisions

| App/API | Approved | Conditional | R3 Hold | Rejected |
|---------|----------|-------------|---------|----------|
| Telegram | outbound alerts, read-only commands | `/kill` with allowlist/audit | `/approve`, auto-mode, order-like remote commands | unauthenticated or broadcast-style control |
| Discord | incoming webhook alerts | bot/slash command for owner server | private reads, state-changing commands | broad server scraping |
| Google Sheets | none by brand | portfolio/report mirror to selected sheet | broad Drive scope | all-Drive access for MVP |
| Google Chat | none by brand | incoming webhook alerts | interactive bot/private-space read | workspace-wide automation |
| Google Calendar | none by brand | owner calendar reminders | calendar automation with broad write scope | hidden/background schedule mutation |
| Gmail | none by brand | outbound reports with minimal send path | read/modify/restricted scopes | mailbox automation for MVP |
| KakaoTalk | none by brand | "send to me" owner notification | friend messaging, AlimTalk/FriendTalk | marketing/broadcast messaging |
| Naver | none by brand | social login/profile, Papago/search helper | Naver Works org APIs | unofficial extraction |
| X | none by brand | optional read-only monitoring if paid/rate policy exists | posting/reposting/DM automation | scraping/unofficial API |
| Notion | none by brand | selected DB journal/report write | workspace-wide read/write | broad workspace sync |
| Slack | none by brand | incoming webhook alerts | bot/private channel reads | workspace scraping |

## Task Mapping

| Decision Surface | Task |
|------------------|------|
| This external app/API record | TASK-043 |
| Owner setup manual | TASK-044; `docs/EXTERNAL_APP_API_OWNER_MANUAL.md` |
| Capability vocabulary and supported labels | TASK-041 |
| Watchlist/screener alert preview | TASK-038 |
| Portfolio/report export candidates | TASK-040 |
| Backtest/research reports | TASK-039 |
| Live order/risk/prod toggles | Existing R3 order/risk tasks only |

## Required Assertions For Future Tests

1. Unsupported or R3-held connectors must not be displayed as fully supported.
2. Connector cards must show auth type, scope, destination, status, and last verification.
3. Read-only commands must not call broker order, cancel, prod, or risk-policy mutation paths.
4. `/kill` is the only safety-direction command that may be lower risk than other state changes.
5. `/approve`, auto-mode, prod-mode, order, cancel, credential, and withdrawal commands are blocked unless an explicit R3 task authorizes them.
6. OAuth connectors must use least-privilege scopes and must not persist tokens in plain text.
7. Inbound webhook support must have signature/replay tests before any public endpoint is enabled.
8. Future connector implementation TASKs must link the Owner setup manual and name the prepared account, scope, destination, secret storage path, quota/cost decision, and revocation path without recording the real secret.
