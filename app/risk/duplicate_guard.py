from datetime import datetime


def is_condition_executable(status: str, cooldown_until: str | None, now: datetime) -> bool:
    if status != "ACTIVE":
        return False

    if cooldown_until:
        try:
            until = datetime.fromisoformat(cooldown_until)
            if now < until:
                return False
        except ValueError:
            return False

    return True
