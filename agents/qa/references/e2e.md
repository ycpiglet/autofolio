# QA E2E Reference

This project uses Streamlit AppTest and focused Python tests as the default
local E2E path. Browser screenshots are useful evidence when a real browser is
available, but they are not required when the environment blocks browser
automation and AppTest covers the target behavior.

## Standard Commands

```powershell
pytest tests/unit/test_beta_cycle001_ui_smoke.py
pytest tests/unit/test_home_market_indices_view.py tests/unit/test_trade_order_book_view.py
pytest tests/unit/test_analysis_intraday_view.py tests/unit/test_history_kis_view.py
pytest tests/unit/test_alerts_disclosure_view.py tests/unit/test_portfolio_dividend_view.py
```

For local UI health:

```powershell
streamlit run app/ui/autofolio_app.py --server.address=127.0.0.1 --server.port=8501
Invoke-WebRequest -Uri http://127.0.0.1:8501/ -UseBasicParsing
```

## Evidence Rules

- Record the command, result, and affected screen or API path.
- If Browser/Playwright is unavailable, record the reason and use AppTest plus
  HTTP/API checks.
- Do not click order execution controls in `paper` or `prod` unless the Owner
  explicitly approves that exact run.
- For visual regressions, save before/after screenshots when the browser surface
  is available.
