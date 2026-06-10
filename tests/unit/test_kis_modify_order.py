from unittest.mock import patch, MagicMock
import pytest
from app.brokers.kis.kis_client import KisClient
from app.config.settings import resolve_settings
from app.common.enums import OrderStatus


def _make_client():
    s = resolve_settings("mock")
    c = KisClient(s)
    c.auth.get_access_token = lambda: "fake-token"
    object.__setattr__(c.settings, "kis_env", "paper")
    object.__setattr__(c.settings, "kis_base_url", "https://openapivts.koreainvestment.com:29443")
    object.__setattr__(c.settings, "kis_app_key", "testkey")
    object.__setattr__(c.settings, "kis_app_secret", "testsecret")
    object.__setattr__(c.settings, "kis_account_no", "12345678")
    object.__setattr__(c.settings, "kis_account_product_code", "01")
    return c


def _resp(body):
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = body
    m.text = str(body)
    return m


def test_modify_order_returns_pending(monkeypatch):
    c = _make_client()
    # Cache an org_no for the order
    c._orders["0000037101"] = {"org_no": "91234", "ord_dvsn": "00", "quantity": 1}
    body = {"rt_cd": "0", "msg_cd": "MAAP0", "msg1": "ok",
            "output": {"ODNO": "0000037102", "KRX_FWDG_ORD_ORGNO": "91234", "ORD_TMD": "150800"}}
    monkeypatch.setattr("requests.request", lambda *a, **kw: _resp(body))
    result = c.modify_order("0000037101", new_price=290000.0, new_quantity=1)
    assert result.status == OrderStatus.PENDING
    assert result.broker_order_id == "0000037102"


def test_modify_order_raises_on_unknown_order(monkeypatch):
    from app.common.errors import BrokerError
    c = _make_client()
    # No cached org_no, lookup also fails
    body = {"rt_cd": "1", "msg_cd": "ERR", "msg1": "fail", "output": []}
    monkeypatch.setattr("requests.request", lambda *a, **kw: _resp(body))
    with pytest.raises(BrokerError):
        c.modify_order("0000099999", new_price=290000.0, new_quantity=1)
