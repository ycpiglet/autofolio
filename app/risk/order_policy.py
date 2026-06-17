from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Mapping


ADVANCED_ORDER_TYPES = {
    "CONDITIONAL_LIMIT",
    "BEST_LIMIT",
    "PRIORITY_LIMIT",
    "STOP",
    "STOP_LIMIT",
    "TRAILING_STOP",
    "IOC",
    "FOK",
    "MOO",
    "MOC",
}
DERIVATIVE_PRODUCT_TYPES = {"DERIVATIVE", "FUTURES", "OPTIONS", "FX_FUTURES"}
SHORT_SELL_TYPES = {"02", "05"}
SUPPORTED_OVERSEAS_MARKETS = {"NASD", "NYSE", "AMEX", "SEHK"}


@dataclass(frozen=True)
class ProductCapability:
    product_type: str
    trading_unit: int = 1
    tick_size: float = 1.0
    price_limit_pct: float | None = 30.0
    mock_only: bool = False
    live_order_allowed: bool = True


@dataclass(frozen=True)
class OrderPolicyResult:
    allowed: bool
    reason: str = "Allowed."


PRODUCT_CAPABILITIES: dict[str, ProductCapability] = {
    "EQUITY": ProductCapability("EQUITY"),
    "ETF": ProductCapability("ETF"),
    "ETN": ProductCapability("ETN", mock_only=False),
    "REIT": ProductCapability("REIT"),
    "ELW": ProductCapability("ELW", tick_size=5.0, mock_only=True, live_order_allowed=False),
    "BOND": ProductCapability("BOND", trading_unit=10, tick_size=0.01, mock_only=True, live_order_allowed=False),
    "OVERSEAS_EQUITY": ProductCapability("OVERSEAS_EQUITY", price_limit_pct=None),
    "FUTURES": ProductCapability("FUTURES", mock_only=True, live_order_allowed=False),
    "OPTIONS": ProductCapability("OPTIONS", mock_only=True, live_order_allowed=False),
    "FX_FUTURES": ProductCapability("FX_FUTURES", mock_only=True, live_order_allowed=False),
    "BASKET": ProductCapability("BASKET", mock_only=True, live_order_allowed=False),
}


def autonomy_rank(mode: str | None) -> int:
    value = (mode or "L0").upper()
    if value.startswith("L") and value[1:].isdigit():
        return int(value[1:])
    return 0


def product_type_for(condition: Mapping[str, Any], whitelist_symbol: Mapping[str, Any] | None) -> str:
    explicit = str(condition.get("product_type") or "").strip().upper()
    if explicit:
        return explicit
    role = str((whitelist_symbol or {}).get("role") or "").upper()
    market = str((whitelist_symbol or {}).get("market") or condition.get("market") or "KRX").upper()
    if market in SUPPORTED_OVERSEAS_MARKETS:
        return "OVERSEAS_EQUITY"
    if "ELW" in role:
        return "ELW"
    if "BOND_DIRECT" in role or role == "BOND":
        return "BOND"
    if "BOND_PROXY" in role:
        return "ETF"
    if "REIT" in role:
        return "REIT"
    if "ETN" in role or "COMMODITY" in role:
        return "ETN"
    if "ETF" in role:
        return "ETF"
    if "FUTURE" in role:
        return "FUTURES"
    if "OPTION" in role:
        return "OPTIONS"
    return "EQUITY"


def capability_for(product_type: str) -> ProductCapability:
    return PRODUCT_CAPABILITIES.get(product_type.upper(), PRODUCT_CAPABILITIES["EQUITY"])


def validate_order_policy(
    *,
    condition: Mapping[str, Any],
    current_price: float,
    whitelist_symbol: Mapping[str, Any] | None,
    system_state: Mapping[str, str] | None = None,
    kis_env: str = "mock",
) -> OrderPolicyResult:
    system_state = system_state or {}
    symbol = str(condition.get("symbol") or "")

    market_block = _market_state_block(symbol, system_state)
    if market_block:
        return market_block

    product_type = product_type_for(condition, whitelist_symbol)
    capability = capability_for(product_type)
    product_result = _validate_product_rules(condition, current_price, capability)
    if not product_result.allowed:
        return product_result

    mode = str(condition.get("symbol_mode") or system_state.get(f"symbol_mode_{symbol}") or system_state.get("global_mode", "L2"))
    rank = autonomy_rank(mode)
    order_type = str(condition.get("order_type") or "LIMIT").upper()
    sell_type = str(condition.get("sell_type") or "01")

    if sell_type in SHORT_SELL_TYPES and rank < 3:
        return OrderPolicyResult(False, f"Credit/short sell type {sell_type} requires autonomy L3 or higher.")

    if order_type in ADVANCED_ORDER_TYPES and rank < 3:
        return OrderPolicyResult(False, f"Advanced order type {order_type} requires autonomy L3 or higher.")

    if product_type in DERIVATIVE_PRODUCT_TYPES:
        if str(system_state.get("derivatives_mock_enabled", "false")).lower() != "true":
            return OrderPolicyResult(False, f"{product_type} orders are mock-only and disabled by default.")
        if rank < 3:
            return OrderPolicyResult(False, f"{product_type} mock orders require autonomy L3 or higher.")

    if product_type == "BASKET":
        if str(condition.get("venue", "MOCK")).upper() != "MOCK":
            return OrderPolicyResult(False, "Actual basket/block venue submission is disabled.")
        if str(system_state.get("basket_mock_enabled", "false")).lower() != "true":
            return OrderPolicyResult(False, "Basket mock execution is disabled by default.")

    if product_type == "OVERSEAS_EQUITY":
        market = str(condition.get("market") or (whitelist_symbol or {}).get("market") or "").upper()
        if market not in SUPPORTED_OVERSEAS_MARKETS:
            return OrderPolicyResult(False, f"Unsupported overseas market: {market or 'missing'}.")
        if str(system_state.get("overseas_paper_enabled", "false")).lower() != "true":
            return OrderPolicyResult(False, "Overseas stock orders are paper-only and disabled by default.")

    if kis_env.lower() == "prod" and _requires_prod_hardguard(condition, product_type):
        return OrderPolicyResult(False, "R3 order surface requires explicit prod hardguard review.")

    return OrderPolicyResult(True, "Allowed.")


def _market_state_block(symbol: str, system_state: Mapping[str, str]) -> OrderPolicyResult | None:
    checks = (
        (f"market_halt_{symbol}", "Market halt is active."),
        (f"vi_active_{symbol}", "Volatility interruption is active."),
        (f"disclosure_block_{symbol}", "Disclosure block is active."),
        ("market_wide_halt", "Market-wide halt is active."),
    )
    for key, reason in checks:
        if str(system_state.get(key, "false")).lower() == "true":
            return OrderPolicyResult(False, reason)
    return None


def _validate_product_rules(
    condition: Mapping[str, Any],
    current_price: float,
    capability: ProductCapability,
) -> OrderPolicyResult:
    try:
        quantity = int(condition.get("quantity", 0))
    except (TypeError, ValueError):
        return OrderPolicyResult(False, "Order quantity is invalid.")
    if quantity <= 0:
        return OrderPolicyResult(False, "Order quantity must be positive.")
    if capability.trading_unit > 1 and quantity % capability.trading_unit != 0:
        return OrderPolicyResult(
            False,
            f"{capability.product_type} quantity must be a multiple of {capability.trading_unit}.",
        )

    if not isfinite(float(current_price)) or float(current_price) <= 0:
        return OrderPolicyResult(False, "Current price is invalid.")

    price_limit_reference = condition.get("reference_price")
    if price_limit_reference is not None and capability.price_limit_pct is not None:
        try:
            reference = float(price_limit_reference)
        except (TypeError, ValueError):
            return OrderPolicyResult(False, "Reference price is invalid.")
        if reference <= 0:
            return OrderPolicyResult(False, "Reference price must be positive.")
        move_pct = abs(float(current_price) - reference) / reference * 100.0
        if move_pct > capability.price_limit_pct:
            return OrderPolicyResult(
                False,
                f"{capability.product_type} price move {move_pct:.2f}% exceeds limit {capability.price_limit_pct:.2f}%.",
            )
    return OrderPolicyResult(True, "Allowed.")


def _requires_prod_hardguard(condition: Mapping[str, Any], product_type: str) -> bool:
    order_type = str(condition.get("order_type") or "LIMIT").upper()
    sell_type = str(condition.get("sell_type") or "01")
    session = str(condition.get("order_session") or "REGULAR").upper()
    if session != "REGULAR":
        return True
    if sell_type in SHORT_SELL_TYPES:
        return True
    if order_type in ADVANCED_ORDER_TYPES:
        return True
    if product_type not in {"EQUITY", "ETF", "ETN", "REIT"}:
        return True
    return False
