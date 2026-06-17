"""CLI-generated pre-market summary storage and rendering.

The summary is intentionally manual-triggered. No scheduler or daemon is started
from this module.
"""
from __future__ import annotations

import datetime as dt
import os
import re
from pathlib import Path
from typing import Any

from app.services.agents import list_agent_infos

ROOT = Path(__file__).resolve().parents[2]
PREMARKET_DIR = Path(os.getenv("AUTOFOLIO_HOME", ".autofolio")) / "premarket"
MARKET_OPEN_REFERENCE = "09:00 KST regular session open"


def generate_summary(
    *,
    target_date: str | None = None,
    save: bool = True,
    limit_symbols: int = 5,
) -> dict[str, Any]:
    """Build a read-only pre-market report and optionally save it to disk."""
    day = target_date or dt.date.today().isoformat()
    generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    agents = list_agent_infos(experts_only=True)
    snapshot = _collect_snapshot(limit_symbols=limit_symbols)
    highlights = _build_highlights(snapshot)
    content = render_summary(
        target_date=day,
        generated_at=generated_at,
        agents=agents,
        snapshot=snapshot,
        highlights=highlights,
    )

    path = summary_path(day)
    if save:
        PREMARKET_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    return {
        "date": day,
        "created_at": generated_at,
        "file": path.name,
        "market_open_reference": MARKET_OPEN_REFERENCE,
        "content": content,
        "highlights": highlights,
        "agents": agents,
        "path": str(path),
    }


def load_summary(target_date: str | None = None) -> dict[str, Any] | None:
    """Load a saved summary. If date is omitted, load the latest one."""
    path = summary_path(target_date) if target_date else latest_summary_path()
    if path is None or not path.exists():
        return None

    content = path.read_text(encoding="utf-8")
    day = _date_from_path(path)
    created_at = _frontmatter_value(content, "created_at") or ""
    return {
        "date": day,
        "created_at": created_at,
        "file": path.name,
        "market_open_reference": MARKET_OPEN_REFERENCE,
        "content": content,
        "highlights": _extract_highlights(content),
        "agents": list_agent_infos(experts_only=True),
    }


def list_summaries(limit: int = 10) -> list[dict[str, str]]:
    if not PREMARKET_DIR.exists():
        return []
    files = sorted(PREMARKET_DIR.glob("PREMARKET_*.md"), reverse=True)[:limit]
    return [{"date": _date_from_path(path), "file": path.name} for path in files]


def summary_path(target_date: str | None) -> Path:
    day = target_date or dt.date.today().isoformat()
    return PREMARKET_DIR / f"PREMARKET_{day.replace('-', '')}.md"


def latest_summary_path() -> Path | None:
    if not PREMARKET_DIR.exists():
        return None
    files = sorted(PREMARKET_DIR.glob("PREMARKET_*.md"), reverse=True)
    return files[0] if files else None


def render_summary(
    *,
    target_date: str,
    generated_at: str,
    agents: list[dict[str, Any]],
    snapshot: dict[str, Any],
    highlights: list[str],
) -> str:
    lines = [
        "---",
        "type: premarket_summary",
        f"date: {target_date}",
        f"created_at: {generated_at}",
        f"market_open_reference: {MARKET_OPEN_REFERENCE}",
        "---",
        "",
        f"# 프리마켓 핵심 요약 — {target_date}",
        "",
        f"> 생성: {generated_at} · 기준: 정규장 시작 전({MARKET_OPEN_REFERENCE})",
        "",
        "## 핵심 요약",
    ]
    lines.extend(f"- {item}" for item in highlights)

    lines.extend([
        "",
        "## 리서치·금융 전문가 에이전트",
        "| 에이전트 | 역할 | 카테고리 |",
        "|---|---|---|",
    ])
    for agent in agents:
        lines.append(
            f"| `{agent['name']}` | {agent.get('role') or '-'} | {agent.get('category') or '-'} |"
        )

    lines.extend(["", "## 시장 스냅샷"])
    _append_table(lines, snapshot.get("indices", []), ["name", "price", "change", "change_rate"])

    lines.extend(["", "## 관심종목"])
    _append_table(lines, snapshot.get("watchlist", []), ["symbol", "name", "price"])

    lines.extend(["", "## 포트폴리오 체크"])
    kpis = snapshot.get("kpis") or {}
    if kpis:
        for key, value in kpis.items():
            lines.append(f"- {key}: {_fmt(value)}")
    else:
        lines.append("- KPI 데이터 없음")

    lines.extend(["", "## 최근 공시 체크"])
    disclosures = snapshot.get("disclosures", [])
    if disclosures:
        _append_table(lines, disclosures, ["symbol", "date", "title", "category"])
    else:
        lines.append("- 최근 공시 없음 또는 데이터 미제공")

    warnings = snapshot.get("warnings", [])
    if warnings:
        lines.extend(["", "## 데이터 경고"])
        lines.extend(f"- {warning}" for warning in warnings)

    lines.extend([
        "",
        "## 운영 메모",
        "- 이 파일은 CLI 명시 실행으로만 생성된다.",
        "- 주문·조건 저장·자동매매 상태를 변경하지 않는 읽기 전용 요약이다.",
        "- 실제 투자 결정 전 최신 시세, 공시, 계좌 상태를 다시 확인한다.",
    ])
    return "\n".join(lines)


def _collect_snapshot(*, limit_symbols: int) -> dict[str, Any]:
    from app.services import backend

    warnings: list[str] = []

    def safe(label: str, fn, default):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"{label}: {exc}")
            return default

    indices = _records(safe("market_indices_df", backend.market_indices_df, None), limit=6)
    watchlist = _records(safe("watchlist", backend.watchlist, None), limit=limit_symbols)
    kpis = safe("kpis", backend.kpis, {})
    whitelist = _records(safe("list_whitelist", backend.list_whitelist, None), limit=limit_symbols)

    disclosures: list[dict[str, Any]] = []
    for row in whitelist:
        symbol = str(row.get("symbol") or "")
        if not symbol:
            continue
        df = safe(f"disclosures_df({symbol})", lambda s=symbol: backend.disclosures_df(s, days=1), None)
        for item in _records(df, limit=3):
            item.setdefault("symbol", symbol)
            disclosures.append(item)

    return {
        "indices": indices,
        "watchlist": watchlist,
        "kpis": kpis if isinstance(kpis, dict) else {},
        "disclosures": disclosures[:8],
        "warnings": warnings,
    }


def _records(value: Any, *, limit: int) -> list[dict[str, Any]]:
    if value is None:
        return []
    if hasattr(value, "head") and hasattr(value, "to_dict"):
        return value.head(limit).to_dict(orient="records")
    if isinstance(value, list):
        return [item for item in value[:limit] if isinstance(item, dict)]
    return []


def _build_highlights(snapshot: dict[str, Any]) -> list[str]:
    highlights = [f"정규장 시작 전 기준점은 {MARKET_OPEN_REFERENCE}이다."]
    indices = snapshot.get("indices") or []
    if indices:
        labels = []
        for item in indices[:3]:
            name = item.get("name") or item.get("code") or "index"
            price = item.get("price")
            change_rate = item.get("change_rate")
            suffix = f"({_fmt(change_rate)}%)" if change_rate not in (None, "") else ""
            labels.append(f"{name} {_fmt(price)}{suffix}".strip())
        highlights.append("시장 지수: " + ", ".join(labels))
    watchlist = snapshot.get("watchlist") or []
    if watchlist:
        highlights.append(f"관심종목 {len(watchlist)}개를 프리마켓 점검 대상으로 포함했다.")
    disclosures = snapshot.get("disclosures") or []
    if disclosures:
        highlights.append(f"최근 공시 {len(disclosures)}건을 확인했다.")
    kpis = snapshot.get("kpis") or {}
    total = kpis.get("총자산") or kpis.get("total_value") or kpis.get("tot_evlu_amt")
    if total not in (None, ""):
        highlights.append(f"포트폴리오 총자산 기준값: {_fmt(total)}")
    if len(highlights) == 1:
        highlights.append("저장된 시장 데이터가 부족해 에이전트 패널과 운영 체크리스트 중심으로 요약했다.")
    return highlights


def _append_table(lines: list[str], rows: list[dict[str, Any]], keys: list[str]) -> None:
    if not rows:
        lines.append("- 데이터 없음")
        return
    lines.append("| " + " | ".join(keys) + " |")
    lines.append("|" + "|".join("---" for _ in keys) + "|")
    for row in rows:
        lines.append("| " + " | ".join(_fmt(row.get(key, "")) for key in keys) + " |")


def _fmt(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:,.2f}".rstrip("0").rstrip(".")
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def _date_from_path(path: Path) -> str:
    match = re.search(r"PREMARKET_(\d{8})", path.name)
    if not match:
        return ""
    raw = match.group(1)
    return f"{raw[:4]}-{raw[4:6]}-{raw[6:]}"


def _frontmatter_value(content: str, key: str) -> str | None:
    pattern = re.compile(rf"^{re.escape(key)}:\s*(.+)$", re.MULTILINE)
    match = pattern.search(content)
    return match.group(1).strip() if match else None


def _extract_highlights(content: str) -> list[str]:
    match = re.search(r"## 핵심 요약\n(?P<body>.*?)(?:\n## |\Z)", content, re.S)
    if not match:
        return []
    highlights: list[str] = []
    for line in match.group("body").splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            highlights.append(stripped[2:])
    return highlights
