# QA E2E Reference

This project uses Next.js Playwright specs and focused Python API/service tests
as the default local E2E path. The Streamlit UI was retired in TASK-049 and is
kept only under `archive/streamlit_ui/` for reference.

## Standard Commands

```powershell
cd web
npm run test:e2e -- e2e/demo-walkthrough.spec.ts
npm run test:e2e -- e2e/login.spec.ts e2e/phase3.spec.ts e2e/phase4.spec.ts e2e/analysis.spec.ts
```

For local UI health:

```powershell
run_api.bat
run_frontend.bat
Invoke-WebRequest -Uri http://127.0.0.1:8000/api/health -UseBasicParsing
Invoke-WebRequest -Uri http://127.0.0.1:3000/login -UseBasicParsing
```

## Evidence Rules

- Record the command, result, and affected screen or API path.
- If Browser/Playwright is unavailable, record the reason and use HTTP/API
  checks plus focused service tests.
- Do not click order execution controls in `paper` or `prod` unless the Owner
  explicitly approves that exact run.
- For visual regressions, save before/after screenshots when the browser surface
  is available.
