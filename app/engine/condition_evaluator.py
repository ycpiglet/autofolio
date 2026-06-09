from app.common.enums import Side


def is_condition_triggered(*, side: str, current_price: float, target_price: float) -> bool:
    side_value = Side(side)

    if side_value == Side.BUY:
        return current_price <= target_price

    if side_value == Side.SELL:
        return current_price >= target_price

    raise ValueError(f"Unsupported side: {side}")
