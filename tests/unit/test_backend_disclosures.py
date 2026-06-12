from __future__ import annotations


class _FakeRepo:
    def __init__(self):
        self.state = {}

    def get_system_state(self, key: str, default=None):
        return self.state.get(key, default)

    def set_system_state(self, key: str, value: str) -> None:
        self.state[key] = value


class _FakeNotifier:
    def __init__(self):
        self.messages = []

    def send(self, text: str) -> None:
        self.messages.append(text)


def test_disclosures_df_uses_kis_client(monkeypatch):
    from app.brokers.kis.kis_client import KisClient
    from app.ui import backend

    class FakeKisClient(KisClient):
        def __init__(self):
            self.calls = []

        def get_disclosures(self, symbol: str, days: int = 1) -> list[dict]:
            self.calls.append((symbol, days))
            return [
                {
                    "date": "20260612",
                    "time": "091500",
                    "symbol": symbol,
                    "title": "분기보고서 제출",
                    "category": "정기공시",
                    "severity": "LOW",
                    "block_order": False,
                    "source": "KRX",
                    "serial": "1",
                }
            ]

    broker = FakeKisClient()
    monkeypatch.setattr(backend, "_ctx", lambda: (_FakeRepo(), broker, None, None))

    df = backend.disclosures_df("005930", days=3)

    assert broker.calls == [("005930", 3)]
    assert df.columns.tolist() == [
        "date",
        "time",
        "symbol",
        "title",
        "category",
        "severity",
        "block_order",
        "source",
        "serial",
    ]
    assert df.iloc[0]["title"] == "분기보고서 제출"


def test_refresh_disclosure_gate_sets_block_flag_and_notifies(monkeypatch):
    from app.brokers.kis.kis_client import KisClient
    from app.ui import backend

    class FakeKisClient(KisClient):
        def __init__(self):
            pass

        def get_disclosures(self, symbol: str, days: int = 1) -> list[dict]:
            return [
                {
                    "date": "20260612",
                    "time": "091500",
                    "symbol": symbol,
                    "title": "삼성전자 유상증자 결정",
                    "category": "주요사항보고서",
                    "severity": "HIGH",
                    "block_order": True,
                    "source": "KRX",
                    "serial": "123",
                }
            ]

    repo = _FakeRepo()
    notifier = _FakeNotifier()
    monkeypatch.setattr(backend, "_ctx", lambda: (repo, FakeKisClient(), None, None))

    result = backend.refresh_disclosure_gate("005930", notify=True, notifier=notifier)
    state = backend.disclosure_gate_state("005930")

    assert result["blocked"] is True
    assert state["blocked"] is True
    assert "유상증자" in state["reason"]
    assert repo.state["compliance_disclosure_block:005930"] == "true"
    assert notifier.messages and "공시 경고" in notifier.messages[0]


def test_refresh_disclosure_gate_clears_flag_when_no_blocking_rows(monkeypatch):
    from app.brokers.kis.kis_client import KisClient
    from app.ui import backend

    class FakeKisClient(KisClient):
        def __init__(self):
            pass

        def get_disclosures(self, symbol: str, days: int = 1) -> list[dict]:
            return [
                {
                    "date": "20260612",
                    "time": "091500",
                    "symbol": symbol,
                    "title": "분기보고서 제출",
                    "category": "정기공시",
                    "severity": "LOW",
                    "block_order": False,
                    "source": "KRX",
                    "serial": "1",
                }
            ]

    repo = _FakeRepo()
    repo.set_system_state("compliance_disclosure_block:005930", "true")
    monkeypatch.setattr(backend, "_ctx", lambda: (repo, FakeKisClient(), None, None))

    result = backend.refresh_disclosure_gate("005930")

    assert result["blocked"] is False
    assert backend.disclosure_gate_state("005930")["blocked"] is False


def test_disclosures_df_returns_empty_for_non_kis_client(monkeypatch):
    from app.ui import backend

    monkeypatch.setattr(backend, "_ctx", lambda: (_FakeRepo(), object(), None, None))

    df = backend.disclosures_df("005930")

    assert df.empty
    assert df.columns.tolist() == backend.DISCLOSURE_COLUMNS
