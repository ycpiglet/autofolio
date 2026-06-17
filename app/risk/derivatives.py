from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DerivativeContract:
    symbol: str
    product_type: str
    expiry: date
    multiplier: float
    margin_rate: float
    strike: float | None = None


def validate_derivative_contract(contract: DerivativeContract, *, today: date) -> tuple[bool, str]:
    product_type = contract.product_type.upper()
    if product_type not in {"FUTURES", "OPTIONS", "FX_FUTURES"}:
        return False, f"Unsupported derivative product type: {contract.product_type}"
    if contract.expiry <= today:
        return False, "Derivative contract is expired."
    if contract.multiplier <= 0:
        return False, "Derivative multiplier must be positive."
    if contract.margin_rate <= 0:
        return False, "Derivative margin rate must be positive."
    if product_type == "OPTIONS" and (contract.strike is None or contract.strike <= 0):
        return False, "Options require a positive strike."
    return True, "ok"


def estimate_margin(price: float, quantity: int, contract: DerivativeContract) -> float:
    if price <= 0:
        raise ValueError("price must be positive")
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    return round(price * quantity * contract.multiplier * contract.margin_rate, 4)
