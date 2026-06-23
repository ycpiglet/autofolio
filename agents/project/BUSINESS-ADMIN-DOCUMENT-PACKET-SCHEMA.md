# Business Admin Document Packet Schema

Status: foundation-only-not-submission-ready
Owner: Regulatory Admin
Last updated: 2026-06-19T22:31:45+09:00
Related tasks: TASK-092, TASK-093, TASK-094, TASK-127

## Purpose

This schema is the reusable contract for future business-registration,
admin-filing, policy, startup-support, and HWPX document packets. It exists so
Regulatory Admin can prepare structured packets without collecting private Owner
identity data or crossing official submission boundaries.

This does not complete TASK-094. It prepares TASK-094 by defining the packet
shape, validation expectations, and forbidden actions.

## Boundary

Allowed:

- Official-source source register.
- Placeholder-safe field map.
- Markdown-first packet structure.
- Future HWPX fixture requirements.
- Local validation gate and focused tests.

Forbidden:

- Hometax, Government24, Hancom account, KIS, bank, or payment-provider login.
- Authentication, signature, payment, upload, submission, correction, or
  withdrawal.
- Resident registration number, certificate, bank account, KIS key, API secret,
  customer data, or signed private filing copy in the repo.
- Final legal, tax, accounting, securities, KIS, or regulatory advice.
- Final HWPX/PDF generation from a target official form before the target form
  and private-data path are selected.

## Packet Lifecycle

1. `draft_schema`
2. `official_source_refreshed`
3. `owner_non_sensitive_facts_collected`
4. `owner_private_facts_supplied_outside_repo`
5. `markdown_review_draft_generated`
6. `optional_hwpx_fixture_generated`
7. `professional_review_needed`
8. `owner_review`
9. `owner_submitted`
10. `archived`

## Required Packet Fields

| Field | Meaning |
|-------|---------|
| `packet_id` | Stable document packet ID, such as `DOC-PACKET-YYYY-MM-DD-NNN`. |
| `procedure` | Business registration, policy packet, startup-support application, etc. |
| `jurisdiction` | Korea, national/local agency, or target issuer context. |
| `status` | Draft, Owner review, professional review, ready for Owner submission, submitted by Owner, archived. |
| `source_basis` | Official URLs and checked dates. |
| `checked_at` | Timestamp from `python scripts/now.py`. |
| `owner_non_sensitive_business_data` | Product and business facts safe to keep in repo. |
| `owner_private_data_placeholders` | Placeholder labels only; actual private values stay outside repo. |
| `agent_drafted_text` | Draft text derived from approved business-plan sections. |
| `required_attachments` | Checklist of required attachments, not private files. |
| `generated_artifacts` | Markdown first; optional DOCX/PDF/HWPX later. |
| `owner_only_steps` | Login, authentication, signature, payment, upload, final review, submission. |
| `review_gates` | Tax accountant, attorney, FSC/FSS, KIS, privacy, refund, terms. |
| `forbidden_repo_data` | Private data and secrets that must not be stored. |
| `verification` | Local gate and focused test commands. |

## HWPX Direction

HWPX work must stay template-driven and reviewable:

- structured JSON/YAML source data;
- reviewable Markdown first;
- target official form selected before generation;
- template fixture required;
- XML diff required;
- human review required;
- no auto-submit path.

## Candidate Packets

| Packet | Status | Output |
|--------|--------|--------|
| Business registration intake placeholder | Candidate after Owner chooses business type | Field map and Markdown review draft first; HWPX only after target form fixture. |
| Membership terms/privacy/refund placeholder | Candidate after policy scope decision | Policy source packet for professional review, not public terms. |
| Startup-support business-plan placeholder | Candidate after program selection | Transform from `BUSINESS-PLAN.md` into selected program form. |

## Verification

- `python scripts/business_admin_document_packet_schema_gate.py --check`
- `python -m pytest tests/unit/test_business_admin_document_packet_schema_gate.py -q`

## Handoff

TASK-094 can use this schema after the Owner chooses business type, target form
or procedure, private-data handling path, and review boundary. Until then,
TASK-094 remains blocked.
