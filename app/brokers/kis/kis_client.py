from __future__ import annotations

import logging
import time
import calendar
from datetime import date, datetime, timedelta, timezone

import requests

from app.brokers.base import BrokerClient, OrderRequest, OrderResult, Position, PriceQuote
from app.brokers.kis.kis_auth import KisAuth
from app.brokers.kis.constants import (
    KIS_INDEX_CODES,
    KIS_SECTOR_CODES,
    KIS_SECTOR_CODE_TO_NAME,
    KIS_SECTOR_NAMES,
)
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
_PATH_MULTPRICE = "/uapi/domestic-stock/v1/quotations/intstock-multprice"
_PATH_INDEX_PRICE = "/uapi/domestic-stock/v1/quotations/inquire-index-price"
_PATH_KSDINFO_DIVIDEND = "/uapi/domestic-stock/v1/ksdinfo/dividend"
_PATH_ORDER_BOOK = "/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn"
_PATH_NEWS_TITLE = "/uapi/domestic-stock/v1/quotations/news-title"
_PATH_FINANCE_RATIO = "/uapi/domestic-stock/v1/ranking/finance-ratio"
_PATH_BALANCE = "/uapi/domestic-stock/v1/trading/inquire-balance"
_PATH_ORDER_CASH = "/uapi/domestic-stock/v1/trading/order-cash"
_PATH_OVERSEAS_ORDER = "/uapi/overseas-stock/v1/trading/order"
_PATH_RVSECNCL = "/uapi/domestic-stock/v1/trading/order-rvsecncl"
_PATH_DAILY_CCLD = "/uapi/domestic-stock/v1/trading/inquire-daily-ccld"
_PATH_PSBL_RVSECNCL = "/uapi/domestic-stock/v1/trading/inquire-psbl-rvsecncl"
_PATH_CHART = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
_PATH_INTRADAY = "/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"
_PATH_PSBL_ORDER = "/uapi/domestic-stock/v1/trading/inquire-psbl-order"

_TR_PRICE = "FHKST01010100"
_TR_MULTPRICE = "FHKST11300006"
_TR_INDEX_PRICE = "FHPUP02100000"
_TR_KSDINFO_DIVIDEND = "HHKDB669102C0"
_TR_ORDER_BOOK = "FHKST01010200"
_TR_NEWS_TITLE = "FHKST01011800"
_TR_FINANCE_RATIO = "FHPST01750000"
_TR_CHART = "FHKST03010100"  # 일봉, paper/prod 동일 (F* TR — no V prefix needed)
_TR_INTRADAY = "FHKST03010200"  # 분봉, paper/prod 동일 (F* TR)
_TR_BALANCE = "TTTC8434R"
_TR_BUY = "TTTC0012U"
_TR_SELL = "TTTC0011U"
_TR_OVERSEAS_BUY = "TTTT1002U"
_TR_OVERSEAS_SELL = "TTTT1006U"
_TR_RVSECNCL = "TTTC0013U"
_TR_DAILY_CCLD = "TTTC0081R"
_TR_DAILY_CCLD_LONG = "CTSC9215R"
_TR_PSBL_RVSECNCL = "TTTC0084R"
_TR_PSBL_ORDER = "TTTC8908R"

_ORD_DVSN_LIMIT = "00"   # 지정가
_ORD_DVSN_MARKET = "01"  # 시장가 (ORD_UNPR="0")
_ORD_DVSN_CONDITIONAL_LIMIT = "02"
_ORD_DVSN_BEST_LIMIT = "03"
_ORD_DVSN_PRIORITY_LIMIT = "04"
_ORD_DVSN_PRE_OPEN = "05"
_ORD_DVSN_AFTER_CLOSE = "06"
_ORD_DVSN_AFTER_HOURS_SINGLE = "07"
_EXCG_KRX = "KRX"
_NORMAL_SELL_TYPE = "01"
_R3_SELL_TYPES = {"02", "05"}
_OVERSEAS_MARKETS = {"NASD", "NYSE", "AMEX", "SEHK"}
_RVSE_CNCL_MODIFY = "01"  # 정정
_RVSE_CNCL_CANCEL = "02"  # 취소

_DEFAULT_TIMEOUT_SEC = 10
_MAX_BALANCE_PAGES = 20  # 연속조회 무한루프 방지 상한
_MAX_HISTORY_PAGES = 20
_MAX_MULTPRICE_SYMBOLS = 30
_MAX_DIVIDEND_PAGES = 10
_MAX_DISCLOSURE_DAYS = 30
_RATE_LIMIT_MSG_CD = "EGW00201"  # KIS "초당 거래건수 초과" (MVP_SPEC 오류표: 일정 시간 대기)
_DEFAULT_MAX_RETRIES = 2
_DEFAULT_RATE_LIMIT_WAIT_SEC = 0.6
_KST = timezone(timedelta(hours=9))
_INTRADAY_UNITS = {"1", "3", "5", "10", "30", "60"}


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


def _optional_float(value):
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def _optional_int(value, default: int = 0) -> int:
    if value in (None, ""):
        return default
    try:
        return int(float(str(value).replace(",", "")))
    except (TypeError, ValueError):
        return default


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


def _intraday_input_time() -> str:
    return datetime.now(_KST).strftime("%H%M%S")


def _parse_intraday_dt(row: dict) -> datetime | None:
    stamp = f"{row.get('stck_bsop_date') or ''} {row.get('stck_cntg_hour') or ''}"
    try:
        return datetime.strptime(stamp, "%Y%m%d %H%M%S")
    except ValueError:
        return None


def _intraday_row(row: dict) -> dict | None:
    dt = _parse_intraday_dt(row)
    if dt is None:
        return None
    return {
        "datetime": dt.strftime("%Y%m%d %H%M%S"),
        "open": float(row.get("stck_oprc") or 0),
        "high": float(row.get("stck_hgpr") or 0),
        "low": float(row.get("stck_lwpr") or 0),
        "close": float(row.get("stck_prpr") or 0),
        "volume": int(row.get("cntg_vol") or 0),
        "_dt": dt,
    }


def _aggregate_intraday(rows: list[dict], unit: str, count: int) -> list[dict]:
    parsed = [item for row in rows if (item := _intraday_row(row)) is not None]
    parsed.sort(key=lambda item: item["_dt"])
    if count <= 0:
        return []
    if unit == "1":
        return [{k: v for k, v in item.items() if k != "_dt"} for item in parsed[-count:]]

    minutes = int(unit)
    buckets: dict[datetime, list[dict]] = {}
    for item in parsed:
        dt = item["_dt"]
        bucket = dt.replace(minute=dt.minute - (dt.minute % minutes), second=0)
        buckets.setdefault(bucket, []).append(item)

    bars: list[dict] = []
    for bucket in sorted(buckets):
        items = buckets[bucket]
        bars.append(
            {
                "datetime": bucket.strftime("%Y%m%d %H%M%S"),
                "open": items[0]["open"],
                "high": max(item["high"] for item in items),
                "low": min(item["low"] for item in items),
                "close": items[-1]["close"],
                "volume": sum(item["volume"] for item in items),
            }
        )
    return bars[-count:]


def _today_kst() -> date:
    return datetime.now(_KST).date()


def _parse_yyyymmdd(value: str, field_name: str) -> date:
    if len(value) != 8 or not value.isdigit():
        raise ValueError(f"{field_name} must be 'YYYYMMDD' format.")
    return datetime.strptime(value, "%Y%m%d").date()


def _subtract_months(value: date, months: int) -> date:
    month = value.month - months
    year = value.year
    while month <= 0:
        month += 12
        year -= 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _current_year_window(today: date | None = None) -> tuple[str, str]:
    value = today or _today_kst()
    return date(value.year, 1, 1).strftime("%Y%m%d"), date(value.year, 12, 31).strftime("%Y%m%d")


def _order_history_windows(
    start_date: str,
    end_date: str,
    *,
    today: date | None = None,
) -> list[tuple[str, str, str]]:
    start = _parse_yyyymmdd(start_date, "start_date")
    end = _parse_yyyymmdd(end_date, "end_date")
    if end < start:
        raise ValueError("end_date must be on or after start_date.")

    cutoff = _subtract_months(today or _today_kst(), 3)
    if end < cutoff:
        return [(start.strftime("%Y%m%d"), end.strftime("%Y%m%d"), _TR_DAILY_CCLD_LONG)]
    if start >= cutoff:
        return [(start.strftime("%Y%m%d"), end.strftime("%Y%m%d"), _TR_DAILY_CCLD)]

    long_end = cutoff - timedelta(days=1)
    return [
        (start.strftime("%Y%m%d"), long_end.strftime("%Y%m%d"), _TR_DAILY_CCLD_LONG),
        (cutoff.strftime("%Y%m%d"), end.strftime("%Y%m%d"), _TR_DAILY_CCLD),
    ]


_ORDER_HISTORY_FIELDS = [
    "ord_dt",
    "odno",
    "orgn_odno",
    "pdno",
    "sll_buy_dvsn_cd",
    "ord_qty",
    "tot_ccld_qty",
    "rmn_qty",
    "ord_unpr",
    "avg_prvs",
    "cncl_yn",
    "ord_tmd",
    "ord_gno_brno",
]


def _normalize_order_history_row(row: dict) -> dict:
    return {field: row.get(field, "") for field in _ORDER_HISTORY_FIELDS}


def _unique_symbols(symbols: list[str]) -> list[str]:
    seen = set()
    result = []
    for symbol in symbols:
        normalized = str(symbol).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _chunks(items: list[str], size: int) -> list[list[str]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def _multprice_params(symbols: list[str]) -> dict:
    params = {}
    for idx, symbol in enumerate(symbols, start=1):
        params[f"FID_COND_MRKT_DIV_CODE_{idx}"] = "J"
        params[f"FID_INPUT_ISCD_{idx}"] = symbol
    return params


def _multprice_row_price(row: dict) -> tuple[str | None, float | None]:
    symbol = row.get("inter_shrn_iscd") or row.get("stck_shrn_iscd") or row.get("pdno")
    price = _as_float(row.get("inter2_prpr") or row.get("stck_prpr") or row.get("prpr"))
    return symbol, price


def _normalize_dividend_row(row: dict) -> dict:
    return {
        "record_date": row.get("record_date", ""),
        "symbol": row.get("sht_cd", ""),
        "kind": row.get("divi_kind", ""),
        "cash_dividend": _optional_float(row.get("per_sto_divi_amt")) or 0.0,
        "dividend_rate": _optional_float(row.get("divi_rate")),
        "stock_dividend_rate": _optional_float(row.get("stk_divi_rate")),
        "pay_date": row.get("divi_pay_dt", ""),
        "stock_pay_date": row.get("stk_div_pay_dt", ""),
        "stock_kind": row.get("stk_kind", ""),
        "high_dividend": row.get("high_divi_gb", ""),
        "raw": row,
    }


def _first_object(value) -> dict:
    if isinstance(value, dict):
        return value
    if isinstance(value, list):
        return value[0] if value and isinstance(value[0], dict) else {}
    return {}


def _balance_summary(output2) -> dict:
    """Normalize KIS balance summary output.

    KIS balance endpoints can return ``output2`` either as a dict or as a
    one-item list depending on environment/endpoint variant.
    """
    return _first_object(output2)


def _order_book_levels(output: dict) -> list[dict]:
    levels = []
    for level in range(1, 11):
        levels.append(
            {
                "level": level,
                "ask_price": _optional_float(output.get(f"askp{level}")) or 0.0,
                "ask_quantity": _optional_int(output.get(f"askp_rsqn{level}")),
                "bid_price": _optional_float(output.get(f"bidp{level}")) or 0.0,
                "bid_quantity": _optional_int(output.get(f"bidp_rsqn{level}")),
            }
        )
    return levels


def _normalize_side(side: str | Side) -> str:
    value = side.value if isinstance(side, Side) else str(side or "")
    normalized = value.upper()
    if normalized not in {"BUY", "SELL"}:
        raise ValueError("side must be BUY or SELL.")
    return normalized


def estimate_order_book_slippage(
    levels: list[dict],
    side: str | Side,
    quantity: int,
    reference_price: float | None = None,
) -> dict:
    """Estimate marketable execution price from visible 10-level depth."""
    normalized_side = _normalize_side(side)
    requested_quantity = int(quantity)
    if requested_quantity <= 0:
        raise ValueError("quantity must be positive.")

    price_key = "ask_price" if normalized_side == "BUY" else "bid_price"
    quantity_key = "ask_quantity" if normalized_side == "BUY" else "bid_quantity"

    remaining = requested_quantity
    notional = 0.0
    default_reference = None
    for level in levels:
        price = _optional_float(level.get(price_key)) or 0.0
        available = _optional_int(level.get(quantity_key))
        if price <= 0 or available <= 0:
            continue
        if default_reference is None:
            default_reference = price
        take = min(remaining, available)
        notional += take * price
        remaining -= take
        if remaining == 0:
            break

    filled = requested_quantity - remaining
    average_price = notional / filled if filled else None
    reference = reference_price if reference_price is not None else default_reference
    slippage_per_share = None
    slippage_rate = None
    if average_price is not None and reference:
        if normalized_side == "BUY":
            slippage_per_share = average_price - reference
        else:
            slippage_per_share = reference - average_price
        slippage_rate = slippage_per_share / reference * 100

    return {
        "side": normalized_side,
        "requested_quantity": requested_quantity,
        "filled_quantity": filled,
        "unfilled_quantity": remaining,
        "average_price": round(average_price, 4) if average_price is not None else None,
        "notional": round(notional, 2),
        "reference_price": reference,
        "slippage_per_share": round(slippage_per_share, 4) if slippage_per_share is not None else None,
        "slippage_rate": round(slippage_rate, 4) if slippage_rate is not None else None,
    }


_DISCLOSURE_BLOCK_KEYWORDS = (
    "상장폐지",
    "관리종목",
    "거래정지",
    "투자주의환기",
    "불성실공시",
    "감사의견",
    "의견거절",
    "한정의견",
    "횡령",
    "배임",
    "회생",
    "파산",
    "부도",
    "영업정지",
    "유상증자",
    "감자",
    "합병",
    "분할",
    "주요사항보고서",
    "공개매수",
)
_DISCLOSURE_REGULAR_KEYWORDS = ("사업보고서", "반기보고서", "분기보고서", "감사보고서")
_DISCLOSURE_ADHOC_KEYWORDS = ("공시", "조회공시", "수시공시", "결정", "계약", "소송", "잠정")


def classify_disclosure_title(title: str) -> dict:
    """Classify KIS news-title rows for compliance gating."""
    text = str(title or "")
    matched = [keyword for keyword in _DISCLOSURE_BLOCK_KEYWORDS if keyword in text]
    if matched:
        return {
            "category": "주요사항보고서",
            "severity": "HIGH",
            "block_order": True,
            "matched_keywords": matched,
        }

    matched = [keyword for keyword in _DISCLOSURE_REGULAR_KEYWORDS if keyword in text]
    if matched:
        return {
            "category": "정기공시",
            "severity": "LOW",
            "block_order": False,
            "matched_keywords": matched,
        }

    matched = [keyword for keyword in _DISCLOSURE_ADHOC_KEYWORDS if keyword in text]
    if matched:
        return {
            "category": "수시공시",
            "severity": "MEDIUM",
            "block_order": False,
            "matched_keywords": matched,
        }

    return {
        "category": "뉴스/기타",
        "severity": "LOW",
        "block_order": False,
        "matched_keywords": [],
    }


def _normalize_disclosure_row(row: dict, requested_symbol: str = "") -> dict:
    title = row.get("hts_pbnt_titl_cntt", "")
    classification = classify_disclosure_title(title)
    symbols = [
        str(row.get(f"iscd{idx}") or "").strip()
        for idx in range(1, 6)
        if str(row.get(f"iscd{idx}") or "").strip()
    ]
    return {
        "serial": row.get("cntt_usiq_srno", ""),
        "provider": row.get("news_ofer_entp_code", ""),
        "date": row.get("data_dt", ""),
        "time": row.get("data_tm", ""),
        "symbol": requested_symbol or (symbols[0] if symbols else ""),
        "symbols": symbols,
        "title": title,
        "source": row.get("dorg", ""),
        "news_category": row.get("news_lrdv_code", ""),
        "category": classification["category"],
        "severity": classification["severity"],
        "block_order": classification["block_order"],
        "matched_keywords": classification["matched_keywords"],
        "raw": row,
    }


_FINANCE_RATIO_FLOAT_FIELDS = (
    "cptl_op_prfi",
    "cptl_ntin_rate",
    "sale_totl_rate",
    "sale_ntin_rate",
    "bis",
    "lblt_rate",
    "bram_depn",
    "rsrv_rate",
    "grs",
    "op_prfi_inrt",
    "bsop_prfi_inrt",
    "ntin_inrt",
    "equt_inrt",
    "cptl_tnrt",
    "sale_bond_tnrt",
    "totl_aset_inrt",
)


def _normalize_finance_ratio_row(row: dict) -> dict:
    item = {
        "rank": _optional_int(row.get("data_rank")),
        "symbol": row.get("mksc_shrn_iscd", ""),
        "name": row.get("hts_kor_isnm", ""),
        "price": _optional_float(row.get("stck_prpr")),
        "change": _optional_float(row.get("prdy_vrss")),
        "change_sign": row.get("prdy_vrss_sign", ""),
        "change_rate": _optional_float(row.get("prdy_ctrt")),
        "volume": _optional_int(row.get("acml_vol")),
        "stac_month": row.get("stac_month", ""),
        "stac_month_cls_code": row.get("stac_month_cls_code", ""),
        "raw": row,
    }
    for field in _FINANCE_RATIO_FLOAT_FIELDS:
        item[field] = _optional_float(row.get(field))
    return item


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
        self._last_batch_price_stats: dict[str, int] = {}

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
            raise BrokerError(
                f"KIS price response missing stck_prpr for {symbol}: "
                f"rt_cd={data.get('rt_cd')} msg_cd={data.get('msg_cd')} msg1={data.get('msg1')}"
            )
        return PriceQuote(symbol=symbol, price=price)

    def get_finance_ratio_rank(
        self,
        market_code: str = "0000",
        fiscal_year: str | None = None,
        quarter: str = "3",
        sort_code: str = "7",
        limit: int = 50,
    ) -> list[dict]:
        """국내주식 재무비율 순위 조회.

        공식 KIS `finance_ratio` 샘플 기준:
        `/uapi/domestic-stock/v1/ranking/finance-ratio`, TR `FHPST01750000`.
        market_code는 `0000`(전체), `0001`(거래소), `1001`(코스닥), `2001`(KOSPI200).
        """
        code = str(market_code or "").strip()
        if code not in {"0000", "0001", "1001", "2001"}:
            raise ValueError("market_code must be one of 0000, 0001, 1001, 2001.")
        if quarter not in {"0", "1", "2", "3"}:
            raise ValueError("quarter must be one of 0, 1, 2, 3.")
        if sort_code not in {"7", "11", "15", "20"}:
            raise ValueError("sort_code must be one of 7, 11, 15, 20.")
        year = fiscal_year or str(_today_kst().year - 1)
        params = {
            "fid_trgt_cls_code": "0",
            "fid_cond_mrkt_div_code": "J",
            "fid_cond_scr_div_code": "20175",
            "fid_input_iscd": code,
            "fid_div_cls_code": "0",
            "fid_input_price_1": "",
            "fid_input_price_2": "",
            "fid_vol_cnt": "",
            "fid_input_option_1": year,
            "fid_input_option_2": quarter,
            "fid_rank_sort_cls_code": sort_code,
            "fid_blng_cls_code": "0",
            "fid_trgt_exls_cls_code": "0",
        }
        try:
            data, _ = self._request("GET", _PATH_FINANCE_RATIO, _TR_FINANCE_RATIO, params=params)
        except BrokerError as exc:
            logging.getLogger(__name__).warning("get_finance_ratio_rank failed: %s", exc)
            return []
        output = data.get("output") or []
        if isinstance(output, dict):
            output = [output]
        rows = [_normalize_finance_ratio_row(row) for row in output]
        return rows[: max(int(limit), 0)]

    def get_fundamental(self, symbol: str, include_finance_ratio: bool = True) -> dict:
        """PER/PBR/EPS/시가총액 등 기본 재무 지표 조회."""
        code = str(symbol or "").strip()
        if not code:
            raise ValueError("symbol is required.")
        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code}
        try:
            data, _ = self._request("GET", _PATH_PRICE, _TR_PRICE, params=params)
        except BrokerError as exc:
            logging.getLogger(__name__).warning("get_fundamental %s failed: %s", code, exc)
            return {}
        output = data.get("output") or {}
        price = _optional_float(output.get("stck_prpr"))
        fundamental = {
            "symbol": code,
            "price": price,
            "per": _optional_float(output.get("per")),
            "pbr": _optional_float(output.get("pbr")),
            "eps": _optional_float(output.get("eps")),
            "market_cap": _optional_float(output.get("hts_avls")),
            "listed_shares": _optional_int(output.get("lstn_stcn")),
            "raw": {"price": output},
        }
        if include_finance_ratio:
            ratio_rows = self.get_finance_ratio_rank(limit=100)
            ratio = next((row for row in ratio_rows if row.get("symbol") == code), {})
            fundamental["finance_ratio"] = {k: v for k, v in ratio.items() if k != "raw"} if ratio else {}
            fundamental["raw"]["finance_ratio"] = ratio.get("raw", {}) if ratio else {}
        return fundamental

    def get_prices_batch(
        self,
        symbols: list[str],
        max_workers: int = 5,
        batch_size: int = _MAX_MULTPRICE_SYMBOLS,
    ) -> dict[str, float]:
        """복수 종목 현재가 조회.

        공식 `inquire-price-2`는 단일 종목 API다. 실제 복수 종목 시세는
        `intstock-multprice`/`FHKST11300006`가 최대 30종목을 받으므로 이를 우선 사용한다.
        실패하거나 누락된 종목만 기존 단건 `get_current_price()`로 fallback한다.
        """
        unique = _unique_symbols(symbols)
        if not unique:
            return {}
        if batch_size <= 0:
            raise ValueError("batch_size must be positive.")
        batch_size = min(batch_size, _MAX_MULTPRICE_SYMBOLS)

        result: dict[str, float] = {}
        batch_calls = 0
        fallback_symbols: list[str] = []
        for chunk in _chunks(unique, batch_size):
            batch_calls += 1
            try:
                data, _ = self._request("GET", _PATH_MULTPRICE, _TR_MULTPRICE, params=_multprice_params(chunk))
            except BrokerError as exc:
                logging.getLogger(__name__).warning("get_prices_batch chunk failed: %s", exc)
                fallback_symbols.extend(chunk)
                continue

            rows = data.get("output") or data.get("output1") or []
            if isinstance(rows, dict):
                rows = [rows]
            for row in rows:
                symbol, price = _multprice_row_price(row)
                if symbol and price is not None:
                    result[symbol] = price
            fallback_symbols.extend(symbol for symbol in chunk if symbol not in result)

        fallback_calls = 0
        if fallback_symbols:
            from concurrent.futures import ThreadPoolExecutor, as_completed

            with ThreadPoolExecutor(max_workers=min(max_workers, len(fallback_symbols))) as pool:
                futures = {pool.submit(self.get_current_price, sym): sym for sym in fallback_symbols}
                for future in as_completed(futures):
                    sym = futures[future]
                    fallback_calls += 1
                    try:
                        result[sym] = future.result().price
                    except Exception as exc:
                        logging.getLogger(__name__).warning(
                            "get_prices_batch fallback: %s failed: %s", sym, exc
                        )

        self._last_batch_price_stats = {
            "symbols": len(unique),
            "batch_calls": batch_calls,
            "single_fallback_calls": fallback_calls,
            "saved_calls": max(len(unique) - batch_calls - fallback_calls, 0),
        }
        logging.getLogger(__name__).info("get_prices_batch stats: %s", self._last_batch_price_stats)
        return result

    def get_index_price(self, index_code: str) -> dict:
        """국내업종 현재지수 조회. index_code 예: 0001(KOSPI), 1001(KOSDAQ), 2001(KOSPI200)."""
        code = KIS_INDEX_CODES.get(index_code.upper(), index_code) if isinstance(index_code, str) else index_code
        if not code:
            raise ValueError("index_code is required.")
        params = {"FID_COND_MRKT_DIV_CODE": "U", "FID_INPUT_ISCD": code}
        try:
            data, _ = self._request("GET", _PATH_INDEX_PRICE, _TR_INDEX_PRICE, params=params)
            output = data.get("output") or {}
            if isinstance(output, list):
                output = output[0] if output else {}
            price = _as_float(output.get("bstp_nmix_prpr"))
            if price is None:
                raise BrokerError(
                    f"KIS index response missing bstp_nmix_prpr for {code}: "
                    f"rt_cd={data.get('rt_cd')} msg_cd={data.get('msg_cd')} msg1={data.get('msg1')}"
                )
            return {
                "index_code": code,
                "price": price,
                "change": _as_float(output.get("bstp_nmix_prdy_vrss")) or 0.0,
                "change_sign": output.get("prdy_vrss_sign", ""),
                "change_rate": _as_float(output.get("bstp_nmix_prdy_ctrt")) or 0.0,
                "volume": _as_int(output.get("acml_vol")),
                "trading_value": _as_int(output.get("acml_tr_pbmn")),
                "raw": output,
            }
        except BrokerError as exc:
            logging.getLogger(__name__).warning("get_index_price %s failed: %s", code, exc)
            return {}

    def get_sector_price(self, sector_code: str) -> dict:
        """국내 업종 현재지수 조회.

        KIS 현행 샘플에서 업종 시세는 `inquire-index-price`/`FHPUP02100000`를 사용한다.
        sector_code는 `KOSPI_ELECTRONICS` 같은 alias 또는 4자리 업종코드를 받을 수 있다.
        """
        key_or_code = str(sector_code or "").strip()
        if not key_or_code:
            raise ValueError("sector_code is required.")
        alias = key_or_code.upper()
        code = KIS_SECTOR_CODES.get(alias, key_or_code)
        data = self.get_index_price(code)
        if not data:
            return {}
        return {
            "sector_code": code,
            "name": KIS_SECTOR_NAMES.get(alias) or KIS_SECTOR_CODE_TO_NAME.get(code, code),
            "price": data.get("price"),
            "change": data.get("change"),
            "change_sign": data.get("change_sign", ""),
            "change_rate": data.get("change_rate"),
            "volume": data.get("volume", 0),
            "trading_value": data.get("trading_value", 0),
            "raw": data.get("raw", {}),
        }

    def get_order_book(self, symbol: str, market: str = "J") -> dict:
        """국내주식 10단계 호가/예상체결 조회.

        공식 KIS `inquire_asking_price_exp_ccn` 샘플 기준:
        `/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn`,
        TR `FHKST01010200`. market은 `J`(KRX), `NX`(NXT), `UN`(통합)을 받는다.
        """
        code = str(symbol or "").strip()
        if not code:
            raise ValueError("symbol is required.")
        market_code = str(market or "").strip().upper()
        if market_code not in {"J", "NX", "UN"}:
            raise ValueError("market must be one of J, NX, UN.")

        params = {
            "FID_COND_MRKT_DIV_CODE": market_code,
            "FID_INPUT_ISCD": code,
        }
        try:
            data, _ = self._request("GET", _PATH_ORDER_BOOK, _TR_ORDER_BOOK, params=params)
        except BrokerError as exc:
            logging.getLogger(__name__).warning("get_order_book %s failed: %s", code, exc)
            return {}

        output1 = _first_object(data.get("output1"))
        output2 = _first_object(data.get("output2"))
        levels = _order_book_levels(output1)
        return {
            "symbol": output1.get("stck_shrn_iscd") or code,
            "market": market_code,
            "accepted_at": output1.get("aspr_acpt_hour", ""),
            "current_price": _optional_float(output1.get("stck_prpr")),
            "expected_price": _optional_float(output1.get("antc_cnpr") or output2.get("antc_cnpr")),
            "expected_volume": _optional_int(output1.get("antc_vol") or output2.get("antc_vol")),
            "total_ask_quantity": _optional_int(output1.get("total_askp_rsqn")),
            "total_bid_quantity": _optional_int(output1.get("total_bidp_rsqn")),
            "levels": levels,
            "raw": {"output1": output1, "output2": output2},
        }

    def get_disclosures(self, symbol: str, days: int = 1) -> list[dict]:
        """종합 시황/공시(제목) 조회.

        공식 KIS `news_title` 샘플 기준:
        `/uapi/domestic-stock/v1/quotations/news-title`, TR `FHKST01011800`.
        KIS 샘플명은 news-title이지만 API 설명은 "종합 시황/공시(제목)"이다.
        """
        code = str(symbol or "").strip()
        if not code:
            raise ValueError("symbol is required.")
        lookup_days = int(days)
        if lookup_days <= 0:
            raise ValueError("days must be positive.")
        lookup_days = min(lookup_days, _MAX_DISCLOSURE_DAYS)

        rows: list[dict] = []
        seen: set[tuple[str, str, str]] = set()
        today = _today_kst()
        for offset in range(lookup_days):
            query_date = (today - timedelta(days=offset)).strftime("%Y%m%d")
            params = {
                "FID_NEWS_OFER_ENTP_CODE": "",
                "FID_COND_MRKT_CLS_CODE": "",
                "FID_INPUT_ISCD": code,
                "FID_TITL_CNTT": "",
                "FID_INPUT_DATE_1": query_date,
                "FID_INPUT_HOUR_1": "",
                "FID_RANK_SORT_CLS_CODE": "01",
                "FID_INPUT_SRNO": "",
            }
            try:
                data, _ = self._request("GET", _PATH_NEWS_TITLE, _TR_NEWS_TITLE, params=params)
            except BrokerError as exc:
                logging.getLogger(__name__).warning("get_disclosures %s failed: %s", code, exc)
                return []

            output = data.get("output") or []
            if isinstance(output, dict):
                output = [output]
            for row in output:
                item = _normalize_disclosure_row(row, requested_symbol=code)
                if not item["date"]:
                    item["date"] = query_date
                key = (str(item.get("serial") or ""), str(item.get("date") or ""), str(item.get("title") or ""))
                if key in seen:
                    continue
                seen.add(key)
                rows.append(item)

        rows.sort(key=lambda item: (item.get("date") or "", item.get("time") or ""), reverse=True)
        return rows

    def get_dividend_info(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict:
        """예탁원정보(배당일정) 조회.

        공식 KIS `ksdinfo_dividend` 샘플 기준:
        `/uapi/domestic-stock/v1/ksdinfo/dividend`, TR `HHKDB669102C0`.
        start_date/end_date는 YYYYMMDD이며, 생략 시 현재 KST 연도 전체를 조회한다.
        """
        code = str(symbol or "").strip()
        if not code:
            raise ValueError("symbol is required.")
        default_start, default_end = _current_year_window()
        start = start_date or default_start
        end = end_date or default_end
        _parse_yyyymmdd(start, "start_date")
        _parse_yyyymmdd(end, "end_date")
        if end < start:
            raise ValueError("end_date must be on or after start_date.")

        params = {
            "CTS": "",
            "GB1": "0",
            "F_DT": start,
            "T_DT": end,
            "SHT_CD": code,
            "HIGH_GB": "",
        }
        rows: list[dict] = []
        tr_cont = ""
        try:
            for _ in range(_MAX_DIVIDEND_PAGES):
                data, resp_headers = self._request(
                    "GET",
                    _PATH_KSDINFO_DIVIDEND,
                    _TR_KSDINFO_DIVIDEND,
                    params=params,
                    tr_cont=tr_cont,
                )
                output = data.get("output1") or []
                if isinstance(output, dict):
                    output = [output]
                rows.extend(_normalize_dividend_row(row) for row in output)
                next_flag = (resp_headers.get("tr_cont") or "").strip()
                if next_flag in ("M", "F"):
                    params["CTS"] = (data.get("cts") or data.get("CTS") or params["CTS"]).strip()
                    tr_cont = "N"
                else:
                    break
        except BrokerError as exc:
            logging.getLogger(__name__).warning("get_dividend_info %s failed: %s", code, exc)
            return {}

        rows.sort(key=lambda item: (item.get("record_date") or "", item.get("pay_date") or ""))
        annual_cash = sum(float(row.get("cash_dividend") or 0.0) for row in rows)
        latest_rate = next(
            (row["dividend_rate"] for row in reversed(rows) if row.get("dividend_rate") is not None),
            None,
        )
        return {
            "symbol": code,
            "start_date": start,
            "end_date": end,
            "annual_cash_dividend": annual_cash,
            "latest_dividend_rate": latest_rate,
            "records": rows,
        }

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
            summary = _balance_summary(data.get("output2"))
            return _optional_float(summary.get("dnca_tot_amt")) or 0.0
        except BrokerError:
            return 0.0

    def get_account_summary(self) -> dict:
        """KIS account summary from balance ``output2``.

        Returns normalized numeric fields used by the UI. Broker errors or
        missing summary rows return an empty dict so callers can fallback.
        """
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
        except BrokerError:
            return {}

        summary = _balance_summary(data.get("output2"))
        if not summary:
            return {}
        return {
            "scts_evlu_amt": _optional_float(summary.get("scts_evlu_amt")) or 0.0,
            "dnca_tot_amt": _optional_float(summary.get("dnca_tot_amt")) or 0.0,
            "tot_evlu_amt": _optional_float(summary.get("tot_evlu_amt")) or 0.0,
            "nass_amt": _optional_float(summary.get("nass_amt")) or 0.0,
            "pchs_amt_smtl_amt": _optional_float(summary.get("pchs_amt_smtl_amt")) or 0.0,
            "evlu_pfls_smtl_amt": _optional_float(summary.get("evlu_pfls_smtl_amt")) or 0.0,
            "source": "kis",
        }

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
            # KIS는 환경/계좌에 따라 매수가능수량을 psbl_qty 대신
            # nrcvb_buy_qty(미수 없는 매수가능수량) / max_buy_qty 로만 채워주기도 한다.
            # 모의(paper) inquire-psbl-order 응답에는 psbl_qty 자체가 없어서
            # psbl_qty만 보면 항상 0이 되어 매수가 막힌다 → 보수적 순서로 fallback.
            max_quantity = (
                _as_int(output.get("psbl_qty"))
                or _as_int(output.get("nrcvb_buy_qty"))
                or _as_int(output.get("max_buy_qty"))
            )
            return {
                "max_quantity": max_quantity,
                "available_cash": float(output.get("ord_psbl_cash") or 0),
            }
        except BrokerError as exc:
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
            logging.getLogger(__name__).warning("get_price_history %s failed: %s", symbol, exc)
            return []

    def get_intraday_chart(
        self,
        symbol: str,
        time_unit: str = "1",
        count: int = 100,
        input_time: str | None = None,
    ) -> list[dict]:
        """당일 분봉 OHLCV.

        KIS API는 1분 단위 output2를 반환한다. time_unit이 3/5/10/30/60이면
        클라이언트에서 OHLCV를 집계한다. input_time은 HHMMSS이며 None이면 KST 현재시각.

        반환 항목: {datetime: 'YYYYMMDD HHMMSS', open, high, low, close: float, volume: int}.
        BrokerError 시 [] 반환.
        """
        unit = str(time_unit)
        if unit not in _INTRADAY_UNITS:
            raise ValueError(f"time_unit must be one of {sorted(_INTRADAY_UNITS)}.")
        params = {
            "FID_ETC_CLS_CODE": "",
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": symbol,
            "FID_INPUT_HOUR_1": input_time or _intraday_input_time(),
            "FID_PW_DATA_INCU_YN": "Y",
        }
        try:
            data, _ = self._request("GET", _PATH_INTRADAY, _TR_INTRADAY, params=params)
            return _aggregate_intraday(data.get("output2") or [], unit, count)
        except BrokerError as exc:
            logging.getLogger(__name__).warning("get_intraday_chart %s failed: %s", symbol, exc)
            return []

    # ----- 주문 -------------------------------------------------------------
    def place_order(self, request: OrderRequest) -> OrderResult:
        cano, acnt = self._account()
        is_buy = request.side == Side.BUY
        prod_tr = _TR_BUY if is_buy else _TR_SELL
        self._enforce_r3_prod_guard(request)
        ord_dvsn, ord_unpr = self._domestic_order_price_fields(request)
        sell_type = "" if is_buy else str(request.sell_type or _NORMAL_SELL_TYPE)
        if sell_type not in {"", _NORMAL_SELL_TYPE, *_R3_SELL_TYPES}:
            raise BrokerError(f"Unsupported SLL_TYPE: {sell_type}")

        body = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt,
            "PDNO": request.symbol,
            "ORD_DVSN": ord_dvsn,
            "ORD_QTY": str(int(request.quantity)),
            "ORD_UNPR": ord_unpr,
            "EXCG_ID_DVSN_CD": str(request.market or _EXCG_KRX).upper(),
            "SLL_TYPE": sell_type,
            "CNDT_PRIC": "",
        }
        data, _ = self._request("POST", _PATH_ORDER_CASH, prod_tr, json_body=body)
        output = data.get("output") or {}
        odno = output.get("ODNO")
        if not odno:
            raise BrokerError(
                f"KIS order accepted but ODNO missing: "
                f"rt_cd={data.get('rt_cd')} msg_cd={data.get('msg_cd')} msg1={data.get('msg1')}"
            )
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

    def place_overseas_order(
        self,
        *,
        symbol: str,
        market: str,
        side: Side,
        quantity: int,
        price: float,
        currency: str = "USD",
        allow_prod_r3_order: bool = False,
    ) -> OrderResult:
        """Place a paper-gated overseas stock order.

        The method builds the KIS overseas order payload but refuses prod by
        default. Actual prod activation requires a separate hardguard review.
        """
        if not self._paper and not allow_prod_r3_order:
            raise BrokerError("Overseas stock prod order requires explicit R3 hardguard review.")
        market = market.upper()
        if market not in _OVERSEAS_MARKETS:
            raise BrokerError(f"Unsupported overseas market: {market}")
        if quantity <= 0:
            raise BrokerError("Overseas order quantity must be positive.")
        if price <= 0:
            raise BrokerError("Overseas order price must be positive.")

        cano, acnt = self._account()
        prod_tr = _TR_OVERSEAS_BUY if side == Side.BUY else _TR_OVERSEAS_SELL
        body = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt,
            "OVRS_EXCG_CD": market,
            "PDNO": symbol,
            "ORD_DVSN": _ORD_DVSN_LIMIT,
            "ORD_QTY": str(int(quantity)),
            "OVRS_ORD_UNPR": f"{float(price):.2f}",
            "ORD_SVR_DVSN_CD": "0",
            "ORD_CRNCY_CD": currency.upper(),
        }
        data, _ = self._request("POST", _PATH_OVERSEAS_ORDER, prod_tr, json_body=body)
        output = data.get("output") or {}
        odno = output.get("ODNO") or output.get("odno")
        if not odno:
            raise BrokerError(
                f"KIS overseas order accepted but ODNO missing: "
                f"rt_cd={data.get('rt_cd')} msg_cd={data.get('msg_cd')} msg1={data.get('msg1')}"
            )
        self._orders[odno] = {
            "org_no": output.get("KRX_FWDG_ORD_ORGNO"),
            "ord_dvsn": _ORD_DVSN_LIMIT,
            "quantity": int(quantity),
            "market": market,
            "currency": currency.upper(),
        }
        return OrderResult(
            broker_order_id=odno,
            status=OrderStatus.PENDING,
            message=f"KIS overseas order accepted: {data.get('msg1')}",
        )

    def _domestic_order_price_fields(self, request: OrderRequest) -> tuple[str, str]:
        session = str(request.order_session or "REGULAR").upper()
        if session == "PRE_OPEN_SINGLE" or request.order_type == OrderType.MOO:
            return _ORD_DVSN_PRE_OPEN, "0"
        if session == "AFTER_CLOSE_SINGLE" or request.order_type == OrderType.MOC:
            return _ORD_DVSN_AFTER_CLOSE, "0"
        if session == "AFTER_HOURS_SINGLE":
            return _ORD_DVSN_AFTER_HOURS_SINGLE, "0"
        if request.order_type == OrderType.MARKET:
            return _ORD_DVSN_MARKET, "0"
        if request.order_type == OrderType.CONDITIONAL_LIMIT:
            if request.price is None:
                raise BrokerError("Conditional limit order requires a price.")
            return _ORD_DVSN_CONDITIONAL_LIMIT, str(int(round(request.price)))
        if request.order_type == OrderType.BEST_LIMIT:
            if request.price is None:
                raise BrokerError("Best limit order requires a price.")
            return _ORD_DVSN_BEST_LIMIT, str(int(round(request.price)))
        if request.order_type == OrderType.PRIORITY_LIMIT:
            if request.price is None:
                raise BrokerError("Priority limit order requires a price.")
            return _ORD_DVSN_PRIORITY_LIMIT, str(int(round(request.price)))
        if request.order_type not in {OrderType.LIMIT, OrderType.IOC, OrderType.FOK, OrderType.STOP_LIMIT}:
            raise BrokerError(f"KIS domestic cash order type is not supported: {request.order_type.value}")
        if request.price is None:
            raise BrokerError("Limit order requires a price.")
        return _ORD_DVSN_LIMIT, str(int(round(request.price)))

    def _enforce_r3_prod_guard(self, request: OrderRequest) -> None:
        if self._paper:
            return
        if bool(request.metadata.get("allow_prod_r3_order")):
            return
        r3_surface = (
            str(request.order_session or "REGULAR").upper() != "REGULAR"
            or str(request.sell_type or _NORMAL_SELL_TYPE) in _R3_SELL_TYPES
            or request.order_type
            not in {
                OrderType.LIMIT,
                OrderType.MARKET,
            }
            or str(request.product_type or "EQUITY").upper()
            not in {"EQUITY", "ETF", "ETN", "REIT"}
        )
        if r3_surface:
            raise BrokerError("R3 domestic order option requires explicit prod hardguard review.")

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
            "RVSE_CNCL_DVSN_CD": _RVSE_CNCL_MODIFY,
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

    def get_today_orders(self, *, suppress_errors: bool = True) -> list[dict]:
        """오늘 전체 주문 내역 조회 (KIS inquire-daily-ccld, ODNO="" = 전체).

        Returns list of dicts with keys: odno, pdno, sll_buy_dvsn_cd, ord_qty,
        tot_ccld_qty, rmn_qty, ord_unpr, avg_prvs, cncl_yn, ord_tmd.
        기본값은 UI 호환을 위해 장애 시 빈 리스트를 반환한다.
        검증 스크립트는 ``suppress_errors=False``로 fail-closed 호출할 수 있다.
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
        rows: list[dict] = []
        tr_cont = ""
        try:
            for _ in range(_MAX_HISTORY_PAGES):
                data, resp_headers = self._request(
                    "GET",
                    _PATH_DAILY_CCLD,
                    _TR_DAILY_CCLD,
                    params=params,
                    tr_cont=tr_cont,
                )
                output = data.get("output1") or []
                if isinstance(output, dict):
                    output = [output]
                rows.extend(output)
                next_flag = (resp_headers.get("tr_cont") or "").strip()
                if next_flag in ("M", "F"):
                    params["CTX_AREA_FK100"] = (data.get("ctx_area_fk100") or "").strip()
                    params["CTX_AREA_NK100"] = (data.get("ctx_area_nk100") or "").strip()
                    tr_cont = "N"
                else:
                    break
            return rows
        except BrokerError as exc:
            logging.getLogger(__name__).warning("get_today_orders failed: %s", exc)
            if not suppress_errors:
                raise
            return []


    def get_order_history(self, start_date: str, end_date: str) -> list[dict]:
        """날짜 범위 주문 내역 조회 (당일 포함). inquire-daily-ccld ODNO="" 전체 조회.

        start_date, end_date: 'YYYYMMDD' 형식.
        반환: canonical 주문내역 dict 리스트.
        최근 3개월 이내는 TTTC0081R/VTTC0081R, 3개월 이전은 CTSC9215R/VTSC9215R.
        BrokerError 시 [] 반환.
        """
        cano, acnt = self._account()
        windows = _order_history_windows(start_date, end_date)
        rows: list[dict] = []
        try:
            for window_start, window_end, prod_tr in windows:
                params = {
                    "CANO": cano, "ACNT_PRDT_CD": acnt,
                    "INQR_STRT_DT": window_start,
                    "INQR_END_DT": window_end,
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
                tr_cont = ""
                for _ in range(_MAX_HISTORY_PAGES):
                    data, resp_headers = self._request(
                        "GET",
                        _PATH_DAILY_CCLD,
                        prod_tr,
                        params=params,
                        tr_cont=tr_cont,
                    )
                    rows.extend(_normalize_order_history_row(row) for row in (data.get("output1") or []))
                    next_flag = (resp_headers.get("tr_cont") or "").strip()
                    if next_flag in ("M", "F"):
                        params["CTX_AREA_FK100"] = (data.get("ctx_area_fk100") or "").strip()
                        params["CTX_AREA_NK100"] = (data.get("ctx_area_nk100") or "").strip()
                        tr_cont = "N"
                    else:
                        break
            return rows
        except BrokerError as exc:
            logging.getLogger(__name__).warning("get_order_history failed: %s", exc)
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
