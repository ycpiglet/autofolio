from datetime import datetime, time


def parse_hhmm(value: str) -> time:
    hour, minute = value.split(":")
    return time(hour=int(hour), minute=int(minute))


def is_within_trading_window(
    now: datetime,
    start_hhmm: str = "09:10",
    end_hhmm: str = "15:20",
) -> bool:
    start = parse_hhmm(start_hhmm)
    end = parse_hhmm(end_hhmm)
    return start <= now.time() <= end
