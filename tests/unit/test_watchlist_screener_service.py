"""Unit tests for app/services/watchlist_screener.py.

No Streamlit imports anywhere in this file.
"""
from __future__ import annotations

import json

import pytest

import app.services.watchlist_screener as svc
from app.services.watchlist_screener import (
    apply_screener_filters,
    evaluate_all_alerts,
    evaluate_disclosure_keyword_alert,
    evaluate_portfolio_weight_alert,
    evaluate_price_alert,
    evaluate_volume_spike_alert,
)


# ---------------------------------------------------------------------------
# Candidate helper
# ---------------------------------------------------------------------------


def _candidate(**kwargs) -> dict:
    defaults = {
        "symbol": "X",
        "name": "Test",
        "price": 10000.0,
        "change_rate": 1.0,
        "volume": 1000.0,
        "sector": "IT",
        "per": 10.0,
        "pbr": 1.0,
        "dividend_yield": 2.0,
        "held": False,
        "disclosure_keywords": [],
    }
    defaults.update(kwargs)
    return defaults


# ---------------------------------------------------------------------------
# Persistence CRUD round-trip
# ---------------------------------------------------------------------------


def test_watchlist_crud_roundtrip(tmp_path, monkeypatch):
    fake_file = tmp_path / "test_store.json"
    monkeypatch.setattr(svc, "_WATCHLIST_FILE", fake_file)
    monkeypatch.setattr(svc, "_DIR", tmp_path)

    # create
    created = svc.create_watchlist("테스트", ["005930", "000660"])
    assert created["name"] == "테스트"
    assert created["symbols"] == ["005930", "000660"]
    wl_id = created["id"]

    # list
    all_wls = svc.list_watchlists()
    assert len(all_wls) == 1
    assert all_wls[0]["id"] == wl_id

    # get
    fetched = svc.get_watchlist(wl_id)
    assert fetched is not None
    assert fetched["id"] == wl_id

    # update
    updated = svc.update_watchlist(wl_id, name="변경됨", symbols=["035720"])
    assert updated["name"] == "변경됨"
    assert updated["symbols"] == ["035720"]

    # verify updated persists
    refetched = svc.get_watchlist(wl_id)
    assert refetched["name"] == "변경됨"

    # delete
    deleted = svc.delete_watchlist(wl_id)
    assert deleted is True

    # gone
    assert svc.get_watchlist(wl_id) is None
    assert svc.list_watchlists() == []


def test_screener_crud_roundtrip(tmp_path, monkeypatch):
    fake_file = tmp_path / "test_store.json"
    monkeypatch.setattr(svc, "_WATCHLIST_FILE", fake_file)
    monkeypatch.setattr(svc, "_DIR", tmp_path)

    filters = {"price_min": 50000.0, "sector": "반도체"}

    # create
    created = svc.create_screener("반도체 프리셋", filters)
    assert created["name"] == "반도체 프리셋"
    assert created["filters"] == filters
    sc_id = created["id"]

    # list
    all_sc = svc.list_screeners()
    assert len(all_sc) == 1
    assert all_sc[0]["id"] == sc_id

    # update name
    updated = svc.update_screener(sc_id, name="새 이름")
    assert updated["name"] == "새 이름"
    assert updated["filters"] == filters

    # update filters
    new_filters = {"price_max": 200000.0}
    updated2 = svc.update_screener(sc_id, filters=new_filters)
    assert updated2["filters"] == new_filters

    # delete
    deleted = svc.delete_screener(sc_id)
    assert deleted is True
    assert svc.list_screeners() == []


def test_load_store_returns_empty_when_file_missing(tmp_path, monkeypatch):
    fake_file = tmp_path / "does_not_exist.json"
    monkeypatch.setattr(svc, "_WATCHLIST_FILE", fake_file)
    monkeypatch.setattr(svc, "_DIR", tmp_path)

    store = svc.load_store()
    assert store == {"watchlists": [], "screeners": []}


def test_load_store_returns_empty_on_corrupt_file(tmp_path, monkeypatch):
    fake_file = tmp_path / "corrupt.json"
    fake_file.write_text("NOT VALID JSON {{{{", encoding="utf-8")
    monkeypatch.setattr(svc, "_WATCHLIST_FILE", fake_file)
    monkeypatch.setattr(svc, "_DIR", tmp_path)

    store = svc.load_store()
    assert store == {"watchlists": [], "screeners": []}


# ---------------------------------------------------------------------------
# Screener filter logic — pure computation
# ---------------------------------------------------------------------------


def test_filter_price_min():
    candidates = [
        _candidate(symbol="A", price=100.0),
        _candidate(symbol="B", price=50.0),
    ]
    result = apply_screener_filters(candidates, {"price_min": 75.0})
    symbols = [c["symbol"] for c in result]
    assert symbols == ["A"]


def test_filter_price_max():
    candidates = [
        _candidate(symbol="A", price=100.0),
        _candidate(symbol="B", price=50.0),
    ]
    result = apply_screener_filters(candidates, {"price_max": 75.0})
    symbols = [c["symbol"] for c in result]
    assert symbols == ["B"]


def test_filter_change_rate():
    candidates = [
        _candidate(symbol="UP", change_rate=3.0),
        _candidate(symbol="FLAT", change_rate=0.0),
        _candidate(symbol="DOWN", change_rate=-2.0),
    ]
    result = apply_screener_filters(candidates, {"change_rate_min": 1.0, "change_rate_max": 5.0})
    symbols = [c["symbol"] for c in result]
    assert symbols == ["UP"]


def test_filter_sector():
    candidates = [
        _candidate(symbol="IT1", sector="IT"),
        _candidate(symbol="FIN1", sector="금융"),
        _candidate(symbol="IT2", sector="IT"),
    ]
    result = apply_screener_filters(candidates, {"sector": "IT"})
    symbols = [c["symbol"] for c in result]
    assert symbols == ["IT1", "IT2"]


def test_filter_per_max():
    # per=None candidate passes per_max filter
    candidates = [
        _candidate(symbol="HIGH_PER", per=50.0),
        _candidate(symbol="LOW_PER", per=10.0),
        _candidate(symbol="NO_PER", per=None),
    ]
    result = apply_screener_filters(candidates, {"per_max": 20.0})
    symbols = [c["symbol"] for c in result]
    assert "LOW_PER" in symbols
    assert "NO_PER" in symbols
    assert "HIGH_PER" not in symbols


def test_filter_pbr_max():
    # pbr=None candidate passes pbr_max filter
    candidates = [
        _candidate(symbol="HIGH_PBR", pbr=5.0),
        _candidate(symbol="LOW_PBR", pbr=0.5),
        _candidate(symbol="NO_PBR", pbr=None),
    ]
    result = apply_screener_filters(candidates, {"pbr_max": 1.0})
    symbols = [c["symbol"] for c in result]
    assert "LOW_PBR" in symbols
    assert "NO_PBR" in symbols
    assert "HIGH_PBR" not in symbols


def test_filter_dividend_yield_min():
    # dividend_yield=None candidate FAILS dividend_yield_min filter
    candidates = [
        _candidate(symbol="HIGH_DIV", dividend_yield=5.0),
        _candidate(symbol="LOW_DIV", dividend_yield=1.0),
        _candidate(symbol="NO_DIV", dividend_yield=None),
    ]
    result = apply_screener_filters(candidates, {"dividend_yield_min": 3.0})
    symbols = [c["symbol"] for c in result]
    assert symbols == ["HIGH_DIV"]
    assert "NO_DIV" not in symbols
    assert "LOW_DIV" not in symbols


def test_filter_disclosure_keyword():
    # case-insensitive substring match in disclosure_keywords list
    candidates = [
        _candidate(symbol="A", disclosure_keywords=["자사주 취득", "배당"]),
        _candidate(symbol="B", disclosure_keywords=["유상증자"]),
        _candidate(symbol="C", disclosure_keywords=["자사주 소각"]),
    ]
    result = apply_screener_filters(candidates, {"disclosure_keyword": "자사주"})
    symbols = [c["symbol"] for c in result]
    assert "A" in symbols
    assert "C" in symbols
    assert "B" not in symbols


def test_filter_disclosure_keyword_case_insensitive():
    candidates = [
        _candidate(symbol="A", disclosure_keywords=["Buy-Back Program"]),
        _candidate(symbol="B", disclosure_keywords=["Other News"]),
    ]
    result = apply_screener_filters(candidates, {"disclosure_keyword": "buy-back"})
    symbols = [c["symbol"] for c in result]
    assert symbols == ["A"]


def test_filter_only_held():
    candidates = [
        _candidate(symbol="HELD", held=True),
        _candidate(symbol="NOT_HELD", held=False),
    ]
    result = apply_screener_filters(candidates, {"only_held": True})
    symbols = [c["symbol"] for c in result]
    assert symbols == ["HELD"]


def test_filter_only_not_held():
    candidates = [
        _candidate(symbol="HELD", held=True),
        _candidate(symbol="NOT_HELD", held=False),
    ]
    result = apply_screener_filters(candidates, {"only_not_held": True})
    symbols = [c["symbol"] for c in result]
    assert symbols == ["NOT_HELD"]


def test_filter_no_filters():
    candidates = [_candidate(symbol="A"), _candidate(symbol="B"), _candidate(symbol="C")]
    result = apply_screener_filters(candidates, {})
    assert len(result) == 3


def test_filter_multiple_combined():
    # price_min + sector combo
    candidates = [
        _candidate(symbol="PASS", price=80000.0, sector="IT"),
        _candidate(symbol="CHEAP_IT", price=20000.0, sector="IT"),
        _candidate(symbol="EXPENSIVE_FIN", price=90000.0, sector="금융"),
        _candidate(symbol="CHEAP_FIN", price=10000.0, sector="금융"),
    ]
    result = apply_screener_filters(candidates, {"price_min": 50000.0, "sector": "IT"})
    symbols = [c["symbol"] for c in result]
    assert symbols == ["PASS"]


# ---------------------------------------------------------------------------
# Alert dry-run evaluation
# ---------------------------------------------------------------------------


def test_price_alert_above_fires():
    result = evaluate_price_alert("A", 100.0, 90.0, "ABOVE")
    assert result["fires"] is True


def test_price_alert_above_does_not_fire():
    result = evaluate_price_alert("A", 80.0, 90.0, "ABOVE")
    assert result["fires"] is False


def test_price_alert_above_at_boundary():
    result = evaluate_price_alert("A", 90.0, 90.0, "ABOVE")
    assert result["fires"] is True


def test_price_alert_below_fires():
    result = evaluate_price_alert("A", 80.0, 90.0, "BELOW")
    assert result["fires"] is True


def test_price_alert_below_does_not_fire():
    result = evaluate_price_alert("A", 100.0, 90.0, "BELOW")
    assert result["fires"] is False


def test_price_alert_below_at_boundary():
    result = evaluate_price_alert("A", 90.0, 90.0, "BELOW")
    assert result["fires"] is True


def test_price_alert_unknown_direction():
    result = evaluate_price_alert("A", 100.0, 90.0, "SIDEWAYS")
    assert result["fires"] is False
    assert "reason" in result


def test_volume_alert_fires():
    result = evaluate_volume_spike_alert("A", 2_000_000.0, 1_000_000.0)
    assert result["fires"] is True


def test_volume_alert_does_not_fire():
    result = evaluate_volume_spike_alert("A", 500_000.0, 1_000_000.0)
    assert result["fires"] is False


def test_volume_alert_at_boundary():
    result = evaluate_volume_spike_alert("A", 1_000_000.0, 1_000_000.0)
    assert result["fires"] is True


def test_disclosure_alert_fires_case_insensitive():
    result = evaluate_disclosure_keyword_alert(
        "A", ["자사주 취득 공시", "배당 발표"], "자사주"
    )
    assert result["fires"] is True
    assert "자사주 취득 공시" in result["matched"]


def test_disclosure_alert_fires_mixed_case():
    result = evaluate_disclosure_keyword_alert(
        "A", ["Buy-Back Program Announced"], "buy-back"
    )
    assert result["fires"] is True


def test_disclosure_alert_no_match():
    result = evaluate_disclosure_keyword_alert(
        "A", ["유상증자 결정", "CB 발행"], "자사주"
    )
    assert result["fires"] is False
    assert result["matched"] == []


def test_weight_alert_above_fires():
    result = evaluate_portfolio_weight_alert("A", 15.0, 10.0, "ABOVE")
    assert result["fires"] is True


def test_weight_alert_above_does_not_fire():
    result = evaluate_portfolio_weight_alert("A", 5.0, 10.0, "ABOVE")
    assert result["fires"] is False


def test_weight_alert_below_fires():
    result = evaluate_portfolio_weight_alert("A", 3.0, 5.0, "BELOW")
    assert result["fires"] is True


def test_weight_alert_below_does_not_fire():
    result = evaluate_portfolio_weight_alert("A", 8.0, 5.0, "BELOW")
    assert result["fires"] is False


def test_weight_alert_unknown_direction():
    result = evaluate_portfolio_weight_alert("A", 8.0, 5.0, "SIDEWAYS")
    assert result["fires"] is False


def test_evaluate_all_alerts_mixed():
    rules = [
        {"type": "price", "symbol": "A", "target_price": 90.0, "direction": "ABOVE"},
        {"type": "price", "symbol": "B", "target_price": 200.0, "direction": "ABOVE"},
        {"type": "volume", "symbol": "A", "threshold_volume": 500_000.0},
        {"type": "disclosure", "symbol": "A", "keyword": "자사주"},
        {"type": "weight", "symbol": "A", "threshold_pct": 5.0, "direction": "ABOVE"},
        {"type": "weight", "symbol": "B", "threshold_pct": 20.0, "direction": "BELOW"},
    ]
    market_data = {
        "A": {
            "price": 100.0,
            "volume": 1_000_000.0,
            "disclosure_titles": ["자사주 취득 결정"],
            "weight_pct": 10.0,
        },
        "B": {
            "price": 150.0,
            "volume": 0.0,
            "disclosure_titles": [],
            "weight_pct": 15.0,
        },
    }
    results = evaluate_all_alerts(rules, market_data)

    # Total results equals total rules
    assert len(results) == len(rules)

    # Each result has "rule" and "result" keys
    for item in results:
        assert "rule" in item
        assert "result" in item
        assert "fires" in item["result"]

    # Identify which fire
    fire_map = {
        (item["rule"]["symbol"], item["rule"]["type"]): item["result"]["fires"]
        for item in results
    }
    assert fire_map[("A", "price")] is True    # 100 >= 90
    assert fire_map[("B", "price")] is False   # 150 < 200
    assert fire_map[("A", "volume")] is True   # 1M >= 500K
    assert fire_map[("A", "disclosure")] is True
    assert fire_map[("A", "weight")] is True   # 10 >= 5
    assert fire_map[("B", "weight")] is True   # 15 <= 20


def test_evaluate_all_alerts_unknown_type():
    rules = [{"type": "magic", "symbol": "X"}]
    market_data = {"X": {"price": 100.0, "volume": 0.0, "disclosure_titles": [], "weight_pct": 0.0}}
    results = evaluate_all_alerts(rules, market_data)
    assert len(results) == 1
    assert results[0]["result"]["fires"] is False


# ---------------------------------------------------------------------------
# No-order boundary (CRITICAL)
# ---------------------------------------------------------------------------


def test_no_order_path_in_service():
    """Assert watchlist_screener module never imports from order_flow or execution path.

    Checks import statements only (not docstring mentions) so the constraint
    is: no runtime dependency on the order-submission path.
    """
    import ast
    import inspect

    source = inspect.getsource(svc)
    tree = ast.parse(source)
    forbidden = {"order_flow", "OrderFlow", "place_order", "add_condition"}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = (
                [node.module or ""] if isinstance(node, ast.ImportFrom)
                else [alias.name for alias in node.names]
            )
            for name in names:
                for f in forbidden:
                    assert f not in (name or ""), (
                        f"Forbidden import of '{f}' found in watchlist_screener service"
                    )
