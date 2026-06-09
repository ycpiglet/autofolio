from __future__ import annotations

import time
from dataclasses import dataclass

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
        return access_token
