# Autofolio Membership Payment Evidence Policy

Status: draft policy, not applied to production
Updated: 2026-06-19T18:29:43+09:00
Related: TASK-087, TASK-103, TASK-108, TASK-110, TASK-111

## Purpose

This policy defines what Autofolio may retain when a verified signup request is
activated after manual bank-transfer review. It is intentionally a local policy
and validation asset. It does not connect to a bank, payment provider,
Supabase, OAuth provider, deploy target, or KIS account.

The machine-readable source is
`agents/project/MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.json`. The local gate is:

```powershell
python scripts/membership_payment_policy_gate.py --check
```

## Rule

Payment evidence must be minimal, masked, and tied to an audited approval
event. Autofolio should store only the fields needed to prove why an account
was activated, rejected, expired, refunded, or reviewed later.

Allowed evidence source types:

- `manual_bank_app_check`: the reviewer checks the bank app or statement
  outside Autofolio and records only the evidence type and minimal audit fields.
- `code_assisted_deposit_match`: Autofolio scans pasted text in memory and
  suggests a match by deposit code, amount, applicant name, and contact.
- `csv_import_review`: future production path only after retention review.
- `provider_receipt_reference`: future production path only after provider
  contract review.

Forbidden evidence in repository or routine app storage:

- raw bank statement text;
- full bank account number;
- resident registration number or card-like identifier;
- bank login credential;
- payment provider secret;
- unredacted customer identifier;
- freeform reviewer note containing private payment data.

## Retained Fields

The allowed production record shape is limited to:

- membership request id;
- target user id and actor user id;
- approval event id;
- evidence type;
- deposit code;
- amount and currency;
- source type and source reference;
- masked excerpt;
- confidence;
- recorded timestamp.

Raw pasted bank statement text remains request-local in the local prototype and
is not persisted by default.

## Launch Boundary

This policy only clears an R2 design/documentation gap. External paid users
still require separate evidence for:

- production data model and RLS mapping;
- retention period and deletion path;
- refund, receipt, tax, and accounting boundary;
- selected payment recognition method;
- staging privacy and non-disclosure tests.

