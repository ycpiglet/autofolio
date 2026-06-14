from enum import Enum


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"


class ConditionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    TRIGGERED = "TRIGGERED"
    DISABLED = "DISABLED"
    ERROR = "ERROR"
    PROCESSING = "PROCESSING"


class OrderStatus(str, Enum):
    REQUESTED = "REQUESTED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    FAILED = "FAILED"
    PENDING = "PENDING"


class SymbolRole(str, Enum):
    ETF_TEST = "ETF_TEST"
    LARGE_CAP_TEST = "LARGE_CAP_TEST"
    LONG_TERM_CANDIDATE = "LONG_TERM_CANDIDATE"
