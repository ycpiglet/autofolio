from app.brokers.base import BrokerClient
from app.brokers.kis.kis_client import KisClient
from app.brokers.mock.mock_client import MockBrokerClient
from app.config.settings import settings


def create_broker_client() -> BrokerClient:
    if settings.kis_env == "mock":
        return MockBrokerClient()

    if settings.kis_env in {"paper", "prod"}:
        return KisClient(settings)

    raise ValueError(f"Unsupported KIS_ENV: {settings.kis_env}")
