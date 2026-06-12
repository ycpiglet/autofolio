from __future__ import annotations


def test_sector_performance_df_uses_kis_client(monkeypatch):
    from app.brokers.kis.constants import KIS_SECTOR_CODES
    from app.brokers.kis.kis_client import KisClient
    from app.ui import backend

    class FakeKisClient(KisClient):
        def __init__(self):
            self.calls = []

        def get_sector_price(self, sector_code: str) -> dict:
            self.calls.append(sector_code)
            return {
                "sector_code": f"C{len(self.calls)}",
                "name": f"업종{len(self.calls)}",
                "price": 100.0 + len(self.calls),
                "change": 1.0,
                "change_rate": 0.5,
                "trading_value": 1000 * len(self.calls),
            }

    broker = FakeKisClient()
    monkeypatch.setattr(backend, "_ctx", lambda: (None, broker, None, None))

    df = backend.sector_performance_df()

    assert broker.calls == list(KIS_SECTOR_CODES)
    assert df["name"].iloc[0] == "업종1"
    assert df["price"].iloc[0] == 101.0
    assert df["trading_value"].iloc[-1] == 1000 * len(KIS_SECTOR_CODES)
