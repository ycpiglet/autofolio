#!/usr/bin/env python3
"""Verify Streamlit backend views can read current paper transaction state."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

load_dotenv(ROOT / ".env")
os.environ["KIS_ENV"] = "paper"


VIEW_CALLS = {
    "home": "home.render()",
    "portfolio": "portfolio.render()",
    "trade": "trade.render()",
}
DEFAULT_TIMEOUT_SEC = 300


def build_view_script(call: str) -> str:
    return dedent(
        f"""
        import os
        from dotenv import load_dotenv
        load_dotenv('.env')
        os.environ['KIS_ENV'] = 'paper'
        import streamlit as st
        from app.ui import state
        from app.ui.views import home, portfolio, trade

        state.init_state()
        st.session_state['authed'] = True
        st.session_state['demo'] = False
        st.session_state['user'] = {{'name': 'QA', 'provider': 'paper'}}
        st.session_state['data_source'] = 'backend'

        {call}
        """
    )


def run_view(name: str, call: str, tmp_path: Path, timeout: int) -> dict:
    script = tmp_path / f"{name}_paper_ui_sync.py"
    script.write_text(build_view_script(call), encoding="utf-8")
    at = AppTest.from_file(str(script)).run(timeout=timeout)
    page_text = " ".join(str(node.value) for node in [*at.title, *at.header, *at.subheader, *at.markdown])
    metric_labels = [metric.label for metric in at.metric]
    return {
        "ok": not bool(at.exception),
        "exceptions": [str(exc)[:180] for exc in at.exception],
        "metrics": metric_labels,
        "buttons": [button.label for button in at.button][:16],
        "dataframes": len(at.dataframe),
        "contains_recent_fills": "최근 체결" in page_text,
        "contains_holdings": (
            "보유 현황" in page_text
            or "보유 종목" in page_text
            or "보유 종목" in metric_labels
        ),
        "contains_order_controls": "엔진 1회 실행" in " ".join(button.label for button in at.button),
    }


def main(argv: list[str] | None = None) -> int:
    timeout = int(argv[0]) if argv else DEFAULT_TIMEOUT_SEC
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        results = {
            name: run_view(name, call, tmp_path, timeout)
            for name, call in VIEW_CALLS.items()
        }
    output = {
        "env": os.environ.get("KIS_ENV"),
        "results": results,
        "ok": all(item["ok"] for item in results.values()),
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 0 if output["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
