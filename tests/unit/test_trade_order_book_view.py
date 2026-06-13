from __future__ import annotations


def test_trade_view_renders_order_book_panel(tmp_path):
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "trade_order_book_app.py"
    script.write_text(
        """
import pandas as pd
import streamlit as st
from unittest.mock import patch

st.session_state["data_source"] = "backend"

from app.ui import backend
from app.ui.views import trade

snapshot = {
    "symbol": "005930",
    "market": "J",
    "current_price": 70000.0,
    "expected_price": 70100.0,
    "levels": [
        {"level": 1, "ask_price": 70100.0, "ask_quantity": 100, "bid_price": 70000.0, "bid_quantity": 200},
        {"level": 2, "ask_price": 70200.0, "ask_quantity": 300, "bid_price": 69900.0, "bid_quantity": 400},
    ],
}

with (
    patch.object(backend, "env", lambda: "paper"),
    patch.object(backend, "symbol_options", lambda: {"005930 · 삼성전자": "005930"}),
    patch.object(backend, "price", lambda symbol: 70000.0),
    patch.object(backend, "order_book_snapshot", lambda symbol: snapshot),
    patch.object(backend, "order_book_levels_df", lambda snapshot: pd.DataFrame(snapshot["levels"])),
    patch.object(backend, "disclosure_gate_state", lambda symbol: {"symbol": symbol, "blocked": False, "reason": ""}),
    patch.object(backend, "refresh_disclosure_gate", lambda symbol, days=1: {"symbol": symbol, "blocked": False, "reason": "", "disclosures": pd.DataFrame()}),
    patch.object(backend, "list_conditions", lambda: pd.DataFrame(columns=["id", "symbol", "status"])),
    patch.object(backend, "list_order_logs", lambda limit=100: pd.DataFrame()),
    patch.object(backend, "kis_today_orders", lambda: pd.DataFrame()),
    patch.object(backend, "circuit_breaker_status", lambda: {"triggered": False, "consecutive_failures": 0}),
    patch.object(backend, "get_flag", lambda key: key == "auto_trading_enabled"),
    patch.object(backend, "list_whitelist", lambda: pd.DataFrame([
        {"symbol": "005930", "name": "삼성전자", "market": "KRX", "role": "LARGE_CAP_TEST", "enabled": 1}
    ])),
):
    trade.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=15)

    assert not at.exception
    assert any(item.value == "호가창" for item in at.subheader)
    assert any(item.label == "예상평균가" for item in at.metric)
    assert len(at.dataframe) >= 1


def test_trade_ack_pending_message_renders_checkbox_outside_button(tmp_path):
    """Verify: when _trade_ack_pending_message is in session_state, the ack
    checkbox renders OUTSIDE the button block (i.e., on every run), so
    Streamlit does not clean it up between reruns.

    This is the structural fix for the infinite-loop bug: previously the
    checkbox was rendered only inside the 'if st.button(...)' block (which
    is False on reruns), causing Streamlit to delete the 'lv_comply_ack'
    widget state. Now the checkbox is rendered unconditionally when
    _trade_ack_pending_message is set.

    Coverage: checks that the checkbox widget IS present when the pending
    message session key is set, without clicking the save button.

    Limitation: this is a structural/rendering test, not a full two-step
    click-sequence test. A full "click save → get needs_acknowledgement →
    check box → click save again → saved" flow cannot be easily expressed
    with AppTest because the intermediate st.rerun() in the fixed code
    triggers a new run inside the button callback, and AppTest's simulation
    of that rerun does not carry forward the mock patches applied in the
    script's with-block.
    """
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "trade_ack_pending_app.py"
    script.write_text(
        """
import pandas as pd
import streamlit as st
from unittest.mock import patch

st.session_state["data_source"] = "backend"
# Pre-seed pending ack state — simulates the state after the first save
# returned needs_acknowledgement and triggered st.rerun().
st.session_state["_trade_ack_pending_message"] = "주의: 테스트 준수사항"
st.session_state["_trade_ack_context"] = "005930:BUY"

from app.ui import backend
from app.ui.views import trade

snapshot = {
    "symbol": "005930",
    "market": "J",
    "current_price": 70000.0,
    "expected_price": 70100.0,
    "levels": [],
}

with (
    patch.object(backend, "env", lambda: "paper"),
    patch.object(backend, "symbol_options", lambda: {"005930 · 삼성전자": "005930"}),
    patch.object(backend, "price", lambda symbol: 70000.0),
    patch.object(backend, "order_book_snapshot", lambda symbol: snapshot),
    patch.object(backend, "order_book_levels_df", lambda s: pd.DataFrame()),
    patch.object(backend, "disclosure_gate_state", lambda symbol: {"symbol": symbol, "blocked": False, "reason": ""}),
    patch.object(backend, "refresh_disclosure_gate", lambda symbol, days=1: {"symbol": symbol, "blocked": False, "reason": "", "disclosures": pd.DataFrame()}),
    patch.object(backend, "list_conditions", lambda: pd.DataFrame(columns=["id", "symbol", "status"])),
    patch.object(backend, "list_order_logs", lambda limit=100: pd.DataFrame()),
    patch.object(backend, "kis_today_orders", lambda: pd.DataFrame()),
    patch.object(backend, "circuit_breaker_status", lambda: {"triggered": False, "consecutive_failures": 0}),
    patch.object(backend, "get_flag", lambda key: key == "auto_trading_enabled"),
    patch.object(backend, "list_whitelist", lambda: pd.DataFrame([
        {"symbol": "005930", "name": "삼성전자", "market": "KRX", "role": "LARGE_CAP_TEST", "enabled": 1}
    ])),
):
    trade.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=15)

    assert not at.exception, f"App raised an exception: {at.exception}"
    # The ack checkbox must be rendered when _trade_ack_pending_message is set.
    ack_boxes = [c for c in at.checkbox if "주의사항을 확인" in c.label]
    assert ack_boxes, (
        "Expected the ack checkbox to be rendered when _trade_ack_pending_message "
        "is in session_state (fix for the infinite-loop bug: checkbox must render "
        "outside the button block so Streamlit does not clean up its widget state)."
    )
    # The warning text should also be visible.
    warning_texts = [w.value for w in at.warning]
    assert any("주의사항" in t for t in warning_texts), (
        f"Expected a warning containing '주의사항', got: {warning_texts}"
    )


def test_trade_ack_session_key_mirrors_checkbox(tmp_path):
    """Verify that checking the ack checkbox sets trade_ack_checked in
    session_state via the mirror logic (not via a deleted widget key).

    This directly validates the fix's persistence mechanism: the view mirrors
    the checkbox value into st.session_state['trade_ack_checked'] on every run,
    so even if the widget is later not rendered, the persistent key retains the
    user's choice.

    Coverage: simulates the checkbox being ticked on a second run (after the
    pending message is set) and confirms session_state['trade_ack_checked']=True.

    Limitation: relies on AppTest session state carry-over between .run() calls.
    The mock patches re-apply via the script context on each run, so we cannot
    intercept save_condition_with_gates arguments here. The caution_acknowledged
    read-through is tested separately by inspecting the key directly.
    """
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "trade_ack_mirror_app.py"
    script.write_text(
        """
import pandas as pd
import streamlit as st
from unittest.mock import patch

st.session_state["data_source"] = "backend"
st.session_state["_trade_ack_pending_message"] = "주의: 테스트"
st.session_state["_trade_ack_context"] = "005930:BUY"

from app.ui import backend
from app.ui.views import trade

snapshot = {
    "symbol": "005930",
    "market": "J",
    "current_price": 70000.0,
    "expected_price": 70100.0,
    "levels": [],
}

with (
    patch.object(backend, "env", lambda: "paper"),
    patch.object(backend, "symbol_options", lambda: {"005930 · 삼성전자": "005930"}),
    patch.object(backend, "price", lambda symbol: 70000.0),
    patch.object(backend, "order_book_snapshot", lambda symbol: snapshot),
    patch.object(backend, "order_book_levels_df", lambda s: pd.DataFrame()),
    patch.object(backend, "disclosure_gate_state", lambda symbol: {"symbol": symbol, "blocked": False, "reason": ""}),
    patch.object(backend, "refresh_disclosure_gate", lambda symbol, days=1: {"symbol": symbol, "blocked": False, "reason": "", "disclosures": pd.DataFrame()}),
    patch.object(backend, "list_conditions", lambda: pd.DataFrame(columns=["id", "symbol", "status"])),
    patch.object(backend, "list_order_logs", lambda limit=100: pd.DataFrame()),
    patch.object(backend, "kis_today_orders", lambda: pd.DataFrame()),
    patch.object(backend, "circuit_breaker_status", lambda: {"triggered": False, "consecutive_failures": 0}),
    patch.object(backend, "get_flag", lambda key: key == "auto_trading_enabled"),
    patch.object(backend, "list_whitelist", lambda: pd.DataFrame([
        {"symbol": "005930", "name": "삼성전자", "market": "KRX", "role": "LARGE_CAP_TEST", "enabled": 1}
    ])),
):
    trade.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=15)
    assert not at.exception

    # Tick the ack checkbox.
    ack_boxes = [c for c in at.checkbox if "주의사항을 확인" in c.label]
    assert ack_boxes, "Ack checkbox not found — precondition for this test"

    at2 = ack_boxes[0].check().run(timeout=15)
    assert not at2.exception

    # The persistent session key must reflect the checked value.
    assert at2.session_state["trade_ack_checked"] is True, (
        "trade_ack_checked must be True after ticking the ack checkbox — "
        "this key is the persistent carrier that survives reruns and is "
        "passed as caution_acknowledged to save_condition_with_gates."
    )
