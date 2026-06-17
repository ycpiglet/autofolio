from datetime import datetime, time, timezone, timedelta

_KST = timezone(timedelta(hours=9))


def parse_hhmm(value: str) -> time:
    hour, minute = value.split(":")
    return time(hour=int(hour), minute=int(minute))


def now_kst() -> datetime:
    """KST 기준 현재 시각 (timezone-aware). 항상 이 함수를 사용한다."""
    return datetime.now(_KST)


def is_within_trading_window(
    now=None,
    start_hhmm: str = "09:10",
    end_hhmm: str = "15:20",
) -> bool:
    """정규장 시간 판정. now가 None이면 KST 현재 시각 사용.

    timezone-naive datetime을 받으면 KST로 간주한다(테스트 하위호환).
    Linux/UTC 서버에서도 datetime.now() 대신 now_kst()를 호출해야 정확하다.
    """
    if now is None:
        now = now_kst()
    elif now.tzinfo is None:
        now = now.replace(tzinfo=_KST)
    start = parse_hhmm(start_hhmm)
    end = parse_hhmm(end_hhmm)
    return start <= now.time() <= end


ORDER_SESSION_WINDOWS = {
    "PRE_OPEN_SINGLE": ("08:30", "09:00"),
    "AFTER_CLOSE_SINGLE": ("15:40", "16:00"),
    "AFTER_HOURS_SINGLE": ("16:00", "18:00"),
}


def is_within_order_session(session: str, now=None) -> bool:
    """Return whether ``now`` is inside a supported non-regular KRX session."""
    normalized = (session or "REGULAR").upper()
    if normalized == "REGULAR":
        return is_within_trading_window(now)
    window = ORDER_SESSION_WINDOWS.get(normalized)
    if window is None:
        return False
    return is_within_trading_window(now, window[0], window[1])
