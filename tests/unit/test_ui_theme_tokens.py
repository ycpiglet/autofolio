"""Theme token helper tests (design-system foundation)."""
from app.ui import theme


def test_env_label_mock():
    assert theme.env_label("mock") == "Mock (데모)"


def test_env_label_paper():
    assert theme.env_label("paper") == "Paper (모의투자)"


def test_env_label_prod():
    assert theme.env_label("prod") == "Live (실전)"


def test_env_label_unknown_fallback():
    assert theme.env_label("staging") == "Unknown"


def test_env_label_none_defaults_unknown():
    assert theme.env_label(None) == "Unknown"


def test_env_tokens_pnl_colors_kr():
    assert theme.SEMANTIC_TOKENS["pnl"]["up_kr"] == "red"
    assert theme.SEMANTIC_TOKENS["pnl"]["down_kr"] == "blue"


def test_env_tokens_present_for_all_modes():
    token = theme.SEMANTIC_TOKENS["env"]
    for key in ("mock", "paper", "prod", "unknown"):
        assert key in token
