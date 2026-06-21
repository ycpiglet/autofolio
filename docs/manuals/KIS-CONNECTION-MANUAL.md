---
title: KIS Connection Manual
description: Step-by-step Korea Investment Open API setup checklist.
audience: owner
visibility: private
ui_section: connections
risk_level: high
requires_ack: false
order: 30
version: manuals-v1
official_sources: ["https://apiportal.koreainvestment.com/about-howto", "https://apiportal.koreainvestment.com/apiservice", "https://github.com/koreainvestment/open-trading-api"]
---

# KIS Connection Manual

Use official Korea Investment sources as the current setup authority:

- KIS Developers service guide: https://apiportal.koreainvestment.com/about-howto
- KIS API documentation: https://apiportal.koreainvestment.com/apiservice
- Official sample repository: https://github.com/koreainvestment/open-trading-api

## Owner Preparation

1. Open or confirm a Korea Investment securities account.
2. Register the account with the Korea Investment ID used for Open API.
3. Apply for Open API service in KIS Developers.
4. Issue separate app key and app secret values for paper and prod.
5. Confirm the account product code, usually `01` for a domestic stock account.
6. Store secrets only in local environment files or the configured vault.

## Autofolio Environment Names

Use placeholders only in documentation:

- `KIS_ENV=mock|paper|prod`
- `KIS_PAPER_APP_KEY`
- `KIS_PAPER_APP_SECRET`
- `KIS_PAPER_ACCOUNT_NO`
- `KIS_PAPER_ACCOUNT_PRODUCT_CODE`
- `KIS_PROD_APP_KEY`
- `KIS_PROD_APP_SECRET`
- `KIS_PROD_ACCOUNT_NO`
- `KIS_PROD_ACCOUNT_PRODUCT_CODE`

Never paste raw secrets, account numbers, cash balances, or broker payloads into
manuals, task records, reports, screenshots, or chat.

## Verification Sequence

1. Start with `KIS_ENV=mock`.
2. Run `python scripts/kis_token_smoke.py`.
3. Run read-only paper/prod capability smoke before any order test.
4. Run paper minimal smoke during market hours.
5. Run prod minimal smoke only after same-day paper pass evidence exists.

## Prod Boundary

Prod connection means real-account access. Do not enable automated live trading
until the risk acknowledgement, re-authentication gate, kill switch, audit event
stream, and engine health dashboard are all working.
