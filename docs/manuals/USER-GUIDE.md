---
title: Autofolio User Guide
description: Public product guide for the app screens and trading workflow.
audience: user
visibility: public
ui_section: getting-started
risk_level: low
requires_ack: false
order: 20
version: manuals-v1
---

# Autofolio User Guide

Autofolio is a personal portfolio and trading automation interface for Korean
securities accounts connected through Korea Investment Open API.

## Main Screens

- Home shows portfolio status, recent activity, and warnings.
- Portfolio shows holdings, allocation, profit and loss, and account summary.
- Trade lets you save conditional orders and run the engine once.
- History shows orders, fills, and audit events.
- Analysis shows prices, disclosures, simulations, and backtests.
- Agents shows research assistants and manual proposal flows.
- Manuals shows the product guide, setup steps, and safety rules.
- Settings manages account, profile, risk limits, and connection status.

## Operating Modes

- `mock`: safe local mode. No broker account or real order is used.
- `paper`: Korea Investment paper account. Use this before live trading.
- `prod`: real account. Requires explicit Owner acknowledgement and extra checks.

## Basic Flow

1. Complete the investor profile.
2. Connect KIS in paper mode.
3. Run read-only checks.
4. Run paper order smoke tests.
5. Review audit events and engine health.
6. Switch to prod only after the paper path is clean.

## What Autofolio Does Not Promise

Autofolio does not guarantee profit, prevent all losses, replace investment
judgment, or remove broker/API/network risk.
