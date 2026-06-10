from __future__ import annotations

import time
from datetime import datetime

import requests

from app.brokers.base import BrokerClient, OrderRequest, OrderResult, Position, PriceQuote
from app.brokers.kis.kis_auth import KisAuth
from app.common.enums import OrderStatus, OrderType, Side
from app.common.errors import BrokerError, ConfigurationError
from app.config.settings import Settings, settings

# ---------------------------------------------------------------------------
# KIS Open API — 국내주식 REST 엔드포인트/TR ID
# 근거: docs/KIS_API_SPEC.md (공식 koreainvestment/open-trading-api 2025 샘플 교차검증).
# TR ID 는 실전(prod) 기준값을 둔다. 모의(paper)는 선두 T/J/C → V 치환(_to_paper_tr).
# 시세 F* TR 은 paper/prod 동일이라 치환하지 않는다.
# ---------------------------------------------------------------------------
_PATH_PRICE = "/uapi/domestic-stock/v1/quotations/inquire-price"
_PATH_BALANCE = "/uapi/domestic-stock/v1/trading/inquire-balance"
_PATH_ORDER_CASH = "/uapi/domestic-stock/v1/trading/order-cash"
_PATH_RVSECNCL = "/uapi/domestic-stock/v1/trading/order-rvsecncl"
_PATH_DAILY_CCLD = "/uapi/domestic-stock/v1/trading/inquire-daily-ccld"
_PATH_PSBL_RVSECNCL = "/uapi/domestic-stock/v1/trading/inquire-psbl-rvsecncl"
_PATH_CHART = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
_PATH_PSBL_ORDER = "/uapi/domestic-stock/v1/trading/inquire-psbl-order"

_TR_PRICE = "FHKST01010100"
_TR_CHART = "FHKST03010100"  # 일봉, paper/prod 동일 (F* TR — no V prefix needed)
_TR_BALANCE = "TTTC8434R"
_TR_BUY = "TTTC0012U"
_TR_SELL = "TTTC0011U"
_TR_RVSECNCL = "TTTC0013U"
_TR_DAILY_CCLD = "TTTC0081R"
_TR_PSBL_RVSECNCL = "TTTC0084R"
_TR_PSBL_ORDER = "TTTC8908R"

_ORD_DVSN_LIMIT = "00"   # 지정가
_ORD_DVSN_MARKET = "01"  # 시장가 (ORD_UNPR="0")
_EXCG_KRX = "KRX"
_RVSE_CNCL_CANCEL = "02"  # 01=정정, 02=취소

_DEFAULT_TIMEOUT_SEC = 10
_MAX_BALANCE_PAGES = 20  # 연속조회 무한루프 방지 상한
_RATE_LIMIT_MSG_CD = "EGW00201"  # KIS "초당 거래건수 초과" (MVP_SPEC 오류표: 일정 시간 대기)
_DEFAULT_MAX_RETRIES = 2
_DEFAULT_RATE_LIMIT_WAIT_SEC = 0.6


def _to_paper_tr(tr_id: str) -> str:
    """모의투자 TR ID 변환: 선두 T/J/C → V. 시세(F*)는 변환 대상이 아니다."""
    if tr_id and tr_id[0] in ("T", "J", "C"):
        return "V" + tr_id[1:]
    return tr_id


def _safe_json(resp) -> dict:
    """KIS 응답 JSON 파싱(실패 시 빈 dict). KIS 본문은 UTF-8 이므로 .json() 으로 한글이 깨지지 않는다."""
    try:
        data = resp.json()
        return data if isinstance(data, dict) else {}
    except ValueError:
        return {}


def _safe_text(resp) -> str:
    try:
        resp.encoding = resp.encoding or "utf-8"
        return resp.text
    except Exception:  # noqa: BLE001 — 진단용 폴백
        return ""


def _as_int(value, default: int = 0) -> int:
    """KIS 숫자 응답은 문자열(때로 빈 값)로 온다."""
    if value in (None, ""):
        return default
    return int(float(value))


def _as_float(value):
    if value in (None, ""):
        return None
    return float(value)


def _odno_eq(a, b) -> bool:
    """주문번호는 zero-padding 이 다를 수 있어 선행 0 무시 비교."""
    return str(a or "").lstrip("0") == str(b or "").lstrip("0")


def _tick_size(price: float) -> int:
    """KRX 호가단위."""
    if price < 2_000:
        return 1
    if price < 5_000:
        return 5
    if price < 20_000:
        return 10
    if price < 50_000:
        return 50
    if price < 200_000:
        return 100
    if price < 500_000:
        return 500
    return 1_000


class KisClient(BrokerClient):
    """한국투자증권 Open API adapter (국내주식).

    동작 방식
    ---------
    - ``KIS_ENV`` (paper/prod) 에 따라 base URL 과 TR ID 가 함께 전환된다.
      자격증명·엔드포인트 해석은 ``app.config.settings.resolve_settings`` 단일 지점이 담당.
    - 모든 응답은 ``rt_cd == "0"`` 이면 성공, 아니면 ``msg_cd``+``msg1`` 로 ``BrokerError``.
    - 주문(``place_order``)은 KIS 가 *접수*(주문번호 ODNO 발급)만 응답하므로 즉시 체결을
      보장하지 않는다. 따라서 ``PENDING`` + ODNO 를 반환하고, 체결 여부는
      ``get_order_status`` 가 일별주문체결조회로 판정한다(엔진의 pending-poll 흐름과 일치).

    안전
    ----
    이 어댑터는 *충실한 실행자*다. 자동매매 ON/OFF·킬스위치·화이트리스트·거래시간·주문한도
    같은 안전 게이트는 상위(SafetyChecker/엔진/UI)에서 강제한다(MVP_SPEC §10/오류표).
    실주문은 paper 검증 후, 사람 승인 하에 1주 수동 테스트부터 시작한다.
    """

    def __init__(self, app_settings: Settings = settings):
        self.settings = app_settings
        self.auth = KisAuth(app_settings)
        self._paper = (app_settings.kis_env or "").lower() == "paper"
        self._timeout = _DEFAULT_TIMEOUT_SEC
        self._max_retries = _DEFAULT_MAX_RETRIES
        self._rate_limit_wait = _DEFAULT_RATE_LIMIT_WAIT_SEC
        # place_order 응답의 KRX_FWDG_ORD_ORGNO 를 캐시 → 같은 프로세스 내 취소에 사용.
        self._orders: dict[str, dict] = {}

    # ----- 내부 헬퍼 --------------------------------------------------------
    def _tr(self, prod_tr_id: str) -> str:
        return _to_paper_tr(prod_tr_id) if self._paper else prod_tr_id

    def _account(self) -> tuple[str, str]:
        cano = self.settings.kis_account_no
        acnt = self.settings.kis_account_product_code
        if not cano or not acnt:
            raise ConfigurationError(
                "KIS account (CANO/ACNT_PRDT_CD) is required for this call. "
                "Set KIS_<ENV>_ACCOUNT_NO and KIS_<ENV>_ACCOUNT_PRODUCT_CODE."
            )
        return cano, acnt

    def _headers(self, prod_tr_id: str) -> dict:
        token = self.auth.get_access_token()
        return {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {token}",
            "appkey": self.settings.kis_app_key,
            "appsecret": self.settings.kis_app_secret,
            "tr_id": self._tr(prod_tr_id),
            "custtype": "P",
            "tr_cont": "",
        }

    def _request(
        self,
        method: str,
        path: str,
        prod_tr_id: str,
        *,
        params: dict | None = None,
        json_body: dict | None = None,
        tr_cont: str = "",
    ) -> tuple[dict, dict]:
        if not self.settings.kis_base_url:
            raise ConfigurationError("KIS_BASE_URL is not set; cannot call KIS API.")
        url = self.settings.kis_base_url.rstrip("/") + path

        for attempt in range(self._max_retries + 1):
            headers = self._headers(prod_tr_id)
            if tr_cont:
                headers["tr_cont"] = tr_cont
            try:
                resp = requests.request(
                    method, url, headers=headers, params=params, json=json_body, timeout=self._timeout
                )
            except requests.RequestException as exc:
                raise BrokerError(
                    f"KIS {prod_tr_id} request error: {type(exc).__name__}: {exc}"
                ) from exc

            data = _safe_json(resp)
            msg_cd = data.get("msg_cd")

            # 레이트리밋(초당 거래건수 초과): 잠시 대기 후 재시도.
            if msg_cd == _RATE_LIMIT_MSG_CD and attempt < self._max_retries:
                time.sleep(self._rate_limit_wait)
                continue

            if resp.status_code >= 400:
                detail = data.get("msg1") or _safe_text(resp)
                raise BrokerError(f"KIS {prod_tr_id} HTTP {resp.status_code}: {msg_cd} {detail}")
            if str(data.get("rt_cd")) != "0":
                raise BrokerError(f"KIS {prod_tr_id} rejected: {msg_cd} {data.get('msg1')}")
            return data, dict(resp.headers)

        # 재시도 소진(레이트리밋 지속).
        raise BrokerError(
            f"KIS {prod_tr_id} rate-limited ({_RATE_LIMIT_MSG_CD}) after {self._max_retries} retries."
        )

    # ----- 시세 -------------------------------------------------------------
    def get_current_price(self, symbol: str) -> PriceQuote:
        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": symbol}
        data, _ = self._request("GET", _PATH_PRICE, _TR_PRICE, params=params)
        output = data.get("output") or {}
        raw = output.get("stck_prpr")
        price = _as_float(raw)
        if price is None:
            raise BrokerError(f"KIS price response missing stck_prpr for {symbol}: {data}")
        return PriceQuote(symbol=symbol, price=price)

    # ----- 잔고 -------------------------------------------------------------
    def get_positions(self) -> list[Position]:
        cano, acnt = self._account()
        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",  # 종목별
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "00",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }
        positions: list[Position] = []
        tr_cont = ""
        for _ in range(_MAX_BALANCE_PAGES):
            data, resp_headers = self._request(
                "GET", _PATH_BALANCE, _TR_BALANCE, params=params, tr_cont=tr_cont
            )
            for row in data.get("output1") or []:
                qty = _as_int(row.get("hldg_qty"))
                if qty == 0:
                    continue
                positions.append(
                    Position(
                        symbol=row.get("pdno", ""),
                        quantity=qty,
                        avg_price=_as_float(row.get("pchs_avg_pric")),
                    )
                )
            next_flag = (resp_headers.get("tr_cont") or "").strip()
            if next_flag in ("M", "F"):
                params["CTX_AREA_FK100"] = (data.get("ctx_area_fk100") or "").strip()
                params["CTX_AREA_NK100"] = (data.get("ctx_area_nk100") or "").strip()
                tr_cont = "N"
            else:
                break
        return positions

    def get_cash_balance(self) -> float:
        """예수금(D+2 결제 가능 현금). output2.dnca_tot_amt. 실패 시 0.0 반환."""
        cano, acnt = self._account()
        params = {
            "CANO": cano, "ACNT_PRDT_CD": acnt,
            "AFHR_FLPR_YN": "N", "OFL_YN": "", "INQR_DVSN": "02",
            "UNPR_DVSN": "01", "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N", "PRCS_DVSN": "01",
            "CTX_AREA_FK100": "", "CTX_AREA_NK100": "",
        }
        try:
            data, _ = self._request("GET", _PATH_BALANCE, _TR_BALANCE, params=params)
            return float(data.get("output2", {}).get("dnca_tot_amt") or 0)
        except BrokerError:
            return 0.0

    def get_buying_power(self, symbol: str, price: float) -> dict:
        """종목별 매수가능수량·금액 조회. inquire-psbl-order.

        반환: {max_quantity: int, available_cash: float}.
        BrokerError 시 {max_quantity: 0, available_cash: 0.0} 반환.
        """
        cano, acnt = self._account()
        tick = _tick_size(price)
        adjusted = int(price // tick * tick)
        params = {
            "CANO": cano, "ACNT_PRDT_CD": acnt,
            "PDNO": symbol,
            "ORD_UNPR": str(adjusted),
            "ORD_DVSN": _ORD_DVSN_LIMIT,
            "CMA_EVLU_AMT_ICLD_YN": "N",
            "OVRS_ICLD_YN": "N",
        }
        try:
            data, _ = self._request("GET", _PATH_PSBL_ORDER, _TR_PSBL_ORDER, params=params)
            output = data.get("output") or {}
            return {
                "max_quantity": int(output.get("psbl_qty") or 0),
                "available_cash": float(output.get("ord_psbl_cash") or 0),
            }
        except BrokerError as exc:
            import logging
            logging.getLogger(__name__).warning("get_buying_power %s failed: %s", symbol, exc)
            return {"max_quantity": 0, "available_cash": 0.0}

    def get_price_history(self, symbol: str, period: str = "D", count: int = 100) -> list[dict]:
        """일봉(D)/주봉(W)/월봉(M) OHLCV. count 건 상한. BrokerError 시 [] 반환.

        반환 항목: {date: str(YYYYMMDD), open, high, low, close: float, volume: int}.
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": symbol,
            "FID_INPUT_DATE_1": "",
            "FID_INPUT_DATE_2": "",
            "FID_PERIOD_DIV_CODE": period,
            "FID_ORG_ADJ_PRC": "0",
        }
        try:
            data, _ = self._request("GET", _PATH_CHART, _TR_CHART, params=params)
            rows = data.get("output2") or []
            return [
                {
                    "date": r["stck_bsop_date"],
                    "open": float(r.get("stck_oprc") or 0),
                    "high": float(r.get("stck_hgpr") or 0),
                    "low": float(r.get("stck_lwpr") or 0),
                    "close": float(r.get("stck_clpr") or 0),
                    "volume": int(r.get("acml_vol") or 0),
                }
                for r in rows[:count]
                if r.get("stck_bsop_date")
            ]
        except BrokerError as exc:
            import logging
            logging.getLogger(__name__).warning("get_price_history %s failed: %s", symbol, exc)
            return []

    # ----- 주문 -------------------------------------------------------------
    def place_order(self, request: OrderRequest) -> OrderResult:
        cano, acnt = self._account()
        is_buy = request.side == Side.BUY
        is_market = request.order_type == OrderType.MARKET
        prod_tr = _TR_BUY if is_buy else _TR_SELL

        if is_market:
            ord_dvsn = _ORD_DVSN_MARKET
            ord_unpr = "0"
        else:
            if request.price is None:
                raise BrokerError("Limit order requires a price.")
            ord_dvsn = _ORD_DVSN_LIMIT
            ord_unpr = str(int(round(request.price)))  # KRX 주식 호가는 정수

        body = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt,
            "PDNO": request.symbol,
            "ORD_DVSN": ord_dvsn,
            "ORD_QTY": str(int(request.quantity)),
            "ORD_UNPR": ord_unpr,
            "EXCG_ID_DVSN_CD": _EXCG_KRX,
            "SLL_TYPE": "" if is_buy else "01",
            "CNDT_PRIC": "",
        }
        data, _ = self._request("POST", _PATH_ORDER_CASH, prod_tr, json_body=body)
        output = data.get("output") or {}
        odno = output.get("ODNO")
        if not odno:
            raise BrokerError(f"KIS order accepted but ODNO missing: {data}")
        self._orders[odno] = {
            "org_no": output.get("KRX_FWDG_ORD_ORGNO"),
            "ord_dvsn": ord_dvsn,
            "quantity": int(request.quantity),
        }
        return OrderResult(
            broker_order_id=odno,
            status=OrderStatus.PENDING,
            message=f"KIS order accepted: {data.get('msg1')}",
        )

    def cancel_order(self, broker_order_id: str) -> OrderResult:
        cano, acnt = self._account()
        ctx = self._orders.get(broker_order_id, {})
        org_no = ctx.get("org_no") or self._lookup_org_no(broker_order_id)
        if not org_no:
            return OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.FAILED,
                message="Cannot cancel: KRX forwarding order org number unknown for this order.",
            )
        body = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt,
            "KRX_FWDG_ORD_ORGNO": org_no,
            "ORGN_ODNO": broker_order_id,
            "ORD_DVSN": ctx.get("ord_dvsn", _ORD_DVSN_LIMIT),
            "RVSE_CNCL_DVSN_CD": _RVSE_CNCL_CANCEL,
            "ORD_QTY": "0",
            "ORD_UNPR": "0",
            "QTY_ALL_ORD_YN": "Y",
            "EXCG_ID_DVSN_CD": _EXCG_KRX,
            "CNDT_PRIC": "",
        }
        try:
            data, _ = self._request("POST", _PATH_RVSECNCL, _TR_RVSECNCL, json_body=body)
        except BrokerError as exc:
            return OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.FAILED,
                message=str(exc),
            )
        return OrderResult(
            broker_order_id=broker_order_id,
            status=OrderStatus.CANCELED,
            message=data.get("msg1"),
        )

    def modify_order(self, broker_order_id: str, new_price: float, new_quantity: int) -> OrderResult:
        """주문 정정 — 지정가 가격/수량 변경. order-rvsecncl RVSE_CNCL_DVSN_CD=01.

        broker_order_id에 대응하는 org_no는 _orders 캐시 또는 _lookup_org_no로 조회한다.
        """
        cano, acnt = self._account()
        ctx = self._orders.get(broker_order_id, {})
        org_no = ctx.get("org_no") or self._lookup_org_no(broker_order_id)
        if not org_no:
            raise BrokerError(
                f"Cannot modify order {broker_order_id}: KRX_FWDG_ORD_ORGNO not found."
            )
        tick = _tick_size(new_price)
        adjusted_price = int(new_price // tick * tick)
        body = {
            "CANO": cano, "ACNT_PRDT_CD": acnt,
            "KRX_FWDG_ORD_ORGNO": org_no,
            "ORGN_ODNO": broker_order_id,
            "ORD_DVSN": ctx.get("ord_dvsn", _ORD_DVSN_LIMIT),
            "RVSE_CNCL_DVSN_CD": "01",  # 정정
            "ORD_QTY": str(int(new_quantity)),
            "ORD_UNPR": str(adjusted_price),
            "QTY_ALL_ORD_YN": "N",
            "EXCG_ID_DVSN_CD": _EXCG_KRX,
            "CNDT_PRIC": "",
        }
        data, _ = self._request("POST", _PATH_RVSECNCL, _TR_RVSECNCL, json_body=body)
        output = data.get("output") or {}
        new_odno = output.get("ODNO") or broker_order_id
        if new_odno and new_odno != broker_order_id:
            self._orders[new_odno] = {
                "org_no": output.get("KRX_FWDG_ORD_ORGNO") or org_no,
                "ord_dvsn": ctx.get("ord_dvsn", _ORD_DVSN_LIMIT),
                "quantity": int(new_quantity),
            }
        return OrderResult(
            broker_order_id=new_odno,
            status=OrderStatus.PENDING,
            message=f"Order modified: {data.get('msg1')}",
        )

    def get_order_status(self, broker_order_id: str) -> OrderResult:
        cano, acnt = self._account()
        today = datetime.now().strftime("%Y%m%d")
        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt,
            "INQR_STRT_DT": today,
            "INQR_END_DT": today,
            "SLL_BUY_DVSN_CD": "00",
            "INQR_DVSN": "00",
            "PDNO": "",
            "CCLD_DVSN": "00",
            "ORD_GNO_BRNO": "",
            "ODNO": broker_order_id,
            "INQR_DVSN_3": "00",
            "INQR_DVSN_1": "",
            "EXCG_ID_DVSN_CD": _EXCG_KRX,
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }
        data, _ = self._request("GET", _PATH_DAILY_CCLD, _TR_DAILY_CCLD, params=params)
        rows = data.get("output1") or []
        row = next((r for r in rows if _odno_eq(r.get("odno"), broker_order_id)), None)
        if row is None:
            return OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.PENDING,
                message="Order not found in today's fills (assumed pending).",
            )
        if str(row.get("cncl_yn", "")).upper() == "Y":
            return OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.CANCELED,
                message="Order canceled.",
            )
        ord_qty = _as_int(row.get("ord_qty"))
        ccld_qty = _as_int(row.get("tot_ccld_qty"))
        rmn_qty = _as_int(row.get("rmn_qty"), default=ord_qty - ccld_qty)
        if rmn_qty == 0 and ccld_qty > 0:
            return OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.FILLED,
                filled_price=_as_float(row.get("avg_prvs")),
                filled_quantity=ccld_qty,
                message="Order filled.",
            )
        return OrderResult(
            broker_order_id=broker_order_id,
            status=OrderStatus.PENDING,
            filled_quantity=ccld_qty,
            message=f"Partial/pending: {ccld_qty}/{ord_qty} filled.",
        )

    def get_today_orders(self) -> list[dict]:
        """오늘 전체 주문 내역 조회 (KIS inquire-daily-ccld, ODNO="" = 전체).

        Returns list of dicts with keys: odno, pdno, sll_buy_dvsn_cd, ord_qty,
        tot_ccld_qty, rmn_qty, ord_unpr, avg_prvs, cncl_yn, ord_tmd.
        모의투자 미지원 시 빈 리스트 반환.
        """
        cano, acnt = self._account()
        today = datetime.now().strftime("%Y%m%d")
        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt,
            "INQR_STRT_DT": today,
            "INQR_END_DT": today,
            "SLL_BUY_DVSN_CD": "00",
            "INQR_DVSN": "00",
            "PDNO": "",
            "CCLD_DVSN": "00",
            "ORD_GNO_BRNO": "",
            "ODNO": "",
            "INQR_DVSN_3": "00",
            "INQR_DVSN_1": "",
            "EXCG_ID_DVSN_CD": _EXCG_KRX,
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }
        try:
            data, _ = self._request("GET", _PATH_DAILY_CCLD, _TR_DAILY_CCLD, params=params)
            return data.get("output1") or []
        except BrokerError as exc:
            import logging
            logging.getLogger(__name__).warning("get_today_orders failed: %s", exc)
            return []

    # ----- 취소용 거래소 주문조직번호 조회 (캐시 미스 시 best-effort) ----------
    def _lookup_org_no(self, broker_order_id: str) -> str | None:
        cano, acnt = self._account()
        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt,
            "INQR_DVSN_1": "0",
            "INQR_DVSN_2": "0",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }
        try:
            data, _ = self._request(
                "GET", _PATH_PSBL_RVSECNCL, _TR_PSBL_RVSECNCL, params=params
            )
        except BrokerError:
            # paper 미지원 가능(docs/KIS_API_SPEC.md 경고 C). 캐시된 org_no 가 없으면 취소 불가.
            return None
        for row in data.get("output") or []:
            if _odno_eq(row.get("odno"), broker_order_id):
                return row.get("ord_gno_brno")
        return None
