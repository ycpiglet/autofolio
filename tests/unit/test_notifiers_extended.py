"""Tests for additional notification adapters: Discord, Email, Notion, Sheets."""
import pytest
from unittest.mock import patch, MagicMock


# ── DiscordNotifier ──────────────────────────────────────────────────────────

def test_discord_notifier_disabled_when_no_url():
    from app.notification.discord_notifier import DiscordNotifier
    n = DiscordNotifier(webhook_url="")
    assert n.enabled is False
    assert n.channel_name == "discord"


def test_discord_notifier_enabled_with_url():
    from app.notification.discord_notifier import DiscordNotifier
    n = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/123/abc")
    assert n.enabled is True


def test_discord_notifier_send_skips_when_disabled():
    from app.notification.discord_notifier import DiscordNotifier
    n = DiscordNotifier()
    with patch("requests.post") as mock_post:
        n.send("hello")
        mock_post.assert_not_called()


def test_discord_notifier_send_calls_requests_when_enabled():
    from app.notification.discord_notifier import DiscordNotifier
    n = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/123/abc")
    mock_resp = MagicMock()
    mock_resp.status_code = 204
    with patch("requests.post", return_value=mock_resp) as mock_post:
        n.send("hello world")
        mock_post.assert_called_once()


def test_discord_notifier_send_logs_on_bad_status():
    from app.notification.discord_notifier import DiscordNotifier
    n = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/123/abc")
    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.text = "Bad request"
    with patch("requests.post", return_value=mock_resp):
        n.send("hello")  # should not raise


def test_discord_notifier_send_handles_exception():
    from app.notification.discord_notifier import DiscordNotifier
    n = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/123/abc")
    with patch("requests.post", side_effect=Exception("network error")):
        n.send("hello")  # should not raise


def test_discord_notifier_send_fill_when_enabled():
    from app.notification.discord_notifier import DiscordNotifier
    n = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/123/abc")
    with patch("requests.post", return_value=MagicMock(status_code=204)) as mock_post:
        n.send_fill("005930", "BUY", 10, 302000.0)
        mock_post.assert_called_once()


def test_discord_notifier_send_fill_when_disabled():
    from app.notification.discord_notifier import DiscordNotifier
    n = DiscordNotifier()
    with patch("requests.post") as mock_post:
        n.send_fill("005930", "BUY", 10, None)
        mock_post.assert_not_called()


def test_discord_notifier_send_fill_exception_handled():
    from app.notification.discord_notifier import DiscordNotifier
    n = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/123/abc")
    with patch("requests.post", side_effect=Exception("network error")):
        n.send_fill("005930", "BUY", 10, 300000.0)  # should not raise


def test_make_discord_notifier_from_env():
    from app.notification.discord_notifier import make_discord_notifier_from_env
    with patch.dict("os.environ", {"DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/test"}):
        n = make_discord_notifier_from_env()
        assert n.enabled is True


# ── EmailNotifier ────────────────────────────────────────────────────────────

def test_email_notifier_disabled_when_no_credentials():
    from app.notification.email_notifier import EmailNotifier
    n = EmailNotifier(user="", app_password="")
    assert n.enabled is False
    assert n.channel_name == "email"


def test_email_notifier_enabled_with_credentials():
    from app.notification.email_notifier import EmailNotifier
    n = EmailNotifier(user="test@gmail.com", app_password="secret")
    assert n.enabled is True


def test_email_notifier_to_defaults_to_user():
    from app.notification.email_notifier import EmailNotifier
    n = EmailNotifier(user="test@gmail.com", app_password="secret")
    assert n._to == "test@gmail.com"


def test_email_notifier_to_explicit():
    from app.notification.email_notifier import EmailNotifier
    n = EmailNotifier(user="sender@gmail.com", app_password="secret", to="recv@example.com")
    assert n._to == "recv@example.com"


def test_email_notifier_send_skips_when_disabled():
    from app.notification.email_notifier import EmailNotifier
    n = EmailNotifier()
    with patch("smtplib.SMTP") as mock_smtp:
        n.send("hello")
        mock_smtp.assert_not_called()


def test_email_notifier_send_when_enabled():
    from app.notification.email_notifier import EmailNotifier
    n = EmailNotifier(user="u@gmail.com", app_password="pw")
    mock_smtp_instance = MagicMock()
    mock_smtp_instance.__enter__ = MagicMock(return_value=mock_smtp_instance)
    mock_smtp_instance.__exit__ = MagicMock(return_value=False)
    with patch("smtplib.SMTP", return_value=mock_smtp_instance):
        n.send("hello")
        mock_smtp_instance.sendmail.assert_called_once()


def test_email_notifier_send_handles_exception():
    from app.notification.email_notifier import EmailNotifier
    n = EmailNotifier(user="u@gmail.com", app_password="pw")
    with patch("smtplib.SMTP", side_effect=Exception("SMTP error")):
        n.send("hello")  # should not raise


def test_email_notifier_send_engine_summary_disabled():
    from app.notification.email_notifier import EmailNotifier
    n = EmailNotifier()  # disabled
    with patch("smtplib.SMTP") as mock_smtp:
        n.send_engine_summary(1, 2, 0)
        mock_smtp.assert_not_called()


def test_email_notifier_send_engine_summary_when_enabled():
    from app.notification.email_notifier import EmailNotifier
    n = EmailNotifier(user="u@gmail.com", app_password="pw")
    mock_smtp_instance = MagicMock()
    mock_smtp_instance.__enter__ = MagicMock(return_value=mock_smtp_instance)
    mock_smtp_instance.__exit__ = MagicMock(return_value=False)
    with patch("smtplib.SMTP", return_value=mock_smtp_instance):
        n.send_engine_summary(5, 3, 1)
        mock_smtp_instance.sendmail.assert_called_once()


def test_email_notifier_summary_exception_handled():
    from app.notification.email_notifier import EmailNotifier
    n = EmailNotifier(user="u@gmail.com", app_password="pw")
    with patch("smtplib.SMTP", side_effect=Exception("SMTP error")):
        n.send_engine_summary(1, 1, 0)  # should not raise


def test_make_email_notifier_from_env():
    from app.notification.email_notifier import make_email_notifier_from_env
    with patch.dict("os.environ", {
        "EMAIL_USER": "user@gmail.com",
        "EMAIL_APP_PASSWORD": "secret",
        "EMAIL_TO": "recv@example.com",
    }):
        n = make_email_notifier_from_env()
        assert n._user == "user@gmail.com"
        assert n._to == "recv@example.com"


# ── NotionNotifier ───────────────────────────────────────────────────────────

def test_notion_notifier_disabled_when_no_token():
    from app.notification.notion_notifier import NotionNotifier
    n = NotionNotifier()
    assert n.enabled is False
    assert n.channel_name == "notion"


def test_notion_notifier_enabled():
    from app.notification.notion_notifier import NotionNotifier
    n = NotionNotifier(token="secret_abc", database_id="dbid123")
    assert n.enabled is True


def test_notion_notifier_headers():
    from app.notification.notion_notifier import NotionNotifier
    n = NotionNotifier(token="mytoken", database_id="dbid")
    headers = n._headers()
    assert headers["Authorization"] == "Bearer mytoken"
    assert "Notion-Version" in headers


def test_notion_notifier_send_skips_when_disabled():
    from app.notification.notion_notifier import NotionNotifier
    n = NotionNotifier()
    with patch("requests.post") as mock_post:
        n.send("hello")
        mock_post.assert_not_called()


def test_notion_notifier_send_when_enabled():
    from app.notification.notion_notifier import NotionNotifier
    n = NotionNotifier(token="tok", database_id="dbid")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    with patch("requests.post", return_value=mock_resp) as mock_post:
        n.send("hello")
        mock_post.assert_called_once()


def test_notion_notifier_send_logs_on_failure():
    from app.notification.notion_notifier import NotionNotifier
    n = NotionNotifier(token="tok", database_id="dbid")
    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.text = "Bad request"
    with patch("requests.post", return_value=mock_resp):
        n.send("hello")  # should not raise


def test_notion_notifier_send_handles_exception():
    from app.notification.notion_notifier import NotionNotifier
    n = NotionNotifier(token="tok", database_id="dbid")
    with patch("requests.post", side_effect=Exception("network error")):
        n.send("hello")  # should not raise


def test_notion_notifier_log_ic_decision():
    from app.notification.notion_notifier import NotionNotifier
    n = NotionNotifier(token="tok", database_id="dbid")
    with patch.object(n, "send") as mock_send:
        n.log_ic_decision("topic123", "decision text", path="/some/path")
        mock_send.assert_called_once()
        call_text = mock_send.call_args[0][0]
        assert "topic123" in call_text
        assert "decision text" in call_text


def test_notion_notifier_log_ic_decision_no_path():
    from app.notification.notion_notifier import NotionNotifier
    n = NotionNotifier(token="tok", database_id="dbid")
    with patch.object(n, "send") as mock_send:
        n.log_ic_decision("topic", "decision")
        mock_send.assert_called_once()


def test_notion_notifier_log_retro():
    from app.notification.notion_notifier import NotionNotifier
    n = NotionNotifier(token="tok", database_id="dbid")
    with patch.object(n, "send") as mock_send:
        n.log_retro("2026-Q2", "Action: do X")
        mock_send.assert_called_once()
        call_text = mock_send.call_args[0][0]
        assert "2026-Q2" in call_text


def test_make_notion_notifier_from_env():
    from app.notification.notion_notifier import make_notion_notifier_from_env
    with patch.dict("os.environ", {"NOTION_TOKEN": "tok", "NOTION_DATABASE_ID": "dbid"}):
        n = make_notion_notifier_from_env()
        assert n.enabled is True


# ── SheetsNotifier ───────────────────────────────────────────────────────────

def test_sheets_notifier_disabled_when_no_spreadsheet():
    from app.notification.sheets_notifier import SheetsNotifier
    n = SheetsNotifier(creds_path="/some/path.json", spreadsheet_id="")
    assert n.enabled is False
    assert n.channel_name == "sheets"


def test_sheets_notifier_enabled_with_creds_path():
    from app.notification.sheets_notifier import SheetsNotifier
    n = SheetsNotifier(creds_path="/some/path.json", spreadsheet_id="sheet123")
    assert n.enabled is True


def test_sheets_notifier_enabled_with_creds_json():
    from app.notification.sheets_notifier import SheetsNotifier
    n = SheetsNotifier(creds_json='{"type": "service_account"}', spreadsheet_id="sheet123")
    assert n.enabled is True


def test_sheets_notifier_send_skips_when_disabled():
    from app.notification.sheets_notifier import SheetsNotifier
    n = SheetsNotifier()  # no creds
    n.send("hello")  # should not raise, not call anything


def test_sheets_notifier_send_skips_when_gc_none():
    from app.notification.sheets_notifier import SheetsNotifier
    n = SheetsNotifier(creds_path="/bad/path.json", spreadsheet_id="sheet123")
    # _client() will fail because gspread is not available or path is bad
    with patch.object(n, "_client", return_value=None):
        n.send("hello")  # should not raise


def test_sheets_notifier_sync_portfolio_skips_when_disabled():
    from app.notification.sheets_notifier import SheetsNotifier
    import pandas as pd
    n = SheetsNotifier()
    df = pd.DataFrame({"symbol": ["005930"], "qty": [10]})
    n.sync_portfolio(df)  # should not raise


def test_sheets_notifier_sync_portfolio_skips_when_empty_df():
    from app.notification.sheets_notifier import SheetsNotifier
    import pandas as pd
    n = SheetsNotifier(creds_path="/p.json", spreadsheet_id="sid")
    n.sync_portfolio(pd.DataFrame())  # should not raise


def test_sheets_notifier_sync_portfolio_skips_when_none():
    from app.notification.sheets_notifier import SheetsNotifier
    n = SheetsNotifier(creds_path="/p.json", spreadsheet_id="sid")
    n.sync_portfolio(None)  # should not raise


def test_make_sheets_notifier_from_env():
    from app.notification.sheets_notifier import make_sheets_notifier_from_env
    with patch.dict("os.environ", {
        "GOOGLE_SERVICE_ACCOUNT_JSON": "/path/sa.json",
        "GOOGLE_SHEETS_SPREADSHEET_ID": "sheet_abc",
    }):
        n = make_sheets_notifier_from_env()
        assert n._spreadsheet_id == "sheet_abc"


def test_sheets_notifier_client_handles_init_failure():
    from app.notification.sheets_notifier import SheetsNotifier
    n = SheetsNotifier(creds_path="/nonexistent.json", spreadsheet_id="sid")
    # Should return None without raising
    result = n._client()
    assert result is None
