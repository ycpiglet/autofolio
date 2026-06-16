---
type: evidence
id: EVIDENCE-2026-06-17-001
status: 완료
owner: Lead Engineer
related_task: TASK-074
created: 2026-06-17
created_at: 2026-06-17T01:33:00+09:00
tags: [bug, onboarding, profile, ui]
---

# Investor Survey Public Load Bug

## 6W1H

- Who: Owner reported "설문을 불러오지 못했다고 하네"; Codex reproduced and fixed.
- When: 2026-06-17T01:33:00+09:00.
- Where: `GET /api/profile/survey`, Next `/onboarding/investor-profile`, PR #91 branch `feat/investor-profile-survey`.
- What: First-time users without an `af_session` cookie saw `설문을 불러오지 못했습니다` instead of the survey.
- Why: The survey definition endpoint required `require_session` even though the definition is static/public and contains no user data. The page therefore received 401 before questions could render.
- How: Removed the session dependency from `GET /api/profile/survey`, kept `POST /api/profile/survey` behind `require_owner_csrf`, added an anonymous-load regression test, and clarified the save-time unauthenticated message.
- Impact: Public survey questions now render before login/guest session. Saving answers still requires an owner session and CSRF; profile gates for trade/engine actions are unchanged.

## Evidence

- Broken reproduction: `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:3000/api/profile/survey -SkipHttpErrorCheck` returned `401 Unauthorized` with `{"detail":"Not authenticated"}` before the patch.
- Fixed API check: same command returned `200 OK` with `version=investor-profile-v1` after the patch.
- Browser check: after clearing cookies, `/onboarding/investor-profile` rendered survey questions including `투자 목적` and did not render `설문을 불러오지 못했습니다`.
- Focused API test: `.\\.venv\\Scripts\\python.exe -m pytest tests/api/test_profile_survey.py -q` -> 10 passed, 2 warnings.
- Frontend checks: `npm run lint` -> pass; `npm run build` -> successful; `npx playwright test e2e/investor-profile.spec.ts` -> 1 passed.

## Remaining Notes

- Anonymous users can read the survey definition only. Persisting responses still requires login/guest-to-owner flow according to the existing auth model.
- Unauthenticated pages may still show protected status/profile API 401s in browser devtools because the shared `AppShell` status bar reads protected runtime state. That is separate from the survey definition load failure.
