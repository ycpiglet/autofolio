from __future__ import annotations


def test_fundamental_uses_kis_client(monkeypatch):
    from app.brokers.kis.kis_client import KisClient
    from app.ui import backend

    class FakeKisClient(KisClient):
        def __init__(self):
            self.calls = []

        def get_fundamental(self, symbol: str) -> dict:
            self.calls.append(symbol)
            return {"symbol": symbol, "per": 12.3, "pbr": 1.4, "eps": 5000.0, "market_cap": 400000000.0}

    broker = FakeKisClient()
    monkeypatch.setattr(backend, "_ctx", lambda: (None, broker, None, None))

    result = backend.fundamental("005930")

    assert broker.calls == ["005930"]
    assert result["per"] == 12.3


def test_fundamental_returns_empty_for_non_kis_client(monkeypatch):
    from app.ui import backend

    monkeypatch.setattr(backend, "_ctx", lambda: (None, object(), None, None))

    assert backend.fundamental("005930") == {}


def test_backend_propose_passes_fundamental_to_research_agent(monkeypatch):
    from app.brokers.base import PriceQuote
    from app.ui import backend

    class FakeBroker:
        def get_current_price(self, symbol: str) -> PriceQuote:
            return PriceQuote(symbol=symbol, price=70000.0)

        def get_fundamental(self, symbol: str) -> dict:
            return {"per": 12.3, "pbr": 1.4, "eps": 5000.0, "market_cap": 400000000.0}

    class FakeAgent:
        def __init__(self):
            self.received = None

        def propose_price_condition(self, **kwargs):
            self.received = kwargs
            return kwargs

    agent = FakeAgent()
    monkeypatch.setattr(backend, "_ctx", lambda: (None, FakeBroker(), None, agent))

    result = backend.propose("005930")

    assert result["fundamental"]["per"] == 12.3
    assert agent.received["fundamental"]["eps"] == 5000.0
