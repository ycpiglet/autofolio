from __future__ import annotations


def test_order_book_snapshot_and_df_use_kis_client(monkeypatch):
    from app.brokers.kis.kis_client import KisClient
    from app.services import backend

    class FakeKisClient(KisClient):
        def __init__(self):
            self.calls = []

        def get_order_book(self, symbol: str, market: str = "J") -> dict:
            self.calls.append((symbol, market))
            return {
                "symbol": symbol,
                "market": market,
                "current_price": 70000.0,
                "levels": [
                    {
                        "level": 1,
                        "ask_price": 70100.0,
                        "ask_quantity": 100,
                        "bid_price": 70000.0,
                        "bid_quantity": 200,
                    }
                ],
            }

    broker = FakeKisClient()
    monkeypatch.setattr(backend, "_ctx", lambda: (None, broker, None, None))

    snapshot = backend.order_book_snapshot("005930", market="UN")
    df = backend.order_book_levels_df(snapshot)

    assert broker.calls == [("005930", "UN")]
    assert snapshot["current_price"] == 70000.0
    assert df.columns.tolist() == ["level", "ask_price", "ask_quantity", "bid_price", "bid_quantity"]
    assert df.iloc[0]["ask_price"] == 70100.0


def test_order_book_df_returns_empty_for_non_kis_client(monkeypatch):
    from app.services import backend

    class FakeBroker:
        pass

    monkeypatch.setattr(backend, "_ctx", lambda: (None, FakeBroker(), None, None))

    df = backend.order_book_df("005930")

    assert df.empty
    assert df.columns.tolist() == ["level", "ask_price", "ask_quantity", "bid_price", "bid_quantity"]
