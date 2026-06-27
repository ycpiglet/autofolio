from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv()


# KIS 환경별 기본 엔드포인트. 환경변수(KIS_<ENV>_BASE_URL / KIS_BASE_URL)가 있으면 그쪽이 우선.
DEFAULT_KIS_BASE_URLS = {
    "mock": "",  # mock 은 MockBrokerClient 라 base_url 불필요
    "paper": "https://openapivts.koreainvestment.com:29443",
    "prod": "https://openapi.koreainvestment.com:9443",
}
DEFAULT_KIS_WS_URLS = {
    "mock": "",
    "paper": "ws://ops.koreainvestment.com:31000",
    "prod": "ws://ops.koreainvestment.com:21000",
}
DEFAULT_KIS_TOKEN_PATH = "/oauth2/tokenP"


@dataclass(frozen=True)
class Settings:
    kis_env: str = os.getenv("KIS_ENV", "mock").lower()

    kis_app_key: str = os.getenv("KIS_APP_KEY", "")
    kis_app_secret: str = os.getenv("KIS_APP_SECRET", "")
    kis_account_no: str = os.getenv("KIS_ACCOUNT_NO", "")
    kis_account_product_code: str = os.getenv("KIS_ACCOUNT_PRODUCT_CODE", "")

    kis_base_url: str = os.getenv("KIS_BASE_URL", "")
    kis_ws_url: str = os.getenv("KIS_WS_URL", "")
    kis_token_path: str = os.getenv("KIS_TOKEN_PATH", "")
    kis_hts_id: str = os.getenv("KIS_HTS_ID", "")

    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")

    db_path: Path = Path(os.getenv("DB_PATH", "trading_bot.db"))

    # Optional Postgres backend selector. When this is a postgres://|postgresql://
    # URL the database seam (app.database.sqlite_db.get_connection) returns the
    # psycopg adapter; when unset/empty (the default) the SQLite path is used,
    # byte-identical to the pre-existing behaviour. No secret value lives here —
    # the URL is supplied via the DATABASE_URL environment variable at deploy time.
    database_url: str = os.getenv("DATABASE_URL", "")

    default_poll_interval_sec: int = 3
    default_order_timeout_sec: int = 60
    default_cooldown_min: int = 30

    default_trading_start: str = "09:10"
    default_trading_end: str = "15:20"

    full_regular_session_start: str = "09:00"
    full_regular_session_end: str = "15:30"

    default_max_order_amount: float = 100_000.0
    default_max_daily_amount: float = 300_000.0


def _kis_cred(env: str, suffix: str) -> str:
    """환경별(KIS_PAPER_APP_KEY 등) 우선, 없으면 generic(KIS_APP_KEY) 폴백."""
    return os.getenv(f"KIS_{env.upper()}_APP_{suffix}") or os.getenv(f"KIS_APP_{suffix}", "")


def _kis_account(env: str, suffix: str) -> str:
    """환경별(KIS_PAPER_ACCOUNT_NO 등) 우선, 없으면 generic 폴백."""
    return os.getenv(f"KIS_{env.upper()}_ACCOUNT_{suffix}") or os.getenv(f"KIS_ACCOUNT_{suffix}", "")


def _kis_hts_id(env: str) -> str:
    """환경별 HTS ID 우선, 없으면 generic 폴백."""
    return os.getenv(f"KIS_{env.upper()}_HTS_ID") or os.getenv("KIS_HTS_ID", "")


def resolve_settings(env: str | None = None) -> Settings:
    """KIS_ENV(또는 인자)에 맞춰 환경별 자격증명·엔드포인트를 해석한 Settings 를 만든다.

    KIS 키는 환경별로 분리(KIS_PAPER_*/KIS_PROD_*)되어 있으므로 generic 필드만 읽는
    기본 Settings() 는 paper/prod 에서 키가 비어 인증이 실패한다. 이 함수가 단일 해석
    지점이다(앱 factory·토큰 스모크가 공유). 우선순위는 KIS_<ENV>_* → generic → 기본값.
    """
    env = (env or os.getenv("KIS_ENV", "mock")).lower()
    base_url = (
        os.getenv(f"KIS_{env.upper()}_BASE_URL")
        or os.getenv("KIS_BASE_URL")
        or DEFAULT_KIS_BASE_URLS.get(env, "")
    )
    ws_url = (
        os.getenv(f"KIS_{env.upper()}_WS_URL")
        or os.getenv("KIS_WS_URL")
        or DEFAULT_KIS_WS_URLS.get(env, "")
    )
    token_path = os.getenv("KIS_TOKEN_PATH") or DEFAULT_KIS_TOKEN_PATH
    return Settings(
        kis_env=env,
        kis_app_key=_kis_cred(env, "KEY"),
        kis_app_secret=_kis_cred(env, "SECRET"),
        kis_account_no=_kis_account(env, "NO"),
        kis_account_product_code=_kis_account(env, "PRODUCT_CODE"),
        kis_base_url=base_url,
        kis_ws_url=ws_url,
        kis_token_path=token_path,
        kis_hts_id=_kis_hts_id(env),
    )


settings = resolve_settings()
