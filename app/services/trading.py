"""app/services/trading — 조건·주문로그·체결·KIS 주문내역·엔진·AI 제안·화이트리스트.

app/services/backend 구현을 도메인별로 재-익스포트한다.
propose() 는 app.agents.research_agent.ConditionProposal 을 반환한다.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal

from app.services.backend import (  # noqa: F401
    add_condition,
    add_whitelist,
    kis_order_history,
    kis_today_orders,
    list_conditions,
    list_order_logs,
    list_whitelist,
    propose,
    recent_fills,
    resolve_symbol_name,
    resolve_symbol_name_map,
    run_engine_once,
    symbol_options,
)

__all__ = [
    "add_condition",
    "add_whitelist",
    "kis_order_history",
    "kis_today_orders",
    "list_conditions",
    "list_order_logs",
    "list_whitelist",
    "propose",
    "recent_fills",
    "resolve_symbol_name",
    "resolve_symbol_name_map",
    "run_engine_once",
    "symbol_options",
    # Service-native (not re-exports from backend)
    "GateResult",
    "save_condition_with_gates",
]


@dataclass
class GateResult:
    status: Literal["saved", "blocked_disclosure", "rejected", "needs_acknowledgement", "error"]
    message: str  # human-readable reason or verdict text
    condition_id: int | None = None
    compliance: Literal["passed", "caution_acked", "skipped", "error"] | None = None


def save_condition_with_gates(
    symbol: str,
    side: str,
    target_price: float,
    qty: int,
    auto: bool,
    *,
    compliance_check: bool = True,
    caution_acknowledged: bool = False,
    progress: Callable[[str], None] | None = None,
) -> GateResult:
    """공시 게이트 + Compliance 검토 후 조건 저장. (Phase 0 → Phase 3 HTTP 게이트 기반)

    호출 흐름:
    1. 공시 게이트 차단 → blocked_disclosure 반환
    2. compliance_check=True이면 compliance-officer 에이전트 검토
       - REJECT/거부 → rejected 반환
       - CAUTION/주의 + caution_acknowledged=False → needs_acknowledgement + verdict 반환
       - CAUTION/주의 + caution_acknowledged=True → 저장 진행
    3. 통과 → add_condition 호출 → saved 반환

    app.services.backend (add_condition, disclosure_gate_state) 와
    app.ui.agents_runtime (ask) 에서 임포트한다 — Phase 0 과도기 의존.
    """
    # Phase 0 transitional imports — will be replaced by HTTP gates in Phase 3
    from app.ui import agents_runtime as ar
    from app.services.backend import add_condition as _add_condition
    from app.services.backend import disclosure_gate_state

    # 1. 공시 게이트 확인
    gate = disclosure_gate_state(symbol)
    if gate.get("blocked"):
        reason = gate.get("reason", "")
        return GateResult(
            status="blocked_disclosure",
            message=f"공시 게이트 차단: {reason}",
        )

    # 2. Compliance 검토
    if compliance_check:
        if progress is not None:
            progress("Compliance 검토 중…")
        verdict_text = ar.ask(
            "compliance-officer",
            f"다음 매매 조건을 법규·세금·거래소 규정 관점에서 검토해주세요: "
            f"{symbol} {side} {int(qty)}주 @ {int(target_price):,}원 (지정가)",
        )
        verdict_lower = verdict_text.lower()
        if "reject" in verdict_lower or "거부" in verdict_lower:
            return GateResult(
                status="rejected",
                message=verdict_text,
            )
        elif "caution" in verdict_lower or "주의" in verdict_lower:
            if not caution_acknowledged:
                return GateResult(
                    status="needs_acknowledgement",
                    message=verdict_text,
                )
            # caution_acknowledged=True → 저장 진행
            _compliance_tag = "caution_acked"
            _verdict_for_result = verdict_text
        elif "호출 오류" in verdict_text:
            # Agent call failed — fail-closed: do NOT save the condition
            return GateResult(
                status="error",
                message=f"Compliance 게이트 평가 불가 (에이전트 오류): {verdict_text}",
                compliance="error",
            )
        else:
            _compliance_tag = "passed"
            _verdict_for_result = verdict_text
    else:
        _compliance_tag = "skipped"
        _verdict_for_result = ""

    # 3. 조건 저장
    cid = _add_condition(
        symbol=symbol,
        side=side,
        target_price=float(target_price),
        quantity=int(qty),
        order_type="LIMIT",
        auto_enabled=auto,
    )
    return GateResult(
        status="saved",
        message=_verdict_for_result if _compliance_tag == "caution_acked" else "조건이 저장되었습니다.",
        condition_id=cid,
        compliance=_compliance_tag,
    )
