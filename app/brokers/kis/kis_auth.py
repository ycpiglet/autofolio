from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

import requests

from app.common.errors import ConfigurationError, BrokerError
from app.common.fileperms import restrict_to_user
from app.config.settings import Settings


def _safe_error_detail(response) -> str:
    """Extract only non-secret KIS diagnostic fields from a response.

    SECURITY: never returns ``response.text`` or the full parsed body — those
    can echo bearer tokens / appkey / request context. Mirrors the safe pattern
    in app/brokers/kis/kis_client.py (msg_cd + msg1 only).
    """
    try:
        data = response.json()
    except Exception:  # noqa: BLE001 — diagnostics only
        return ""
    if not isinstance(data, dict):
        return ""
    msg_cd = data.get("msg_cd")
    msg1 = data.get("msg1")
    parts = [str(p) for p in (msg_cd, msg1) if p]
    return " ".join(parts)


@dataclass
class KisToken:
    access_token: str
    expires_at_epoch: float

    @property
    def is_valid(self) -> bool:
        return bool(self.access_token) and time.time() < self.expires_at_epoch - 60


class KisAuth:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._token: KisToken | None = None
        cache_dir = Path(__file__).resolve().parents[3] / ".autofolio"
        cache_dir.mkdir(mode=0o700, exist_ok=True)
        self._cache_path = cache_dir / f"kis_token_{settings.kis_env}.json"
        self._load_cache()

    def _load_cache(self) -> None:
        # SECURITY: the cache is Fernet-encrypted with the vault key (P0.3). A
        # missing / old-cleartext / undecryptable file degrades gracefully to a
        # cache miss → the token is simply re-issued.
        try:
            from app.ui.vault import decrypt_bytes

            raw = decrypt_bytes(self._cache_path.read_bytes())
            data = json.loads(raw.decode("utf-8"))
            t = KisToken(**data)
            if t.is_valid:
                self._token = t
        except Exception:
            pass

    def _save_cache(self, token: KisToken) -> None:
        # SECURITY: encrypt the live bearer token before writing it to disk so
        # the cache file is no longer cleartext. Round-trips with _load_cache via
        # the shared vault key (AUTOFOLIO_VAULT_KEY → co-located fallback).
        try:
            from app.ui.vault import encrypt_bytes

            payload = json.dumps(
                {
                    "access_token": token.access_token,
                    "expires_at_epoch": token.expires_at_epoch,
                }
            ).encode("utf-8")
            self._cache_path.write_bytes(encrypt_bytes(payload))
            restrict_to_user(self._cache_path)
        except Exception:
            pass

    def get_access_token(self) -> str:
        if self._token and self._token.is_valid:
            return self._token.access_token

        if not self.settings.kis_base_url or not self.settings.kis_token_path:
            raise ConfigurationError(
                "KIS_BASE_URL and KIS_TOKEN_PATH must be set before using real KIS API."
            )

        if not self.settings.kis_app_key or not self.settings.kis_app_secret:
            raise ConfigurationError("KIS_APP_KEY and KIS_APP_SECRET are required.")

        url = self.settings.kis_base_url.rstrip("/") + "/" + self.settings.kis_token_path.lstrip("/")
        payload = {
            "grant_type": "client_credentials",
            "appkey": self.settings.kis_app_key,
            "appsecret": self.settings.kis_app_secret,
        }

        response = requests.post(url, json=payload, timeout=10)
        if response.status_code >= 400:
            # SECURITY: do NOT include response.text (can echo tokens / request
            # context) — only the status code + KIS msg_cd/msg1.
            detail = _safe_error_detail(response)
            raise BrokerError(
                f"KIS token request failed: HTTP {response.status_code} {detail}".rstrip()
            )

        data = response.json()
        access_token = data.get("access_token")
        expires_in = int(data.get("expires_in", 3600))
        if not access_token:
            # SECURITY: do NOT dump the full parsed body — only safe diagnostics.
            raise BrokerError(
                "KIS token response missing access_token "
                f"(msg_cd={data.get('msg_cd')} msg1={data.get('msg1')})"
            )

        self._token = KisToken(access_token=access_token, expires_at_epoch=time.time() + expires_in)
        self._save_cache(self._token)
        return access_token
