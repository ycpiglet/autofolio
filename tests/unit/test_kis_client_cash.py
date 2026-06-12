from unittest.mock import patch, MagicMock
import pytest
import app.brokers.kis.kis_client as kc
from app.brokers.kis.kis_client import KisClient
from app.config.settings import Settings


def _make_client():
    s = Settings(
        kis_env="paper",
        kis_base_url="https://openapivts.koreainvestment.com:29443",
        kis_app_key="testkey",
        kis_app_secret="testsecret",
        kis_account_no="12345678",
        kis_account_product_code="01",
        kis_token_path="/oauth2/tokenP",
    )
    c = KisClient(s)
    c.auth.get_access_token = lambda: "fake-token"
    return c


def _resp(body: dict):
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = body
    m.text = str(body)
    return m


def test_get_cash_balance_returns_float(monkeypatch):
    c = _make_client()
    body = {"rt_cd": "0", "msg_cd": "MAAP0", "msg1": "ok",
            "output1": [], "output2": {"dnca_tot_amt": "5000000"}}
    monkeypatch.setattr(kc.requests, "request", lambda *a, **kw: _resp(body))
    cash = c.get_cash_balance()
    assert cash == 5_000_000.0


def test_get_cash_balance_accepts_list_output2(monkeypatch):
    c = _make_client()
    body = {"rt_cd": "0", "msg_cd": "MAAP0", "msg1": "ok",
            "output1": [], "output2": [{"dnca_tot_amt": "5000000"}]}
    monkeypatch.setattr(kc.requests, "request", lambda *a, **kw: _resp(body))
    cash = c.get_cash_balance()
    assert cash == 5_000_000.0


def test_get_cash_balance_missing_output2_returns_zero(monkeypatch):
    c = _make_client()
    body = {"rt_cd": "0", "msg_cd": "MAAP0", "msg1": "ok",
            "output1": [], "output2": {}}
    monkeypatch.setattr(kc.requests, "request", lambda *a, **kw: _resp(body))
    cash = c.get_cash_balance()
    assert cash == 0.0


def test_get_account_summary_accepts_list_output2(monkeypatch):
    c = _make_client()
    body = {
        "rt_cd": "0",
        "msg_cd": "MAAP0",
        "msg1": "ok",
        "output1": [],
        "output2": [{
            "scts_evlu_amt": "1000000",
            "dnca_tot_amt": "5000000",
            "tot_evlu_amt": "6000000",
            "nass_amt": "6000000",
            "pchs_amt_smtl_amt": "900000",
            "evlu_pfls_smtl_amt": "100000",
        }],
    }
    monkeypatch.setattr(kc.requests, "request", lambda *a, **kw: _resp(body))
    summary = c.get_account_summary()
    assert summary["source"] == "kis"
    assert summary["dnca_tot_amt"] == 5_000_000.0
    assert summary["tot_evlu_amt"] == 6_000_000.0
    assert summary["evlu_pfls_smtl_amt"] == 100_000.0


def test_get_cash_balance_broker_error_returns_zero(monkeypatch):
    from app.common.errors import BrokerError
    c = _make_client()
    body = {"rt_cd": "1", "msg_cd": "ERR", "msg1": "fail", "output2": {}}
    monkeypatch.setattr(kc.requests, "request", lambda *a, **kw: _resp(body))
    cash = c.get_cash_balance()
    assert cash == 0.0
