"""Tests for app/data/data_loader.py — new file added on feat/kis-live-trading."""
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock


def test_load_price_history_non_kis_broker_returns_empty_df():
    """Non-KisClient broker → returns empty DataFrame with correct columns."""
    from app.data.data_loader import load_price_history
    from app.brokers.mock.mock_client import MockBrokerClient

    mock_broker = MockBrokerClient()
    with patch("app.brokers.factory.create_broker_client", return_value=mock_broker):
        df = load_price_history("005930")
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["date", "open", "high", "low", "close", "volume"]
    assert len(df) == 0


def test_load_price_history_kis_client_returns_dataframe():
    """KisClient path: rows → DataFrame with datetime date column."""
    from app.data.data_loader import load_price_history
    from app.brokers.kis.kis_client import KisClient

    fake_rows = [
        {
            "date": "20260609",
            "open": 300000.0,
            "high": 305000.0,
            "low": 299000.0,
            "close": 302000.0,
            "volume": 12000000,
        },
    ]
    mock_broker = MagicMock(spec=KisClient)
    mock_broker.get_price_history.return_value = fake_rows

    with patch("app.brokers.factory.create_broker_client", return_value=mock_broker):
        df = load_price_history("005930", period="D", count=1)

    assert len(df) == 1
    assert df["close"].iloc[0] == 302000.0
    assert str(df["date"].dtype) == "datetime64[ns]"


def test_load_price_history_empty_rows_returns_empty_df():
    """KisClient returns empty list → empty DataFrame."""
    from app.data.data_loader import load_price_history
    from app.brokers.kis.kis_client import KisClient

    mock_broker = MagicMock(spec=KisClient)
    mock_broker.get_price_history.return_value = []

    with patch("app.brokers.factory.create_broker_client", return_value=mock_broker):
        df = load_price_history("005930")

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    assert list(df.columns) == ["date", "open", "high", "low", "close", "volume"]


def test_load_price_history_multiple_rows_sorted_ascending():
    """Multiple rows should be sorted by date ascending."""
    from app.data.data_loader import load_price_history
    from app.brokers.kis.kis_client import KisClient

    fake_rows = [
        {"date": "20260610", "open": 305000.0, "high": 308000.0, "low": 303000.0, "close": 307000.0, "volume": 10000000},
        {"date": "20260608", "open": 295000.0, "high": 300000.0, "low": 294000.0, "close": 298000.0, "volume": 8000000},
        {"date": "20260609", "open": 300000.0, "high": 305000.0, "low": 299000.0, "close": 302000.0, "volume": 12000000},
    ]
    mock_broker = MagicMock(spec=KisClient)
    mock_broker.get_price_history.return_value = fake_rows

    with patch("app.brokers.factory.create_broker_client", return_value=mock_broker):
        df = load_price_history("005930", period="D", count=3)

    assert len(df) == 3
    # Should be sorted ascending by date
    dates = list(df["date"])
    assert dates == sorted(dates)
