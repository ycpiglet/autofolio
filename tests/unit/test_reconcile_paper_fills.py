from __future__ import annotations

from scripts import reconcile_paper_fills as reconcile


def test_candidate_rows_filters_existing_unfilled_and_canceled() -> None:
    rows = [
        {"odno": "0001", "pdno": "055550", "tot_ccld_qty": "1", "cncl_yn": "N"},
        {"odno": "0002", "pdno": "105560", "tot_ccld_qty": "0", "cncl_yn": "N"},
        {"odno": "0003", "pdno": "105560", "tot_ccld_qty": "1", "cncl_yn": "Y"},
        {"odno": "0004", "pdno": "005930", "tot_ccld_qty": "1", "cncl_yn": "N"},
    ]

    candidates = reconcile._candidate_rows(
        rows,
        symbols={"055550", "105560"},
        existing_keys={"4"},
    )

    assert candidates == [rows[0]]


def test_side_and_order_type_normalization() -> None:
    assert reconcile._side_from_code("01") == "SELL"
    assert reconcile._side_from_code("02") == "BUY"
    assert reconcile._order_type_from_row({"ord_unpr": "0"}) == "MARKET"
    assert reconcile._order_type_from_row({"ord_unpr": "70000"}) == "LIMIT"
