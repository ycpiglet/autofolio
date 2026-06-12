from __future__ import annotations

from scripts import kis_paper_hold_basket as basket


def test_default_basket_has_diverse_symbols() -> None:
    assert len(basket.DEFAULT_SYMBOLS) >= 8
    assert "035420" in basket.DEFAULT_SYMBOLS
    assert "114260" in basket.DEFAULT_SYMBOLS


def test_safe_error_is_redacted_and_short() -> None:
    message = basket._safe_error(RuntimeError("x" * 500))

    assert message.startswith("RuntimeError: ")
    assert len(message) < 280
