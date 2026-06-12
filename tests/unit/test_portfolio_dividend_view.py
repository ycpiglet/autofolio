from __future__ import annotations


def test_portfolio_view_renders_dividend_metrics(tmp_path):
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "portfolio_dividend_app.py"
    script.write_text(
        """
import pandas as pd
from unittest.mock import patch

from app.ui.views import portfolio

df = pd.DataFrame([
    {
        "종목": "삼성전자",
        "티커": "005930",
        "자산군": "주식",
        "지역": "KR",
        "수량": 10,
        "평단": 70000,
        "현재가": 80000,
        "평가금액": 800000,
        "평가손익": 100000,
        "손익률": 14.3,
        "예상연배당": 4000,
        "배당수익률": 0.5,
        "비중": 100.0,
    }
])

with patch.object(portfolio, "_holdings_df", lambda: df):
    portfolio.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=15)

    assert not at.exception
    assert any(metric.label == "총 매입금액" for metric in at.metric)
    assert any(metric.label == "총수익률" for metric in at.metric)
    assert any(metric.label == "예상 연배당" for metric in at.metric)
    assert any(metric.label == "배당수익률" for metric in at.metric)
    assert any("보유 현황" in str(node.value) for node in [*at.subheader, *at.markdown])
    assert len(at.dataframe) >= 1
