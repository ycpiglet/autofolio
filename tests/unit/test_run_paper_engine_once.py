from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from app.database.sqlite_db import initialize_database


def _cfg(db_path: Path) -> SimpleNamespace:
    return SimpleNamespace(
        kis_env="paper",
        kis_base_url="https://openapivts.koreainvestment.com:29443",
        kis_account_no="12345678",
        kis_account_product_code="01",
        db_path=db_path,
        default_trading_start="09:10",
        default_trading_end="15:20",
    )


def test_run_paper_engine_dry_run_once_exits_after_one_tick(tmp_path, monkeypatch):
    import scripts.run_paper_engine as rpe

    db_path = tmp_path / "paper-engine.db"
    initialize_database(db_path)
    monkeypatch.setattr(rpe, "resolve_settings", lambda env: _cfg(db_path))

    assert rpe.main(["--dry-run", "--once"]) == 0


def test_run_paper_engine_once_outside_window_skips_without_sleep(tmp_path, monkeypatch):
    import scripts.run_paper_engine as rpe

    db_path = tmp_path / "paper-engine.db"
    initialize_database(db_path)
    monkeypatch.setattr(rpe, "resolve_settings", lambda env: _cfg(db_path))
    monkeypatch.setattr(rpe, "is_within_trading_window", lambda *args, **kwargs: False)
    monkeypatch.setattr(
        rpe.time,
        "sleep",
        lambda seconds: pytest.fail(f"one-shot run slept for {seconds}s"),
    )

    assert rpe.main(["--once"]) == 3
