import os as _os

# Force the SQLite backend for the ENTIRE test suite, independent of a
# developer's local .env DATABASE_URL. get_connection() routes to Postgres
# whenever DATABASE_URL is a postgres URL (and then ignores db_path), so a
# populated .env would point every test at the staging Postgres — breaking the
# SQLite-only DDL in fixtures and mutating staging data. We set DATABASE_URL=""
# here, BEFORE any app import; settings.load_dotenv() uses override=False and so
# will NOT overwrite this empty value. Tests needing Postgres must set it
# explicitly against a throwaway database.
_os.environ["DATABASE_URL"] = ""

from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def _auto_exec_enabled(monkeypatch):
    """TASK-087 A2: set deployment flag ON for all tests by default.

    Tests that specifically validate the flag-OFF behaviour must call
    ``monkeypatch.delenv("AUTOFOLIO_AUTO_EXEC_ENABLED", raising=False)``
    in their own body to override this fixture.
    """
    # Override with monkeypatch.delenv("AUTOFOLIO_AUTO_EXEC_ENABLED", raising=False) within a test to exercise flag-OFF paths.
    monkeypatch.setenv("AUTOFOLIO_AUTO_EXEC_ENABLED", "1")
