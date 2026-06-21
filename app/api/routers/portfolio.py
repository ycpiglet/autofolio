"""Portfolio router — /api/portfolio/*

Endpoints (all require_app_user):
  GET /portfolio/holdings
  GET /portfolio/kpis
  GET /portfolio/asset-curve?days=90
  GET /portfolio/allocation-gap
"""
from __future__ import annotations

from datetime import datetime
import re
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import require_app_user, require_owner_csrf
from app.api.schemas import TableResponse
from app.api.serializers import df_records

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


def _table_payload(df: Any) -> dict[str, Any]:
    payload = df_records(df)
    if hasattr(payload, "model_dump"):
        return payload.model_dump()
    return payload.dict()


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        parsed = float(str(value).replace(",", "").replace("%", "").replace("₩", ""))
    except (TypeError, ValueError):
        return default
    return parsed


def _row_num(row: dict[str, Any], key: str) -> float:
    return _num(row.get(key))


def _row_text(row: dict[str, Any], key: str) -> str:
    return str(row.get(key) or "").strip()


def _is_fallback_name(name: str, ticker: str) -> bool:
    compact = name.replace(" ", "")
    if not compact:
        return True
    if ticker and compact == ticker:
        return True
    return bool(re.fullmatch(r"\d{4,6}", compact))


def _normalize_kpis(raw: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    market_value = sum(_row_num(row, "평가금액") for row in rows)
    unrealized_pnl = _num(raw.get("unrealized_pnl", raw.get("평가손익")))
    total_assets = _num(raw.get("total_assets", raw.get("총자산")), market_value)
    cash = _num(raw.get("cash", raw.get("현금")), max(total_assets - market_value, 0.0))
    cash_ratio = _num(
        raw.get("cash_ratio_pct", raw.get("현금비중")),
        (cash / total_assets * 100.0) if total_assets else 0.0,
    )
    daily_return = _num(raw.get("daily_return_pct", raw.get("일간수익률", raw.get("일손익률"))))
    daily_pnl = _num(raw.get("daily_pnl", raw.get("일간손익")))

    return {
        **raw,
        "as_of": datetime.now().isoformat(timespec="seconds"),
        "total_assets": total_assets,
        "total_market_value": market_value,
        "cash": cash,
        "cash_ratio_pct": cash_ratio,
        "unrealized_pnl": unrealized_pnl,
        "daily_pnl": daily_pnl,
        "daily_return_pct": daily_return,
        "total_return_pct": _num(raw.get("total_return_pct", raw.get("누적손익률"))),
        "monthly_return_pct": _num(raw.get("monthly_return_pct", raw.get("월간수익률"))),
        "holdings_count": len([row for row in rows if _row_num(row, "평가금액") > 0]),
    }


def _group_view(
    rows: list[dict[str, Any]],
    *,
    group_id: str,
    title: str,
    column: str,
) -> dict[str, Any] | None:
    if not any(column in row for row in rows):
        return None

    total_market = sum(_row_num(row, "평가금액") for row in rows)
    buckets: dict[str, dict[str, Any]] = {}
    for row in rows:
        name = _row_text(row, column) or "미분류"
        bucket = buckets.setdefault(
            name,
            {
                "name": name,
                "market_value": 0.0,
                "pnl": 0.0,
                "cost": 0.0,
                "count": 0,
                "symbols": [],
            },
        )
        market = _row_num(row, "평가금액")
        pnl = _row_num(row, "평가손익")
        bucket["market_value"] += market
        bucket["pnl"] += pnl
        bucket["cost"] += max(market - pnl, 0.0)
        bucket["count"] += 1
        ticker = _row_text(row, "티커")
        if ticker:
            bucket["symbols"].append(ticker)

    group_rows = []
    for bucket in buckets.values():
        market = float(bucket["market_value"])
        pnl = float(bucket["pnl"])
        cost = float(bucket["cost"])
        group_rows.append(
            {
                **bucket,
                "weight_pct": round((market / total_market * 100.0) if total_market else 0.0, 1),
                "return_pct": round((pnl / cost * 100.0) if cost else 0.0, 1),
            }
        )
    return {
        "id": group_id,
        "title": title,
        "rows": sorted(group_rows, key=lambda row: row["market_value"], reverse=True),
    }


def _automatic_groups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = [
        ("asset-class", "자산군별", "자산군"),
        ("region", "지역별", "지역"),
        ("sector", "섹터별", "섹터"),
        ("strategy", "전략별", "전략"),
        ("risk-bucket", "위험버킷별", "위험버킷"),
    ]
    groups = [_group_view(rows, group_id=group_id, title=title, column=column) for group_id, title, column in candidates]
    return [group for group in groups if group is not None]


def _saved_groups(
    saved: list[dict[str, Any]],
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_symbol = {_row_text(row, "티커").upper(): row for row in rows if _row_text(row, "티커")}
    result: list[dict[str, Any]] = []
    for group in saved:
        symbols = [str(symbol).upper() for symbol in group.get("symbols", [])]
        members = [by_symbol[symbol] for symbol in symbols if symbol in by_symbol]
        market = sum(_row_num(row, "평가금액") for row in members)
        pnl = sum(_row_num(row, "평가손익") for row in members)
        result.append(
            {
                **group,
                "members": members,
                "rows": members,
                "summary": {
                    "market_value": market,
                    "pnl": pnl,
                    "count": len(members),
                    "symbols": symbols,
                },
            }
        )
    return result


def _concentration(rows: list[dict[str, Any]]) -> dict[str, float]:
    weights = sorted((_row_num(row, "비중") for row in rows), reverse=True)
    return {
        "top1_weight_pct": round(sum(weights[:1]), 1),
        "top3_weight_pct": round(sum(weights[:3]), 1),
        "top5_weight_pct": round(sum(weights[:5]), 1),
        "held_symbols": float(len(weights)),
    }


def _top_movers(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    sorted_rows = sorted(rows, key=lambda row: _row_num(row, "평가손익"), reverse=True)
    contributors = [row for row in sorted_rows if _row_num(row, "평가손익") > 0][:5]
    detractors = [row for row in reversed(sorted_rows) if _row_num(row, "평가손익") < 0][:5]
    return {"contributors": contributors, "detractors": detractors}


def _data_quality(rows: list[dict[str, Any]]) -> dict[str, Any]:
    fallback_names: list[str] = []
    missing_sector: list[str] = []
    for row in rows:
        ticker = _row_text(row, "티커")
        name = _row_text(row, "종목")
        if _is_fallback_name(name, ticker):
            fallback_names.append(ticker or name)
        if not _row_text(row, "섹터"):
            missing_sector.append(ticker or name)
    return {
        "warnings": len(fallback_names) + len(missing_sector),
        "fallback_ticker_name_symbols": fallback_names,
        "missing_sector_symbols": missing_sector,
    }


def _diagnostics(
    rows: list[dict[str, Any]],
    concentration: dict[str, float],
    data_quality: dict[str, Any],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    top1 = _num(concentration.get("top1_weight_pct"))
    top3 = _num(concentration.get("top3_weight_pct"))
    if top1 >= 40:
        items.append(
            {
                "level": "watch",
                "title": "단일 종목 집중",
                "message": f"상위 1종목 비중이 {top1:.1f}%입니다.",
                "action": "보유 목적과 손실 허용 범위를 다시 확인하세요.",
                "symbols": [
                    _row_text(row, "티커")
                    for row in sorted(rows, key=lambda row: _row_num(row, "비중"), reverse=True)[:1]
                    if _row_text(row, "티커")
                ],
            }
        )
    if top3 >= 70:
        items.append(
            {
                "level": "watch",
                "title": "상위 종목 쏠림",
                "message": f"상위 3종목 비중이 {top3:.1f}%입니다.",
                "action": "섹터와 전략 기준으로 분산 상태를 함께 보세요.",
                "symbols": [],
            }
        )
    if data_quality["fallback_ticker_name_symbols"]:
        items.append(
            {
                "level": "info",
                "title": "종목명 보강 필요",
                "message": f"{len(data_quality['fallback_ticker_name_symbols'])}개 종목은 종목명 대신 코드가 표시될 수 있습니다.",
                "action": "관심종목/별칭 메타데이터를 보강하면 그룹 분석이 더 읽기 쉬워집니다.",
                "symbols": data_quality["fallback_ticker_name_symbols"][:5],
            }
        )
    if not items:
        items.append(
            {
                "level": "info",
                "title": "즉시 확인할 위험 신호 없음",
                "message": "현재 데이터 기준으로 큰 집중도 또는 표시 품질 경고가 없습니다.",
                "action": "성과 기여와 목표 배분을 함께 확인하세요.",
                "symbols": [],
            }
        )
    return items


@router.get("/holdings", response_model=TableResponse)
def holdings(
    _session: Annotated[dict[str, Any], Depends(require_app_user)],
) -> TableResponse:
    from app.services import backend

    return df_records(backend.holdings_df())


@router.get("/kpis")
def kpis(
    _session: Annotated[dict[str, Any], Depends(require_app_user)],
) -> dict[str, Any]:
    from app.services import backend

    return backend.kpis()


@router.get("/asset-curve", response_model=TableResponse)
def asset_curve(
    _session: Annotated[dict[str, Any], Depends(require_app_user)],
    days: int = Query(default=90, ge=1, le=3650),
) -> TableResponse:
    from app.services import backend

    return df_records(backend.asset_curve(days))


@router.get("/allocation-gap", response_model=TableResponse)
def allocation_gap(
    _session: Annotated[dict[str, Any], Depends(require_app_user)],
) -> TableResponse:
    from app.services import backend

    return df_records(backend.allocation_gap())


@router.get("/overview")
def overview(
    _session: Annotated[dict[str, Any], Depends(require_app_user)],
) -> dict[str, Any]:
    """Portfolio dashboard aggregate payload.

    This endpoint is read-only. It reuses the existing portfolio backend
    functions and normalizes their older Korean KPI keys into the shape used by
    the Next.js portfolio dashboard.
    """
    from app.services import backend

    holdings_df = backend.holdings_df(include_dividends=False)
    holdings_payload = _table_payload(holdings_df)
    rows = list(holdings_payload["rows"])
    raw_kpis = backend.kpis()
    allocation_payload = _table_payload(backend.allocation_gap())
    concentration = _concentration(rows)
    data_quality = _data_quality(rows)
    saved_groups = _saved_groups(getattr(backend, "list_portfolio_groups", lambda: [])(), rows)

    return {
        "kpis": _normalize_kpis(raw_kpis, rows),
        "holdings": holdings_payload,
        "groups": {
            "automatic": _automatic_groups(rows),
            "manual": saved_groups,
            "saved": saved_groups,
        },
        "diagnostics": _diagnostics(rows, concentration, data_quality),
        "top_movers": _top_movers(rows),
        "concentration": concentration,
        "allocation_gap": allocation_payload,
        "data_quality": data_quality,
    }


@router.post("/groups")
def create_group(
    payload: dict[str, Any],
    _session: Annotated[dict[str, Any], Depends(require_owner_csrf)],
) -> dict[str, Any]:
    from app.services import backend

    return backend.create_portfolio_group(
        name=str(payload.get("name", "")).strip(),
        symbols=[str(symbol) for symbol in payload.get("symbols", [])],
        description=str(payload.get("description") or ""),
        color=str(payload.get("color") or "#3182F6"),
        sort_order=int(payload.get("sort_order") or 0),
    )


@router.put("/groups/{group_id}")
def update_group(
    group_id: str,
    payload: dict[str, Any],
    _session: Annotated[dict[str, Any], Depends(require_owner_csrf)],
) -> dict[str, Any]:
    from app.services import backend

    updated = backend.update_portfolio_group(
        group_id,
        name=str(payload.get("name", "")).strip() if payload.get("name") is not None else None,
        symbols=[str(symbol) for symbol in payload.get("symbols", [])] if payload.get("symbols") is not None else None,
        description=str(payload.get("description")) if payload.get("description") is not None else None,
        color=str(payload.get("color")) if payload.get("color") is not None else None,
        sort_order=int(payload.get("sort_order")) if payload.get("sort_order") is not None else None,
    )
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio group not found")
    return updated


@router.delete("/groups/{group_id}")
def delete_group(
    group_id: str,
    _session: Annotated[dict[str, Any], Depends(require_owner_csrf)],
) -> dict[str, str]:
    from app.services import backend

    if not backend.delete_portfolio_group(group_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio group not found")
    return {"status": "deleted"}
