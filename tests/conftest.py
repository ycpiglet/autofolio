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
    monkeypatch.setenv("AUTOFOLIO_AUTO_EXEC_ENABLED", "1")
