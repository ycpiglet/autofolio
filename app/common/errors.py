class TradingError(Exception):
    pass


class BrokerError(TradingError):
    pass


class SafetyCheckError(TradingError):
    pass


class ConfigurationError(TradingError):
    pass
