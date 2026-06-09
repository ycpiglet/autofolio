from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    kis_env: str = os.getenv("KIS_ENV", "mock").lower()

    kis_app_key: str = os.getenv("KIS_APP_KEY", "")
    kis_app_secret: str = os.getenv("KIS_APP_SECRET", "")
    kis_account_no: str = os.getenv("KIS_ACCOUNT_NO", "")
    kis_account_product_code: str = os.getenv("KIS_ACCOUNT_PRODUCT_CODE", "")

    kis_base_url: str = os.getenv("KIS_BASE_URL", "")
    kis_token_path: str = os.getenv("KIS_TOKEN_PATH", "")

    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")

    db_path: Path = Path(os.getenv("DB_PATH", "trading_bot.db"))

    default_poll_interval_sec: int = 3
    default_order_timeout_sec: int = 60
    default_cooldown_min: int = 30

    default_trading_start: str = "09:10"
    default_trading_end: str = "15:20"

    full_regular_session_start: str = "09:00"
    full_regular_session_end: str = "15:30"

    default_max_order_amount: float = 100_000.0
    default_max_daily_amount: float = 300_000.0


settings = Settings()
