"""Tests for notification modules — base, notifier, telegram_notifier, kis_models."""
import pytest
from unittest.mock import patch, MagicMock


# ── BaseNotifier + NotificationBus (app/notification/base.py) ──────────────

from app.notification.base import BaseNotifier


class _ConcreteNotifier(BaseNotifier):
    """Minimal concrete implementation of BaseNotifier for testing."""
    def __init__(self, name: str, enabled: bool):
        self._name = name
        self._enabled = enabled
        self.sent: list[str] = []

    @property
    def channel_name(self) -> str:
        return self._name

    @property
    def enabled(self) -> bool:
        return self._enabled

    def send(self, text: str) -> None:
        self.sent.append(text)


def test_base_notifier_send_fill():
    from app.notification.base import BaseNotifier
    n = _ConcreteNotifier("test", True)
    # Monkey-patch send onto a BaseNotifier-like object
    # Use the mixin methods directly
    n_base = MagicMock()
    n_base.send = MagicMock()
    BaseNotifier.send_fill(n_base, "005930", "BUY", 10, 302000.0)
    n_base.send.assert_called_once()
    call_text = n_base.send.call_args[0][0]
    assert "005930" in call_text
    assert "BUY" in call_text
    assert "10" in call_text


def test_base_notifier_send_fill_no_price():
    from app.notification.base import BaseNotifier
    n_base = MagicMock()
    n_base.send = MagicMock()
    BaseNotifier.send_fill(n_base, "005930", "SELL", 5, None)
    n_base.send.assert_called_once()


def test_base_notifier_send_error():
    from app.notification.base import BaseNotifier
    n_base = MagicMock()
    n_base.send = MagicMock()
    BaseNotifier.send_error(n_base, "order_flow", "timeout")
    n_base.send.assert_called_once()
    call_text = n_base.send.call_args[0][0]
    assert "order_flow" in call_text
    assert "timeout" in call_text


def test_base_notifier_send_engine_summary():
    from app.notification.base import BaseNotifier
    n_base = MagicMock()
    n_base.send = MagicMock()
    BaseNotifier.send_engine_summary(n_base, 5, 3, 1)
    n_base.send.assert_called_once()


def test_notification_bus_send_to_enabled_only():
    from app.notification.base import NotificationBus
    enabled = _ConcreteNotifier("enabled", True)
    disabled = _ConcreteNotifier("disabled", False)
    bus = NotificationBus([enabled, disabled])
    bus.send("hello")
    assert enabled.sent == ["hello"]
    assert disabled.sent == []


def test_notification_bus_send_fill():
    from app.notification.base import NotificationBus
    n = _ConcreteNotifier("test", True)
    bus = NotificationBus([n])
    bus.send_fill("005930", "BUY", 10, 302000.0)
    assert len(n.sent) == 1
    assert "005930" in n.sent[0]


def test_notification_bus_send_error():
    from app.notification.base import NotificationBus
    n = _ConcreteNotifier("test", True)
    bus = NotificationBus([n])
    bus.send_error("ctx", "detail")
    assert len(n.sent) == 1


def test_notification_bus_send_engine_summary():
    from app.notification.base import NotificationBus
    n = _ConcreteNotifier("test", True)
    bus = NotificationBus([n])
    bus.send_engine_summary(1, 2, 0)
    assert len(n.sent) == 1


def test_notification_bus_enabled_if_any_enabled():
    from app.notification.base import NotificationBus
    enabled = _ConcreteNotifier("a", True)
    disabled = _ConcreteNotifier("b", False)
    bus = NotificationBus([enabled, disabled])
    assert bus.enabled is True


def test_notification_bus_not_enabled_when_all_disabled():
    from app.notification.base import NotificationBus
    bus = NotificationBus([_ConcreteNotifier("x", False)])
    assert bus.enabled is False


def test_notification_bus_empty():
    from app.notification.base import NotificationBus
    bus = NotificationBus()
    assert bus.enabled is False
    bus.send("test")  # should not raise


def test_notification_bus_register():
    from app.notification.base import NotificationBus
    bus = NotificationBus()
    n = _ConcreteNotifier("test", True)
    bus.register(n)
    assert bus.enabled is True


def test_notification_bus_handles_send_exception():
    """Bus should catch exceptions from adapters without propagating."""
    from app.notification.base import NotificationBus, BaseNotifier
    bad = MagicMock(spec=BaseNotifier)
    bad.enabled = True
    bad.channel_name = "bad"
    bad.send.side_effect = RuntimeError("network down")
    bus = NotificationBus([bad])
    bus.send("test")  # should not raise


def test_notification_bus_send_fill_exception_handled():
    """send_fill exception in adapter should be caught by bus."""
    from app.notification.base import NotificationBus, BaseNotifier
    bad = MagicMock(spec=BaseNotifier)
    bad.enabled = True
    bad.channel_name = "bad"
    bad.send_fill.side_effect = RuntimeError("network down")
    bus = NotificationBus([bad])
    bus.send_fill("005930", "BUY", 10, 302000.0)  # should not raise


def test_notification_bus_send_error_exception_handled():
    """send_error exception in adapter should be caught by bus."""
    from app.notification.base import NotificationBus, BaseNotifier
    bad = MagicMock(spec=BaseNotifier)
    bad.enabled = True
    bad.channel_name = "bad"
    bad.send_error.side_effect = RuntimeError("network down")
    bus = NotificationBus([bad])
    bus.send_error("context", "detail")  # should not raise


def test_notification_bus_send_engine_summary_exception_handled():
    """send_engine_summary exception in adapter should be caught by bus."""
    from app.notification.base import NotificationBus, BaseNotifier
    bad = MagicMock(spec=BaseNotifier)
    bad.enabled = True
    bad.channel_name = "bad"
    bad.send_engine_summary.side_effect = RuntimeError("network down")
    bus = NotificationBus([bad])
    bus.send_engine_summary(1, 2, 0)  # should not raise


# ── Notifier (app/notification/notifier.py) ───────────────────────────────

def test_notifier_disabled_when_no_token():
    from app.notification.notifier import Notifier
    n = Notifier(bot_token="", chat_id="")
    assert n.enabled is False
    assert n.channel_name == "telegram"


def test_notifier_enabled_when_both_set():
    from app.notification.notifier import Notifier
    n = Notifier(bot_token="token123", chat_id="chat456")
    assert n.enabled is True


def test_notifier_send_no_token_does_not_call_requests():
    from app.notification.notifier import Notifier
    n = Notifier()
    with patch("requests.post") as mock_post:
        n.send("hello")
        mock_post.assert_not_called()


def test_notifier_send_with_token_calls_requests():
    from app.notification.notifier import Notifier
    n = Notifier(bot_token="tok", chat_id="cid")
    with patch("requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        n.send("hello")
        mock_post.assert_called_once()


def test_notifier_send_handles_request_exception():
    from app.notification.notifier import Notifier
    n = Notifier(bot_token="tok", chat_id="cid")
    with patch("requests.post", side_effect=Exception("connection refused")):
        n.send("hello")  # should not raise


def test_notifier_send_engine_summary():
    from app.notification.notifier import Notifier
    n = Notifier()  # disabled
    n.send_engine_summary(3, 2, 0)  # should not raise


def test_make_notifier_from_env():
    from app.notification.notifier import make_notifier_from_env
    with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "mytoken", "TELEGRAM_CHAT_ID": "mychat"}):
        n = make_notifier_from_env()
        assert n._bot_token == "mytoken"
        assert n._chat_id == "mychat"


# ── TelegramNotifier (app/notification/telegram_notifier.py) ──────────────

def test_telegram_notifier_disabled_when_no_token():
    from app.notification.telegram_notifier import TelegramNotifier
    n = TelegramNotifier(bot_token="", chat_id="")
    assert n.enabled is False


def test_telegram_notifier_enabled():
    from app.notification.telegram_notifier import TelegramNotifier
    n = TelegramNotifier(bot_token="tok", chat_id="cid")
    assert n.enabled is True


def test_telegram_notifier_send_message_disabled_returns_false():
    from app.notification.telegram_notifier import TelegramNotifier
    n = TelegramNotifier(bot_token="", chat_id="")
    result = n.send_message("hello")
    assert result is False


def test_telegram_notifier_send_message_success():
    from app.notification.telegram_notifier import TelegramNotifier
    n = TelegramNotifier(bot_token="tok", chat_id="cid")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    with patch("requests.post", return_value=mock_resp):
        result = n.send_message("hello")
        assert result is True


def test_telegram_notifier_send_message_failure():
    from app.notification.telegram_notifier import TelegramNotifier
    n = TelegramNotifier(bot_token="tok", chat_id="cid")
    mock_resp = MagicMock()
    mock_resp.status_code = 400
    with patch("requests.post", return_value=mock_resp):
        result = n.send_message("hello")
        assert result is False


# ── KisModels (app/brokers/kis/kis_models.py) ─────────────────────────────

def test_kis_environment_dataclass():
    from app.brokers.kis.kis_models import KisEnvironment
    env = KisEnvironment(name="paper", base_url="https://openapivts.koreainvestment.com:29443")
    assert env.name == "paper"
    assert env.base_url == "https://openapivts.koreainvestment.com:29443"


def test_kis_environment_frozen():
    from app.brokers.kis.kis_models import KisEnvironment
    env = KisEnvironment(name="prod", base_url="https://openapi.koreainvestment.com:9443")
    with pytest.raises((AttributeError, TypeError)):
        env.name = "paper"  # type: ignore
