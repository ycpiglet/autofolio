from __future__ import annotations


def test_watchlist_uses_batch_price_cache(monkeypatch):
    from app.services import backend

    class Repo:
        def list_whitelist_symbols(self, enabled_only=False):
            return [
                {"symbol": "005930", "name": "삼성전자"},
                {"symbol": "000660", "name": "SK하이닉스"},
            ]

    class Broker:
        def __init__(self):
            self.batch_calls = []
            self.single_calls = []

        def get_prices_batch(self, symbols):
            self.batch_calls.append(symbols)
            return {"005930": 70000.0, "000660": 120000.0}

        def get_current_price(self, symbol):
            self.single_calls.append(symbol)
            raise AssertionError("single price fallback should not be called")

    broker = Broker()
    monkeypatch.setattr(backend, "_ctx", lambda: (Repo(), broker, None, None))

    df = backend.watchlist()

    assert broker.batch_calls == [["005930", "000660"]]
    assert broker.single_calls == []
    assert df["price"].tolist() == [70000.0, 120000.0]
