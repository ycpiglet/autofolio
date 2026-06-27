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


def test_vault_malformed_env_key_raises_clearly(tmp_path):
    """AUTOFOLIO_VAULT_KEY set but malformed → ValueError, not silent empty {}."""
    import importlib
    bad_key = "not-a-valid-fernet-key"
    with patch.dict(os.environ, {
        "AUTOFOLIO_HOME": str(tmp_path),
        "AUTOFOLIO_VAULT_KEY": bad_key,
    }):
        import app.ui.vault as vault
        importlib.reload(vault)
        with pytest.raises(ValueError, match="invalid Fernet key"):
            vault.load()


def test_vault_valid_env_key_does_not_write_keyfile(tmp_path):
    """AUTOFOLIO_VAULT_KEY set to a valid key → vault.key file is never created."""
    import importlib
    from cryptography.fernet import Fernet
    good_key = Fernet.generate_key().decode()
    with patch.dict(os.environ, {
        "AUTOFOLIO_HOME": str(tmp_path),
        "AUTOFOLIO_VAULT_KEY": good_key,
    }):
        import app.ui.vault as vault
        importlib.reload(vault)
        vault.save({"x": 1})
        assert vault.load() == {"x": 1}
        # The co-located key file must NOT have been created
        assert not (tmp_path / "vault.key").exists()
