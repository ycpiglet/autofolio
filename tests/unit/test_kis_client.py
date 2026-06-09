"""KisClient 단위 테스트 — 네트워크 없이 requests.request 를 페이크로 대체.

검증: 요청 헤더/파라미터/바디 구성, paper TR ID 변환, 응답 파싱, rt_cd envelope 오류.
실주문/실시세를 호출하지 않으므로 안전하다(전부 in-memory).
"""
from __future__ import annotations

import pytest

import app.brokers.kis.kis_client as kc
from app.brokers.kis.kis_client import KisClient, _to_paper_tr
from app.brokers.base import OrderRequest
from app.common.enums import OrderStatus, OrderType, Side
from app.common.errors import BrokerError
from app.config.settings import Settings


class FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200, headers: dict | None = None):
        self._payload = payload
        self.status_code = status_code
        self.headers = headers or {}
        self.text = str(payload)

    def json(self) -> dict:
        return self._payload


def make_client(monkeypatch, responder, *, env: str = "paper") -> tuple[KisClient, list[dict]]:
    """responder(call: dict) -> FakeResponse. calls 리스트에 모든 호출이 기록된다."""
    calls: list[dict] = []

    def fake_request(method, url, headers=None, params=None, json=None, timeout=None):
        call = {"method": method, "url": url, "headers": headers or {}, "params": params, "json": json}
        calls.append(call)
        return responder(call)

    monkeypatch.setattr(kc.requests, "request", fake_request)

    s = Settings(
        kis_env=env,
        kis_app_key="appkey-x",
        kis_app_secret="appsecret-y",
        kis_account_no="12345678",
        kis_account_product_code="01",
        kis_base_url="https://paper.example:29443",
        kis_token_path="/oauth2/tokenP",
    )
    client = KisClient(s)
    monkeypatch.setattr(client.auth, "get_access_token", lambda: "tkn-123")
    return client, calls


def _ok(output=None, output1=None, output2=None, headers=None, **extra):
    payload = {"rt_cd": "0", "msg_cd": "OK", "msg1": "정상처리"}
    if output is not None:
        payload["output"] = output
    if output1 is not None:
        payload["output1"] = output1
    if output2 is not None:
        payload["output2"] = output2
    payload.update(extra)
    return FakeResponse(payload, headers=headers or {})


# --------------------------------------------------------------------------- #
# TR 변환
# --------------------------------------------------------------------------- #
def test_to_paper_tr_converts_tjc_prefix():
    assert _to_paper_tr("TTTC0012U") == "VTTC0012U"
    assert _to_paper_tr("TTTC8434R") == "VTTC8434R"
    assert _to_paper_tr("CTSC9215R") == "VTSC9215R"


def test_to_paper_tr_keeps_quotation_f_prefix():
    assert _to_paper_tr("FHKST01010100") == "FHKST01010100"


# --------------------------------------------------------------------------- #
# 시세
# --------------------------------------------------------------------------- #
def test_get_current_price_parses_stck_prpr(monkeypatch):
    client, calls = make_client(monkeypatch, lambda call: _ok(output={"stck_prpr": "71500"}))
    quote = client.get_current_price("005930")

    assert quote.symbol == "005930"
    assert quote.price == 71500.0
    c = calls[0]
    assert c["method"] == "GET"
    assert c["url"].endswith("/uapi/domestic-stock/v1/quotations/inquire-price")
    # 시세 TR 은 paper 에서도 변환되지 않는다.
    assert c["headers"]["tr_id"] == "FHKST01010100"
    assert c["headers"]["custtype"] == "P"
    assert c["headers"]["authorization"] == "Bearer tkn-123"
    assert c["params"] == {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": "005930"}


def test_get_current_price_missing_field_raises(monkeypatch):
    client, _ = make_client(monkeypatch, lambda call: _ok(output={}))
    with pytest.raises(BrokerError):
        client.get_current_price("005930")


# --------------------------------------------------------------------------- #
# 잔고
# --------------------------------------------------------------------------- #
def test_get_positions_parses_and_skips_zero(monkeypatch):
    rows = [
        {"pdno": "005930", "hldg_qty": "10", "pchs_avg_pric": "70000"},
        {"pdno": "069500", "hldg_qty": "0", "pchs_avg_pric": "35000"},  # 0주 → 제외
    ]
    client, calls = make_client(monkeypatch, lambda call: _ok(output1=rows, output2=[{}]))
    positions = client.get_positions()

    assert len(positions) == 1
    assert positions[0].symbol == "005930"
    assert positions[0].quantity == 10
    assert positions[0].avg_price == 70000.0
    # paper 잔고 TR 변환 확인.
    assert calls[0]["headers"]["tr_id"] == "VTTC8434R"
    assert calls[0]["params"]["CANO"] == "12345678"
    assert calls[0]["params"]["ACNT_PRDT_CD"] == "01"


def test_get_positions_paginates_on_tr_cont(monkeypatch):
    page1 = _ok(
        output1=[{"pdno": "005930", "hldg_qty": "1", "pchs_avg_pric": "70000"}],
        output2=[{}],
        headers={"tr_cont": "M"},
        ctx_area_fk100="FK",
        ctx_area_nk100="NK",
    )
    page2 = _ok(
        output1=[{"pdno": "069500", "hldg_qty": "2", "pchs_avg_pric": "35000"}],
        output2=[{}],
        headers={"tr_cont": "D"},
    )
    seq = [page1, page2]
    client, calls = make_client(monkeypatch, lambda call: seq.pop(0))
    positions = client.get_positions()

    assert [p.symbol for p in positions] == ["005930", "069500"]
    assert len(calls) == 2
    # 2번째 호출은 연속조회 키를 echo 하고 tr_cont=N.
    assert calls[1]["headers"]["tr_cont"] == "N"
    assert calls[1]["params"]["CTX_AREA_FK100"] == "FK"
    assert calls[1]["params"]["CTX_AREA_NK100"] == "NK"


# --------------------------------------------------------------------------- #
# 주문
# --------------------------------------------------------------------------- #
def test_place_buy_limit_builds_body_and_returns_pending(monkeypatch):
    resp = _ok(output={"KRX_FWDG_ORD_ORGNO": "06010", "ODNO": "0000117057", "ORD_TMD": "101010"})
    client, calls = make_client(monkeypatch, lambda call: resp)
    result = client.place_order(
        OrderRequest(symbol="005930", side=Side.BUY, order_type=OrderType.LIMIT, quantity=1, price=70000.0)
    )

    assert result.status == OrderStatus.PENDING
    assert result.broker_order_id == "0000117057"

    c = calls[0]
    assert c["method"] == "POST"
    assert c["url"].endswith("/uapi/domestic-stock/v1/trading/order-cash")
    assert c["headers"]["tr_id"] == "VTTC0012U"  # paper 매수
    body = c["json"]
    assert body["PDNO"] == "005930"
    assert body["ORD_DVSN"] == "00"   # 지정가
    assert body["ORD_QTY"] == "1"
    assert body["ORD_UNPR"] == "70000"
    assert body["SLL_TYPE"] == ""     # 매수는 공란
    assert body["EXCG_ID_DVSN_CD"] == "KRX"

    # org_no 캐시 확인 (취소에 사용).
    assert client._orders["0000117057"]["org_no"] == "06010"


def test_place_sell_market_sets_unpr_zero(monkeypatch):
    resp = _ok(output={"KRX_FWDG_ORD_ORGNO": "06010", "ODNO": "0000200000", "ORD_TMD": "101111"})
    client, calls = make_client(monkeypatch, lambda call: resp)
    result = client.place_order(
        OrderRequest(symbol="005930", side=Side.SELL, order_type=OrderType.MARKET, quantity=3, price=None)
    )

    assert result.status == OrderStatus.PENDING
    body = calls[0]["json"]
    assert calls[0]["headers"]["tr_id"] == "VTTC0011U"  # paper 매도
    assert body["ORD_DVSN"] == "01"   # 시장가
    assert body["ORD_UNPR"] == "0"
    assert body["ORD_QTY"] == "3"
    assert body["SLL_TYPE"] == "01"   # 매도


def test_place_order_rejected_envelope_raises(monkeypatch):
    bad = FakeResponse({"rt_cd": "1", "msg_cd": "APBK0919", "msg1": "주문가능금액부족"})
    client, _ = make_client(monkeypatch, lambda call: bad)
    with pytest.raises(BrokerError) as exc:
        client.place_order(
            OrderRequest(symbol="005930", side=Side.BUY, order_type=OrderType.LIMIT, quantity=1, price=70000.0)
        )
    assert "APBK0919" in str(exc.value)


# --------------------------------------------------------------------------- #
# 취소
# --------------------------------------------------------------------------- #
def test_cancel_uses_cached_org_no(monkeypatch):
    resp = _ok(output={"KRX_FWDG_ORD_ORGNO": "06010", "ODNO": "9999", "ORD_TMD": "101212"})
    client, calls = make_client(monkeypatch, lambda call: resp)
    client._orders["0000117057"] = {"org_no": "06010", "ord_dvsn": "00", "quantity": 1}

    result = client.cancel_order("0000117057")

    assert result.status == OrderStatus.CANCELED
    body = calls[0]["json"]
    assert calls[0]["headers"]["tr_id"] == "VTTC0013U"
    assert body["ORGN_ODNO"] == "0000117057"
    assert body["KRX_FWDG_ORD_ORGNO"] == "06010"
    assert body["RVSE_CNCL_DVSN_CD"] == "02"  # 취소
    assert body["QTY_ALL_ORD_YN"] == "Y"


def test_cancel_without_org_no_and_lookup_fails_returns_failed(monkeypatch):
    # 캐시에 없음 + inquire-psbl-rvsecncl 가 rt_cd!=0 (paper 미지원 시나리오) → 취소 불가.
    def responder(call):
        if call["url"].endswith("inquire-psbl-rvsecncl"):
            return FakeResponse({"rt_cd": "1", "msg_cd": "X", "msg1": "모의 미지원"})
        return _ok(output={"ODNO": "x"})

    client, _ = make_client(monkeypatch, responder)
    result = client.cancel_order("unknown-odno")
    assert result.status == OrderStatus.FAILED
    assert "unknown" in result.message.lower() or "org" in result.message.lower()


# --------------------------------------------------------------------------- #
# 체결조회
# --------------------------------------------------------------------------- #
def test_get_order_status_filled(monkeypatch):
    rows = [{"odno": "0000117057", "ord_qty": "10", "tot_ccld_qty": "10", "rmn_qty": "0",
             "avg_prvs": "70050", "cncl_yn": "N"}]
    client, _ = make_client(monkeypatch, lambda call: _ok(output1=rows, output2=[{}]))
    result = client.get_order_status("0000117057")

    assert result.status == OrderStatus.FILLED
    assert result.filled_quantity == 10
    assert result.filled_price == 70050.0


def test_get_order_status_canceled(monkeypatch):
    rows = [{"odno": "0000117057", "ord_qty": "10", "tot_ccld_qty": "0", "rmn_qty": "0", "cncl_yn": "Y"}]
    client, _ = make_client(monkeypatch, lambda call: _ok(output1=rows, output2=[{}]))
    assert client.get_order_status("0000117057").status == OrderStatus.CANCELED


def test_get_order_status_partial_is_pending(monkeypatch):
    rows = [{"odno": "0000117057", "ord_qty": "10", "tot_ccld_qty": "4", "rmn_qty": "6", "cncl_yn": "N"}]
    client, _ = make_client(monkeypatch, lambda call: _ok(output1=rows, output2=[{}]))
    result = client.get_order_status("0000117057")
    assert result.status == OrderStatus.PENDING
    assert result.filled_quantity == 4


def test_get_order_status_not_found_is_pending(monkeypatch):
    client, _ = make_client(monkeypatch, lambda call: _ok(output1=[], output2=[{}]))
    assert client.get_order_status("nope").status == OrderStatus.PENDING


# --------------------------------------------------------------------------- #
# envelope / 레이트리밋
# --------------------------------------------------------------------------- #
def test_request_retries_on_rate_limit_then_succeeds(monkeypatch):
    seq = [
        FakeResponse({"rt_cd": "1", "msg_cd": "EGW00201", "msg1": "초당 거래건수 초과"}, status_code=500),
        _ok(output={"stck_prpr": "70000"}),
    ]
    client, calls = make_client(monkeypatch, lambda call: seq.pop(0))
    client._rate_limit_wait = 0  # 테스트 가속
    quote = client.get_current_price("005930")

    assert quote.price == 70000.0
    assert len(calls) == 2  # 1회 재시도 후 성공


def test_request_http_error_reports_parsed_korean_msg(monkeypatch):
    bad = FakeResponse({"rt_cd": "1", "msg_cd": "EGW00123", "msg1": "권한이 없습니다"}, status_code=403)
    client, _ = make_client(monkeypatch, lambda call: bad)
    with pytest.raises(BrokerError) as exc:
        client.get_current_price("005930")
    msg = str(exc.value)
    assert "EGW00123" in msg
    assert "권한이 없습니다" in msg  # mojibake 아님
