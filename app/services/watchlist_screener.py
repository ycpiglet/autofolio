"""Watchlist and screener service — file-backed JSON persistence.

Manages named watchlists and saved screener filter sets.
Provides pure-computation screener filtering and alert dry-run evaluation.

Constraints:
- NO imports from app.engine.order_flow or any order-submission path.
- NO Streamlit imports.
- Alert evaluation is dry-run / preview only — never submits orders.
- Persistence uses plain JSON at .autofolio/watchlist_screener.json
  (non-sensitive data; no encryption required).
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

# ---------------------------------------------------------------------------
# Storage paths
# ---------------------------------------------------------------------------

_DIR = Path(os.getenv("AUTOFOLIO_HOME", ".autofolio"))
_WATCHLIST_FILE = _DIR / "watchlist_screener.json"

_EMPTY_STORE: dict = {"watchlists": [], "screeners": []}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    """Return current UTC time as ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    """Return a fresh UUID4 string."""
    return str(uuid4())


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def load_store() -> dict:
    """Load watchlist/screener store from disk.

    Returns a dict with keys 'watchlists' and 'screeners'. If the file does
    not exist or is corrupt, returns a fresh empty store.
    """
    if not _WATCHLIST_FILE.exists():
        return {"watchlists": [], "screeners": []}
    try:
        raw = _WATCHLIST_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
        # Ensure both keys are present
        data.setdefault("watchlists", [])
        data.setdefault("screeners", [])
        return data
    except Exception:
        return {"watchlists": [], "screeners": []}


def save_store(data: dict) -> None:
    """Persist the watchlist/screener store to disk.

    Creates the .autofolio directory if it does not exist.
    """
    _DIR.mkdir(parents=True, exist_ok=True)
    _WATCHLIST_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Watchlist CRUD
# ---------------------------------------------------------------------------


def list_watchlists() -> list[dict]:
    """Return all saved watchlists.

    Returns:
        List of WatchlistItem dicts (id, name, symbols, created_at, updated_at).
    """
    return load_store()["watchlists"]


def get_watchlist(wl_id: str) -> dict | None:
    """Return a single watchlist by id, or None if not found.

    Args:
        wl_id: Watchlist UUID string.
    """
    for item in load_store()["watchlists"]:
        if item["id"] == wl_id:
            return item
    return None


def create_watchlist(name: str, symbols: list[str]) -> dict:
    """Create and persist a new watchlist.

    Args:
        name:    Human-readable label for the watchlist.
        symbols: Initial list of ticker symbols.

    Returns:
        The newly created WatchlistItem dict.
    """
    store = load_store()
    now = _now_iso()
    item: dict = {
        "id": _new_id(),
        "name": name,
        "symbols": list(symbols),
        "created_at": now,
        "updated_at": now,
    }
    store["watchlists"].append(item)
    save_store(store)
    return item


def update_watchlist(
    wl_id: str,
    name: str | None = None,
    symbols: list[str] | None = None,
) -> dict | None:
    """Update an existing watchlist's name and/or symbols.

    Args:
        wl_id:   ID of the watchlist to update.
        name:    New name, or None to leave unchanged.
        symbols: New symbols list, or None to leave unchanged.

    Returns:
        Updated WatchlistItem dict, or None if not found.
    """
    store = load_store()
    for item in store["watchlists"]:
        if item["id"] == wl_id:
            if name is not None:
                item["name"] = name
            if symbols is not None:
                item["symbols"] = list(symbols)
            item["updated_at"] = _now_iso()
            save_store(store)
            return item
    return None


def delete_watchlist(wl_id: str) -> bool:
    """Delete a watchlist by id.

    Args:
        wl_id: ID of the watchlist to delete.

    Returns:
        True if deleted, False if not found.
    """
    store = load_store()
    original_len = len(store["watchlists"])
    store["watchlists"] = [w for w in store["watchlists"] if w["id"] != wl_id]
    if len(store["watchlists"]) == original_len:
        return False
    save_store(store)
    return True


# ---------------------------------------------------------------------------
# Screener filter CRUD
# ---------------------------------------------------------------------------


def list_screeners() -> list[dict]:
    """Return all saved screener filter sets.

    Returns:
        List of ScreenerFilter dicts (id, name, filters, created_at, updated_at).
    """
    return load_store()["screeners"]


def create_screener(name: str, filters: dict) -> dict:
    """Create and persist a new screener filter set.

    Args:
        name:    Human-readable label for the screener.
        filters: Dict of filter criteria. Supported keys:
                 price_min, price_max, change_rate_min, change_rate_max,
                 sector, per_max, pbr_max, dividend_yield_min,
                 disclosure_keyword, only_held (bool), only_not_held (bool).

    Returns:
        The newly created ScreenerFilter dict.
    """
    store = load_store()
    now = _now_iso()
    item: dict = {
        "id": _new_id(),
        "name": name,
        "filters": dict(filters),
        "created_at": now,
        "updated_at": now,
    }
    store["screeners"].append(item)
    save_store(store)
    return item


def update_screener(
    sc_id: str,
    name: str | None = None,
    filters: dict | None = None,
) -> dict | None:
    """Update an existing screener filter set.

    Args:
        sc_id:   ID of the screener to update.
        name:    New name, or None to leave unchanged.
        filters: New filters dict, or None to leave unchanged.

    Returns:
        Updated ScreenerFilter dict, or None if not found.
    """
    store = load_store()
    for item in store["screeners"]:
        if item["id"] == sc_id:
            if name is not None:
                item["name"] = name
            if filters is not None:
                item["filters"] = dict(filters)
            item["updated_at"] = _now_iso()
            save_store(store)
            return item
    return None


def delete_screener(sc_id: str) -> bool:
    """Delete a screener filter set by id.

    Args:
        sc_id: ID of the screener to delete.

    Returns:
        True if deleted, False if not found.
    """
    store = load_store()
    original_len = len(store["screeners"])
    store["screeners"] = [s for s in store["screeners"] if s["id"] != sc_id]
    if len(store["screeners"]) == original_len:
        return False
    save_store(store)
    return True


# ---------------------------------------------------------------------------
# Screener filter logic (pure computation)
# ---------------------------------------------------------------------------


def apply_screener_filters(candidates: list[dict], filters: dict) -> list[dict]:
    """Filter a list of symbol candidates by the given screener criteria.

    Each candidate dict must contain:
        symbol (str), name (str), price (float), change_rate (float),
        volume (float), sector (str), per (float|None), pbr (float|None),
        dividend_yield (float|None), held (bool),
        disclosure_keywords (list[str]).

    Supported filter keys (all optional; absent key means "no constraint"):
        price_min (float):             minimum price (inclusive)
        price_max (float):             maximum price (inclusive)
        change_rate_min (float):       minimum daily change rate % (inclusive)
        change_rate_max (float):       maximum daily change rate % (inclusive)
        sector (str):                  exact sector match
        per_max (float):               maximum PER (None-valued candidates pass)
        pbr_max (float):               maximum PBR (None-valued candidates pass)
        dividend_yield_min (float):    minimum dividend yield % (None-valued fail)
        disclosure_keyword (str):      substring that must appear in at least one
                                       disclosure_keywords entry (case-insensitive)
        only_held (bool):              if True, keep only held==True candidates
        only_not_held (bool):          if True, keep only held==False candidates

    Args:
        candidates: List of symbol data dicts.
        filters:    Dict of filter criteria.

    Returns:
        Filtered list of candidate dicts that match all active criteria.
    """
    result = []
    price_min = filters.get("price_min")
    price_max = filters.get("price_max")
    change_rate_min = filters.get("change_rate_min")
    change_rate_max = filters.get("change_rate_max")
    sector_filter = filters.get("sector")
    per_max = filters.get("per_max")
    pbr_max = filters.get("pbr_max")
    dividend_yield_min = filters.get("dividend_yield_min")
    disclosure_keyword = filters.get("disclosure_keyword")
    only_held = filters.get("only_held", False)
    only_not_held = filters.get("only_not_held", False)

    for c in candidates:
        price = c.get("price", 0.0)
        change_rate = c.get("change_rate", 0.0)
        sector = c.get("sector", "")
        per = c.get("per")
        pbr = c.get("pbr")
        dividend_yield = c.get("dividend_yield")
        held = c.get("held", False)
        disc_kws: list[str] = c.get("disclosure_keywords") or []

        if price_min is not None and price < price_min:
            continue
        if price_max is not None and price > price_max:
            continue
        if change_rate_min is not None and change_rate < change_rate_min:
            continue
        if change_rate_max is not None and change_rate > change_rate_max:
            continue
        if sector_filter is not None and sector != sector_filter:
            continue
        if per_max is not None and per is not None and per > per_max:
            continue
        if pbr_max is not None and pbr is not None and pbr > pbr_max:
            continue
        if dividend_yield_min is not None:
            if dividend_yield is None or dividend_yield < dividend_yield_min:
                continue
        if disclosure_keyword:
            kw_lower = disclosure_keyword.lower()
            if not any(kw_lower in dk.lower() for dk in disc_kws):
                continue
        if only_held and not held:
            continue
        if only_not_held and held:
            continue

        result.append(c)

    return result


# ---------------------------------------------------------------------------
# Alert dry-run evaluation (NEVER submits orders)
# ---------------------------------------------------------------------------


def evaluate_price_alert(
    symbol: str,
    current_price: float,
    target_price: float,
    direction: str,
) -> dict:
    """Dry-run evaluation of a price-level alert.

    Args:
        symbol:        Ticker symbol (for reporting only).
        current_price: Latest price of the symbol.
        target_price:  Alert trigger price.
        direction:     'ABOVE' — fires when current_price >= target_price.
                       'BELOW' — fires when current_price <= target_price.

    Returns:
        {"fires": bool, "reason": str}
    """
    if direction == "ABOVE":
        fires = current_price >= target_price
        reason = (
            f"{symbol} 현재가 {current_price} >= 목표가 {target_price} (ABOVE)"
            if fires
            else f"{symbol} 현재가 {current_price} < 목표가 {target_price} (ABOVE, 미발동)"
        )
    elif direction == "BELOW":
        fires = current_price <= target_price
        reason = (
            f"{symbol} 현재가 {current_price} <= 목표가 {target_price} (BELOW)"
            if fires
            else f"{symbol} 현재가 {current_price} > 목표가 {target_price} (BELOW, 미발동)"
        )
    else:
        fires = False
        reason = f"알 수 없는 direction: {direction!r} (ABOVE 또는 BELOW 필요)"
    return {"fires": fires, "reason": reason}


def evaluate_volume_spike_alert(
    symbol: str,
    current_volume: float,
    threshold_volume: float,
) -> dict:
    """Dry-run evaluation of a volume-spike alert.

    Args:
        symbol:           Ticker symbol (for reporting only).
        current_volume:   Current trading volume.
        threshold_volume: Alert fires when current_volume >= threshold_volume.

    Returns:
        {"fires": bool, "reason": str}
    """
    fires = current_volume >= threshold_volume
    if fires:
        reason = (
            f"{symbol} 거래량 {current_volume:.0f} >= 임계값 {threshold_volume:.0f} (발동)"
        )
    else:
        reason = (
            f"{symbol} 거래량 {current_volume:.0f} < 임계값 {threshold_volume:.0f} (미발동)"
        )
    return {"fires": fires, "reason": reason}


def evaluate_disclosure_keyword_alert(
    symbol: str,
    disclosure_titles: list[str],
    keyword: str,
) -> dict:
    """Dry-run evaluation of a disclosure keyword alert.

    Fires when any disclosure title contains the keyword (case-insensitive).

    Args:
        symbol:             Ticker symbol (for reporting only).
        disclosure_titles:  List of recent disclosure headline strings.
        keyword:            Substring to search for in each title.

    Returns:
        {"fires": bool, "reason": str, "matched": list[str]}
    """
    kw_lower = keyword.lower()
    matched = [t for t in disclosure_titles if kw_lower in t.lower()]
    fires = bool(matched)
    if fires:
        reason = (
            f"{symbol} 공시 키워드 '{keyword}' {len(matched)}건 매칭 (발동)"
        )
    else:
        reason = (
            f"{symbol} 공시 키워드 '{keyword}' 매칭 없음 (미발동)"
        )
    return {"fires": fires, "reason": reason, "matched": matched}


def evaluate_portfolio_weight_alert(
    symbol: str,
    current_weight_pct: float,
    threshold_pct: float,
    direction: str = "ABOVE",
) -> dict:
    """Dry-run evaluation of a portfolio weight alert.

    Args:
        symbol:              Ticker symbol (for reporting only).
        current_weight_pct:  Current portfolio weight in percent (0–100).
        threshold_pct:       Alert trigger weight threshold.
        direction:           'ABOVE' — fires when weight >= threshold.
                             'BELOW' — fires when weight <= threshold.

    Returns:
        {"fires": bool, "reason": str}
    """
    if direction == "ABOVE":
        fires = current_weight_pct >= threshold_pct
        reason = (
            f"{symbol} 비중 {current_weight_pct:.2f}% >= {threshold_pct:.2f}% (ABOVE)"
            if fires
            else f"{symbol} 비중 {current_weight_pct:.2f}% < {threshold_pct:.2f}% (ABOVE, 미발동)"
        )
    elif direction == "BELOW":
        fires = current_weight_pct <= threshold_pct
        reason = (
            f"{symbol} 비중 {current_weight_pct:.2f}% <= {threshold_pct:.2f}% (BELOW)"
            if fires
            else f"{symbol} 비중 {current_weight_pct:.2f}% > {threshold_pct:.2f}% (BELOW, 미발동)"
        )
    else:
        fires = False
        reason = f"알 수 없는 direction: {direction!r} (ABOVE 또는 BELOW 필요)"
    return {"fires": fires, "reason": reason}


def evaluate_all_alerts(rules: list[dict], market_data: dict) -> list[dict]:
    """Evaluate a list of alert rules against current market data (dry-run).

    This function NEVER submits orders. It only computes which rules would fire
    given the supplied data.

    Args:
        rules: List of alert rule dicts. Each must contain at minimum:
               - "type": one of "price", "volume", "disclosure", "weight"
               - "symbol": ticker string
               - Additional params per type:
                   price:       target_price (float), direction (str)
                   volume:      threshold_volume (float)
                   disclosure:  keyword (str)
                   weight:      threshold_pct (float), direction (str, default "ABOVE")

        market_data: Dict keyed by symbol string. Each value is a dict with:
               - price (float)
               - volume (float)
               - disclosure_titles (list[str])
               - weight_pct (float)

    Returns:
        List of {"rule": dict, "result": dict} for every rule, regardless of
        whether it fires. Callers can filter on result["fires"] to find active alerts.
    """
    results = []
    for rule in rules:
        rule_type = rule.get("type", "")
        symbol = rule.get("symbol", "")
        sym_data = market_data.get(symbol, {})

        if rule_type == "price":
            result = evaluate_price_alert(
                symbol=symbol,
                current_price=float(sym_data.get("price", 0.0)),
                target_price=float(rule.get("target_price", 0.0)),
                direction=str(rule.get("direction", "ABOVE")),
            )
        elif rule_type == "volume":
            result = evaluate_volume_spike_alert(
                symbol=symbol,
                current_volume=float(sym_data.get("volume", 0.0)),
                threshold_volume=float(rule.get("threshold_volume", 0.0)),
            )
        elif rule_type == "disclosure":
            result = evaluate_disclosure_keyword_alert(
                symbol=symbol,
                disclosure_titles=list(sym_data.get("disclosure_titles") or []),
                keyword=str(rule.get("keyword", "")),
            )
        elif rule_type == "weight":
            result = evaluate_portfolio_weight_alert(
                symbol=symbol,
                current_weight_pct=float(sym_data.get("weight_pct", 0.0)),
                threshold_pct=float(rule.get("threshold_pct", 0.0)),
                direction=str(rule.get("direction", "ABOVE")),
            )
        else:
            result = {
                "fires": False,
                "reason": f"알 수 없는 alert type: {rule_type!r}",
            }

        results.append({"rule": rule, "result": result})

    return results
