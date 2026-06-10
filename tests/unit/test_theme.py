"""Tests for pure helper functions in app/ui/theme.py (no streamlit state needed)."""
import pytest


def test_fmt_won():
    from app.ui.theme import fmt_won
    assert fmt_won(1000000.0) == "₩1,000,000"
    assert fmt_won(0.0) == "₩0"
    assert fmt_won(1234567.89) == "₩1,234,568"


def test_fmt_pct_positive_signed():
    from app.ui.theme import fmt_pct
    result = fmt_pct(5.25)
    assert result == "+5.25%"


def test_fmt_pct_negative():
    from app.ui.theme import fmt_pct
    result = fmt_pct(-3.5)
    assert result == "-3.50%"


def test_fmt_pct_unsigned():
    from app.ui.theme import fmt_pct
    result = fmt_pct(5.0, signed=False)
    assert result == "5.00%"


def test_pnl_color_kr_up():
    from app.ui.theme import pnl_color
    assert pnl_color(1.0, kr=True) == "red"


def test_pnl_color_kr_down():
    from app.ui.theme import pnl_color
    assert pnl_color(-1.0, kr=True) == "blue"


def test_pnl_color_kr_zero():
    from app.ui.theme import pnl_color
    assert pnl_color(0.0, kr=True) == "gray"


def test_pnl_color_western_up():
    from app.ui.theme import pnl_color
    assert pnl_color(1.0, kr=False) == "green"


def test_pnl_color_western_down():
    from app.ui.theme import pnl_color
    assert pnl_color(-1.0, kr=False) == "red"


def test_pnl_md_positive():
    from app.ui.theme import pnl_md
    result = pnl_md(5.0)
    assert ":red[" in result  # KR: positive = red
    assert "5.00%" in result


def test_pnl_md_with_custom_text():
    from app.ui.theme import pnl_md
    result = pnl_md(5.0, text="상승")
    assert "상승" in result


def test_pnl_md_negative():
    from app.ui.theme import pnl_md
    result = pnl_md(-3.0)
    assert ":blue[" in result  # KR: negative = blue


def test_constants():
    from app.ui.theme import APP_NAME, APP_ICON, MODES, MODE_LABELS
    assert APP_NAME == "Autofolio"
    assert len(MODES) == 5
    assert "L0" in MODE_LABELS
    assert "L4" in MODE_LABELS
