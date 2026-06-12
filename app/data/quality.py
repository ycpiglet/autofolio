from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from math import isfinite
from typing import Any, Iterable, Mapping


DEFAULT_QUOTE_MAX_AGE = timedelta(minutes=15)
FUTURE_QUOTE_TOLERANCE = timedelta(minutes=1)
PRICE_FIELDS = ("open", "high", "low", "close")


@dataclass(frozen=True)
class MarketDataIssue:
    code: str
    message: str
    symbol: str | None = None
    session: date | None = None


@dataclass(frozen=True)
class MarketDataValidation:
    issues: tuple[MarketDataIssue, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.issues

    @property
    def reason(self) -> str:
        if not self.issues:
            return "ok"
        return "; ".join(issue.message for issue in self.issues)


@dataclass(frozen=True)
class CorporateAction:
    symbol: str
    action_type: str
    ex_date: date
    ratio: float | None = None
    cash_amount: float | None = None


def validate_price_quote(
    quote: Any,
    *,
    now: datetime | None = None,
    max_age: timedelta | None = DEFAULT_QUOTE_MAX_AGE,
) -> MarketDataValidation:
    """Validate a broker quote before the engine evaluates/order-submits it."""
    symbol = str(getattr(quote, "symbol", "") or "?")
    issues: list[MarketDataIssue] = []
    price = _as_float(getattr(quote, "price", None))

    if price is None or price <= 0:
        issues.append(_issue("invalid_price", f"{symbol} quote price is missing or non-positive", symbol))

    as_of = getattr(quote, "as_of", None)
    if as_of is not None and max_age is not None:
        if not isinstance(as_of, datetime):
            issues.append(_issue("invalid_timestamp", f"{symbol} quote timestamp is invalid", symbol))
        else:
            reference = _aligned_now(as_of, now)
            age = reference - as_of
            if age < -FUTURE_QUOTE_TOLERANCE:
                issues.append(_issue("future_quote", f"{symbol} quote timestamp is in the future", symbol))
            elif age > max_age:
                issues.append(_issue("stale_price", f"{symbol} quote is stale by {age}", symbol))

    return MarketDataValidation(tuple(issues))


def expected_weekday_sessions(
    start: date,
    end: date,
    *,
    holidays: Iterable[date | str] = (),
) -> list[date]:
    holiday_set = {_to_date(item) for item in holidays}
    sessions: list[date] = []
    current = start
    while current <= end:
        if current.weekday() < 5 and current not in holiday_set:
            sessions.append(current)
        current = current + timedelta(days=1)
    return sessions


def validate_ohlcv_bars(
    *,
    symbol: str,
    rows: Iterable[Mapping[str, Any]],
    start: date,
    end: date,
    holidays: Iterable[date | str] = (),
) -> MarketDataValidation:
    """Validate point-in-time OHLCV fixtures for missing and invalid sessions."""
    issues: list[MarketDataIssue] = []
    seen: set[date] = set()

    for row in rows:
        session = _row_date(row)
        if session is None:
            issues.append(_issue("missing_bar_date", f"{symbol} bar is missing a date", symbol))
            continue
        seen.add(session)
        _validate_price_fields(symbol, session, row, issues)

    for session in expected_weekday_sessions(start, end, holidays=holidays):
        if session not in seen:
            issues.append(_issue("missing_bar", f"{symbol} missing bar for {session.isoformat()}", symbol, session))

    return MarketDataValidation(tuple(issues))


def validate_corporate_actions(actions: Iterable[CorporateAction]) -> MarketDataValidation:
    issues: list[MarketDataIssue] = []
    for action in actions:
        action_type = action.action_type.lower()
        if action_type not in {"split", "cash_dividend"}:
            issues.append(_issue("unsupported_action", f"{action.symbol} action type is unsupported"))
            continue
        if action_type == "split" and (action.ratio is None or action.ratio <= 0):
            issues.append(_issue("invalid_split", f"{action.symbol} split ratio must be positive"))
        if action_type == "cash_dividend" and (action.cash_amount is None or action.cash_amount <= 0):
            issues.append(_issue("invalid_dividend", f"{action.symbol} dividend amount must be positive"))
    return MarketDataValidation(tuple(issues))


def apply_split_adjustment(
    rows: Iterable[Mapping[str, Any]],
    action: CorporateAction,
) -> list[dict[str, Any]]:
    """Return split-adjusted rows without mutating the fixture input."""
    if action.action_type.lower() != "split":
        return [dict(row) for row in rows]
    if action.ratio is None or action.ratio <= 0:
        raise ValueError("split ratio must be positive")

    adjusted_rows: list[dict[str, Any]] = []
    for row in rows:
        adjusted = dict(row)
        session = _row_date(row)
        if session is not None and session < action.ex_date:
            for field in PRICE_FIELDS:
                value = _as_float(row.get(field))
                if value is not None:
                    adjusted[field] = value / action.ratio
            volume = _as_float(row.get("volume"))
            if volume is not None:
                adjusted["volume"] = int(round(volume * action.ratio))
            adjusted["adjusted_for"] = f"split:{action.ratio:g}@{action.ex_date.isoformat()}"
        adjusted_rows.append(adjusted)
    return adjusted_rows


def _validate_price_fields(
    symbol: str,
    session: date,
    row: Mapping[str, Any],
    issues: list[MarketDataIssue],
) -> None:
    values: dict[str, float] = {}
    for field in PRICE_FIELDS:
        if field not in row and field != "close":
            continue
        value = _as_float(row.get(field))
        if value is None or value <= 0:
            issues.append(
                _issue(
                    "invalid_price",
                    f"{symbol} {field} is missing or non-positive for {session.isoformat()}",
                    symbol,
                    session,
                )
            )
            continue
        values[field] = value

    high = values.get("high")
    low = values.get("low")
    close = values.get("close")
    if high is not None and low is not None and high < low:
        issues.append(_issue("invalid_bar_range", f"{symbol} high is below low for {session.isoformat()}", symbol, session))
    if close is not None and high is not None and close > high:
        issues.append(_issue("invalid_bar_range", f"{symbol} close is above high for {session.isoformat()}", symbol, session))
    if close is not None and low is not None and close < low:
        issues.append(_issue("invalid_bar_range", f"{symbol} close is below low for {session.isoformat()}", symbol, session))


def _issue(
    code: str,
    message: str,
    symbol: str | None = None,
    session: date | None = None,
) -> MarketDataIssue:
    return MarketDataIssue(code=code, message=message, symbol=symbol, session=session)


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not isfinite(parsed):
        return None
    return parsed


def _row_date(row: Mapping[str, Any]) -> date | None:
    raw = row.get("date") or row.get("datetime") or row.get("session")
    if raw is None:
        return None
    return _to_date(raw)


def _to_date(value: date | datetime | str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if len(text) == 8 and text.isdigit():
        return date(int(text[:4]), int(text[4:6]), int(text[6:8]))
    return datetime.fromisoformat(text[:10]).date()


def _aligned_now(as_of: datetime, now: datetime | None) -> datetime:
    if now is None:
        return datetime.now(as_of.tzinfo) if as_of.tzinfo else datetime.now()
    if as_of.tzinfo is None and now.tzinfo is not None:
        return now.replace(tzinfo=None)
    if as_of.tzinfo is not None and now.tzinfo is None:
        return now.replace(tzinfo=as_of.tzinfo)
    return now
