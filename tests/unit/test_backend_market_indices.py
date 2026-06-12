from __future__ import annotations


def test_market_indices_df_uses_kis_client(monkeypatch):
    from app.brokers.kis.kis_client import KisClient
    from app.ui import backend

    class FakeKisClient(KisClient):
        def __init__(self):
            self.calls = []

        def get_index_price(self, index_code: str) -> dict:
            self.calls.append(index_code)
            return {
                "index_code": index_code,
                "price": 100.0 + len(self.calls),
                "change": 1.0,
                "change_rate": 0.5,
            }

    broker = FakeKisClient()
    monkeypatch.setattr(backend, "_ctx", lambda: (None, broker, None, None))

    df = backend.market_indices_df()

    assert broker.calls == ["0001", "1001", "2001"]
    assert df["name"].tolist() == ["KOSPI", "KOSDAQ", "KOSPI200"]
    assert df["price"].tolist() == [101.0, 102.0, 103.0]
