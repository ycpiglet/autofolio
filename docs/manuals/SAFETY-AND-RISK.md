---
title: Safety And Risk Acknowledgement
description: Risk warning, non-liability statement, and live-trading consent.
audience: all
visibility: public
ui_section: safety
risk_level: critical
requires_ack: true
ack_kind: live_trading_risk_v1
order: 50
version: live-trading-risk-v1
---

# Safety And Risk Acknowledgement

Autofolio is automation software. It is not investment advice, a profit
guarantee, or a loss-prevention system.

## You Must Understand

- Securities trading can lose money.
- Automated trading can submit an order you later regret.
- Broker API errors, network failures, scheduler issues, stale data, and queue
  buildup can happen.
- A market order can fill at a worse price than expected.
- A limit order may not fill or may need cancellation.
- Autofolio can reduce operational risk, but it cannot remove market risk.

## Responsibility Boundary

The user remains responsible for account setup, credential handling, trading
decisions, and final live-trading approval. Autofolio records whether an action
was initiated by the user, an agent, or a scheduler, but the Owner must review
and maintain the automation rules before allowing live trading.

## Required Live-Trading Safeguards

- Investor profile completed.
- Risk acknowledgement recorded.
- Owner re-authentication or stronger authenticator step used before critical
  actions.
- Kill switch visible and working.
- Auto trading default OFF.
- Order source and audit timeline visible.
- Engine health shows no stale processing conditions or duplicate intent risk.

## Authenticator Recommendation

Use a TOTP authenticator such as Microsoft Authenticator, Google Authenticator,
1Password, or another trusted password manager. Autofolio v1 records and
recommends this second factor; full TOTP enforcement is a hardening task before
unattended live automation.

## Acknowledgement Phrase

For live trading, confirm that you understand the loss and automation risk and
that final responsibility remains with the account owner.
