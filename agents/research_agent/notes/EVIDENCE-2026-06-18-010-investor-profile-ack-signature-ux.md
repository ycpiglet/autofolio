---
type: evidence
id: EVIDENCE-2026-06-18-010
title: Investor profile acknowledgement and signature UX
created_at: 2026-06-18T23:40:43+09:00
owner: QA
related_task: TASK-086
tags: [profile, onboarding, ui, safety, qa]
status: pass
redaction: no account number, token, secret, broker order payload, or raw production data recorded
---

# Investor profile acknowledgement and signature UX

## What Changed

- Missing required answers now mark the relevant question blocks with `data-invalid`, shake, gray pulse, stronger border, and scroll-to-first-missing behavior.
- The signature question now requires:
  - typed name,
  - exact phrase `위 항목을 모두 이해했습니다.`,
  - direct canvas signature saved as PNG data URL,
  - signed timestamp.
- Backend validation rejects missing signature images and wrong confirmation text.
- E2E test draws on the canvas and verifies the submitted payload contains the phrase and data URL.

## Safety Contract

| Contract | State |
|----------|-------|
| Profile/onboarding surface only | pass |
| No KIS/order/risk path change | pass |
| No secret/account mutation | pass |
| No production DB migration | pass |
| Server-side validation mirrors UI validation | pass |

## Verification

| Command | Result |
|---------|--------|
| `.venv\Scripts\python.exe -m py_compile app\services\investor_profile.py app\api\routers\profile.py app\api\schemas\__init__.py` | OK |
| `.venv\Scripts\python.exe -m pytest tests/api/test_profile_survey.py -q` | 12 passed, 4 warnings |
| `npm run lint` | pass |
| `npm run build` | pass, `/onboarding/investor-profile` generated |
| `npm run test:e2e -- e2e/investor-profile.spec.ts --reporter=line` | 2 passed |

## Watch

- This is an internal acknowledgement UX, not a certified e-signature or identity verification provider.
- If the app later needs legal-grade e-signature evidence, store a separately versioned acknowledgement artifact and avoid oversized inline data URLs.
