"""AppTest for app/ui/views/watchlist.py.

Follows the pattern from tests/unit/test_alerts_disclosure_view.py.
"""
from __future__ import annotations

import pandas as pd
import pytest


def test_watchlist_view_renders_without_error(tmp_path):
    """View renders all 3 tabs without exception."""
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "test_watchlist_app.py"
    script.write_text(
        """
import streamlit as st
import pandas as pd
from unittest.mock import patch
import app.services.watchlist_screener as svc
from app.ui import backend
from app.ui.views import watchlist

with patch.object(svc, 'list_watchlists', return_value=[]), \
     patch.object(svc, 'list_screeners', return_value=[]), \
     patch.object(backend, 'list_whitelist', return_value=pd.DataFrame(columns=["symbol", "name", "market", "role", "enabled"])), \
     patch.object(backend, 'symbol_options', return_value={}):
    watchlist.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=15)
    assert not at.exception


def test_alert_tab_has_dryrun_disclaimer(tmp_path):
    """The alert tab must show the dry-run disclaimer warning text."""
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "test_watchlist_dryrun.py"
    script.write_text(
        """
import streamlit as st
import pandas as pd
from unittest.mock import patch
import app.services.watchlist_screener as svc
from app.ui import backend
from app.ui.views import watchlist

with patch.object(svc, 'list_watchlists', return_value=[]), \
     patch.object(svc, 'list_screeners', return_value=[]), \
     patch.object(backend, 'list_whitelist', return_value=pd.DataFrame(columns=["symbol", "name", "market", "role", "enabled"])), \
     patch.object(backend, 'symbol_options', return_value={}):
    watchlist.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=15)
    assert not at.exception

    # The alert tab warning contains "dry-run" and "주문 제출"
    warning_texts = [w.value for w in at.warning]
    assert any("dry-run" in t or "주문 제출" in t for t in warning_texts), (
        f"Expected dry-run disclaimer in warnings, got: {warning_texts}"
    )


def test_watchlist_view_renders_with_saved_watchlist(tmp_path):
    """View renders correctly when there is one saved watchlist."""
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "test_watchlist_with_data.py"
    script.write_text(
        """
import streamlit as st
import pandas as pd
from unittest.mock import patch
import app.services.watchlist_screener as svc
from app.ui import backend
from app.ui.views import watchlist

fake_watchlist = [
    {
        "id": "test-id-001",
        "name": "반도체 관심",
        "symbols": ["005930", "000660"],
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
    }
]

with patch.object(svc, 'list_watchlists', return_value=fake_watchlist), \
     patch.object(svc, 'list_screeners', return_value=[]), \
     patch.object(backend, 'list_whitelist', return_value=pd.DataFrame(
         [{"symbol": "005930", "name": "삼성전자", "market": "KOSPI", "role": "core", "enabled": True}]
     )), \
     patch.object(backend, 'symbol_options', return_value={"005930 · 삼성전자": "005930"}):
    watchlist.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=15)
    assert not at.exception


def test_watchlist_view_renders_with_saved_screener(tmp_path):
    """View renders correctly when there is one saved screener preset."""
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "test_watchlist_screener.py"
    script.write_text(
        """
import streamlit as st
import pandas as pd
from unittest.mock import patch
import app.services.watchlist_screener as svc
from app.ui import backend
from app.ui.views import watchlist

fake_screener = [
    {
        "id": "sc-id-001",
        "name": "반도체 필터",
        "filters": {"price_min": 50000.0, "sector": "IT"},
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
    }
]

with patch.object(svc, 'list_watchlists', return_value=[]), \
     patch.object(svc, 'list_screeners', return_value=fake_screener), \
     patch.object(backend, 'list_whitelist', return_value=pd.DataFrame(columns=["symbol", "name", "market", "role", "enabled"])), \
     patch.object(backend, 'symbol_options', return_value={}):
    watchlist.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=15)
    assert not at.exception


def test_no_order_submission_reachable_from_view():
    """The view module must not import from order_flow or any order-submission path.

    Checks import AST only (not docstring/comment mentions) — the real risk
    is a runtime dependency, not a word appearing in a comment.
    """
    import ast
    import inspect

    from app.ui.views import watchlist

    source = inspect.getsource(watchlist)
    tree = ast.parse(source)
    forbidden = {"order_flow", "OrderFlow", "place_order", "run_engine_once", "add_condition"}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = (
                [node.module or ""] if isinstance(node, ast.ImportFrom)
                else [alias.name for alias in node.names]
            )
            for name in names:
                for f in forbidden:
                    assert f not in (name or ""), (
                        f"Forbidden import '{f}' found in watchlist view"
                    )
