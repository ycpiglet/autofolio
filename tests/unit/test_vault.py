"""Tests for app/ui/vault.py — encrypted local vault."""
import os
import pytest
from pathlib import Path
from unittest.mock import patch


def test_vault_save_and_load(tmp_path):
    """Save data and load it back — round-trip test."""
    import importlib
    # Override the .autofolio dir to use tmp_path
    with patch.dict(os.environ, {"AUTOFOLIO_HOME": str(tmp_path)}):
        # Re-import to pick up env var (module uses module-level constants)
        import app.ui.vault as vault
        importlib.reload(vault)
        vault.save({"key": "value", "count": 42})
        loaded = vault.load()
        assert loaded["key"] == "value"
        assert loaded["count"] == 42


def test_vault_load_returns_empty_dict_when_no_file(tmp_path):
    """No vault data file → returns empty dict."""
    with patch.dict(os.environ, {"AUTOFOLIO_HOME": str(tmp_path)}):
        import app.ui.vault as vault
        import importlib
        importlib.reload(vault)
        result = vault.load()
        assert result == {}


def test_vault_load_returns_empty_on_corrupt_data(tmp_path):
    """Corrupt vault file → returns empty dict without raising."""
    with patch.dict(os.environ, {"AUTOFOLIO_HOME": str(tmp_path)}):
        import app.ui.vault as vault
        import importlib
        importlib.reload(vault)
        # Write garbage to the data file
        data_path = tmp_path / "vault.enc"
        data_path.write_bytes(b"not encrypted data at all")
        result = vault.load()
        assert result == {}


def test_vault_save_updates_existing_data(tmp_path):
    """Saving twice should overwrite with the latest data."""
    with patch.dict(os.environ, {"AUTOFOLIO_HOME": str(tmp_path)}):
        import app.ui.vault as vault
        import importlib
        importlib.reload(vault)
        vault.save({"step": 1})
        vault.save({"step": 2})
        loaded = vault.load()
        assert loaded["step"] == 2
