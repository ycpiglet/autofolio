from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database.sqlite_db import initialize_database
from app.database.repositories import Repository, WhitelistSymbol
from app.config.settings import settings


if __name__ == "__main__":
    initialize_database(settings.db_path)
    repo = Repository(settings.db_path)

    repo.add_whitelist_symbol(
        WhitelistSymbol(symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST")
    )
    repo.add_whitelist_symbol(
        WhitelistSymbol(symbol="069500", name="KODEX 200", market="KRX", role="ETF_TEST")
    )
    repo.add_whitelist_symbol(
        WhitelistSymbol(symbol="360750", name="TIGER 미국S&P500", market="KRX", role="LONG_TERM_CANDIDATE")
    )

    print("Seeded sample whitelist symbols.")
