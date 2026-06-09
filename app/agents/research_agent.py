from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConditionProposal:
    symbol: str
    side: str
    target_price: float
    quantity: int
    order_type: str
    allow_market_fallback: bool
    rationale: str
    risk_note: str


class ResearchAgent:
    '''
    MVP용 읽기/제안 전용 리서치 에이전트.

    실제 LLM 연결은 Future Roadmap이다.
    현재는 사용자가 선택한 화이트리스트 종목과 현재가를 받아
    보수적인 예시 조건을 생성한다.
    '''

    def propose_price_condition(
        self,
        *,
        symbol: str,
        current_price: float,
        side: str = "BUY",
        quantity: int = 1,
    ) -> ConditionProposal:
        side = side.upper()
        if side == "BUY":
            target_price = round(current_price * 0.99)
            rationale = "현재가보다 1% 낮은 보수적 매수 대기 조건 예시."
            risk_note = "가격이 목표가에 도달해도 추가 하락 가능성이 있으므로 자동주문은 기본 OFF로 저장해야 함."
        elif side == "SELL":
            target_price = round(current_price * 1.03)
            rationale = "현재가보다 3% 높은 목표 매도 조건 예시."
            risk_note = "목표가 도달 전 가격이 하락할 수 있으며, 손절 조건은 MVP 범위에 포함되지 않음."
        else:
            raise ValueError("side must be BUY or SELL")

        return ConditionProposal(
            symbol=symbol,
            side=side,
            target_price=float(target_price),
            quantity=quantity,
            order_type="LIMIT",
            allow_market_fallback=False,
            rationale=rationale,
            risk_note=risk_note,
        )
