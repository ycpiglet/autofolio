"""Unit tests for df_records serializer.

Covers:
- Korean column keys preserved verbatim
- Empty DataFrame → columns=[], rows=[]
- NaN values → None
- numpy types → JSON-safe Python types
- pandas Timestamp → ISO string
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from app.api.serializers import df_records


class TestDfRecords:
    def test_empty_df_returns_empty_response(self):
        df = pd.DataFrame()
        result = df_records(df)
        assert result.columns == []
        assert result.rows == []

    def test_empty_df_with_columns(self):
        df = pd.DataFrame(columns=["종목", "가격"])
        result = df_records(df)
        assert result.columns == ["종목", "가격"]
        assert result.rows == []

    def test_korean_column_keys_preserved(self):
        df = pd.DataFrame(
            [{"종목": "삼성전자", "평가금액": 1_000_000, "손익률": 7.1}]
        )
        result = df_records(df)
        assert "종목" in result.columns
        assert "평가금액" in result.columns
        assert "손익률" in result.columns
        assert result.rows[0]["종목"] == "삼성전자"

    def test_nan_float_becomes_none(self):
        df = pd.DataFrame([{"value": float("nan")}])
        result = df_records(df)
        assert result.rows[0]["value"] is None

    def test_inf_becomes_none(self):
        df = pd.DataFrame([{"value": float("inf")}, {"value": float("-inf")}])
        result = df_records(df)
        assert result.rows[0]["value"] is None
        assert result.rows[1]["value"] is None

    def test_numpy_int_to_python_int(self):
        df = pd.DataFrame([{"qty": np.int64(42)}])
        result = df_records(df)
        assert result.rows[0]["qty"] == 42
        assert isinstance(result.rows[0]["qty"], int)

    def test_numpy_float_to_python_float(self):
        df = pd.DataFrame([{"rate": np.float64(3.14)}])
        result = df_records(df)
        assert abs(result.rows[0]["rate"] - 3.14) < 1e-9
        assert isinstance(result.rows[0]["rate"], float)

    def test_numpy_nan_becomes_none(self):
        df = pd.DataFrame([{"x": np.float64("nan")}])
        result = df_records(df)
        assert result.rows[0]["x"] is None

    def test_pandas_timestamp_to_isostring(self):
        ts = pd.Timestamp("2026-06-14 09:00:00")
        df = pd.DataFrame([{"ts": ts}])
        result = df_records(df)
        assert isinstance(result.rows[0]["ts"], str)
        assert "2026-06-14" in result.rows[0]["ts"]

    def test_none_value_stays_none(self):
        df = pd.DataFrame([{"x": None}])
        result = df_records(df)
        assert result.rows[0]["x"] is None

    def test_string_values_preserved(self):
        df = pd.DataFrame([{"종목": "삼성전자", "방향": "BUY"}])
        result = df_records(df)
        assert result.rows[0]["종목"] == "삼성전자"
        assert result.rows[0]["방향"] == "BUY"

    def test_multiple_rows(self):
        df = pd.DataFrame([
            {"종목": "A", "가격": 1000},
            {"종목": "B", "가격": 2000},
            {"종목": "C", "가격": 3000},
        ])
        result = df_records(df)
        assert len(result.rows) == 3
        assert result.rows[2]["종목"] == "C"

    def test_none_df_returns_empty(self):
        result = df_records(None)
        assert result.columns == []
        assert result.rows == []

    def test_named_datetime_index_included_as_column(self):
        """Named DatetimeIndex must appear as a column in the output."""
        dates = pd.date_range("2026-06-12", periods=3, freq="D")
        df = pd.DataFrame({"자산": [700_000.0, 720_000.0, 750_000.0]}, index=dates)
        df.index.name = "date"
        result = df_records(df)
        assert "date" in result.columns
        assert "date" in result.rows[0]

    def test_unnamed_range_index_not_added(self):
        """Default RangeIndex (unnamed) must NOT add a junk 'index' column."""
        df = pd.DataFrame([{"종목": "삼성전자", "가격": 75_000}])
        result = df_records(df)
        assert "index" not in result.columns
