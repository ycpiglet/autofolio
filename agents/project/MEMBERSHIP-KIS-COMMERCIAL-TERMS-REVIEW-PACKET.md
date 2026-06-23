# Membership KIS Commercial Terms Review Packet

Status: review packet only, not clearance
Owner: Compliance Officer
Last updated: 2026-06-19T22:16:54+09:00
Related tasks: TASK-087, TASK-125

## Purpose

This packet records the official-source KIS Open API terms and partnership
questions that block external/member staging or paid launch. It is not legal
advice, KIS approval, exchange-data approval, or launch clearance.

Machine-readable source:

- `agents/project/MEMBERSHIP-KIS-COMMERCIAL-TERMS-REVIEW-PACKET.json`

Local gate:

```powershell
python scripts/membership_kis_terms_review_gate.py --check
```

## Official Source Basis

| Source | Use |
|--------|-----|
| KIS Developers 제휴안내 | Third-party service, market-data, and order API partnership risk. |
| KIS Developers 제휴 API 시작하기 | User account-auth/token process and partner-side membership responsibility. |
| KIS 오픈 API 서비스 이용 약관(제휴 이용기관_사용자), 2025-06-04 | Defines affiliate institution/user terms, user consent, annual reapplication, and suspension grounds. |
| eFriend Expert Open API service page | Shows the self-owned-account algorithm/program use case. |
| FSC/FSS robo-advisor interpretation | Useful regulatory context, but not Autofolio clearance. |

## Current Finding

Autofolio's v1 position is "user-controlled software membership": users keep
their own account authority, settings, approvals, LLM/SNS/KIS keys, and risk
responsibility. That position is directionally safer than discretionary
operation, but KIS official materials do not currently prove that a paid hosted
multi-user service may use personal KIS API paths without KIS/legal approval.

## Blocking Questions

| ID | Question | Reviewer |
|----|----------|----------|
| third_party_service_boundary | Does a paid hosted membership service where each user connects their own KIS account/key count as third-party service requiring KIS partnership or approval? | KIS or legal professional |
| software_only_vs_hosted_service | Is the answer different if Autofolio is distributed as user-run local software instead of a hosted service? | KIS or legal professional |
| market_data_display_rights | Can Autofolio display KIS-provided market data inside a paid member screen, and what KRX/overseas information-use agreements are required? | KIS or exchange-data/legal professional |
| order_api_user_approval_model | Can a user-controlled workflow submit orders through each user's own KIS authority if all decisions and approvals remain under the user? | KIS or financial-regulatory legal professional |
| credential_storage_and_token_handling | What storage, refresh, revocation, password-omission, consent, and audit requirements apply to user-owned KIS tokens/credentials? | KIS, security, legal |
| investment_advice_and_discretionary_boundary | Which recommendations, signals, automation, or default settings would become advice, paid signal, or discretionary management? | Financial-regulatory legal professional |
| rate_limit_and_load_controls | What call-rate, load, market-hours, retry, and emergency fallback controls are required for multi-user operation? | KIS technical or partnership reviewer |

## Launch Policy

- Keep `KIS_ENV=mock` for external/member staging.
- Do not activate real KIS credentials, order APIs, or KIS market-data display
  for external members until Owner/KIS/legal confirmation exists.
- Do not claim paid KIS production integration, market-data rights, order API
  support, or commercial readiness in marketing material.
- Keep `can_launch=false` while KIS commercial/multi-user clearance is missing.

## Forbidden In This Packet

- No KIS login or KIS Developers login.
- No KIS contact, partnership proposal, or external submission.
- No KIS credential collection, storage, validation, or rotation.
- No `app/brokers/kis`, OrderFlow, SafetyChecker, risk, deploy, or production
  DB changes.
- No legal/tax/securities final advice.

## Handoff

TASK-087 can use this packet as local R2 evidence that the KIS commercial terms
blocker has been researched and converted into exact Owner/KIS/legal questions.
It does not resolve the blocker. Actual launch, deploy, KIS credential
activation, market-data display, and order API support remain Owner/R3.
