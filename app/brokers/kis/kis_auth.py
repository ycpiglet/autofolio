from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

import requests

from app.common.errors import ConfigurationError, BrokerError
from app.config.settings import Settings


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
        try:
            data = json.loads(self._cache_path.read_text())
            t = KisToken(**data)
            if t.is_valid:
                self._token = t
        except Exception:
            pass

    def _save_cache(self, token: KisToken) -> None:
        try:
            fd = os.open(self._cache_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w") as f:
                json.dump({"access_token": token.access_token, "expires_at_epoch": token.expires_at_epoch}, f)
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
            raise BrokerError(f"KIS token request failed: {response.status_code} {response.text}")

        data = response.json()
        access_token = data.get("access_token")
        expires_in = int(data.get("expires_in", 3600))
        if not access_token:
            raise BrokerError(f"KIS token response missing access_token: {data}")

        self._token = KisToken(access_token=access_token, expires_at_epoch=time.time() + expires_in)
        self._save_cache(self._token)
        return access_token
