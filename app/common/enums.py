from enum import Enum


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    CONDITIONAL_LIMIT = "CONDITIONAL_LIMIT"
    BEST_LIMIT = "BEST_LIMIT"
    PRIORITY_LIMIT = "PRIORITY_LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"
    IOC = "IOC"
    FOK = "FOK"
    MOO = "MOO"
    MOC = "MOC"


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
