from __future__ import annotations

from app.brokers.base import BrokerClient, OrderRequest, OrderResult, Position, PriceQuote
from app.config.settings import Settings, settings
from app.brokers.kis.kis_auth import KisAuth


class KisClient(BrokerClient):
    '''
    한국투자증권 Open API adapter.

    현재 파일은 안전한 스캐폴딩이다.
    실 주문이 바로 나가지 않도록 주문/취소 함수는 명시적으로 구현 전까지
    NotImplementedError를 발생시킨다.

    구현 시 공식 KIS Open API 문서를 기준으로 다음을 채워야 한다.
    - 국내주식 현재가 조회 endpoint / TR ID
    - 국내주식 주문 endpoint / TR ID
    - 국내주식 주문취소 endpoint / TR ID
    - 체결조회 / 잔고조회 endpoint / TR ID
    - 모의투자와 실전 환경 차이
    '''

    def __init__(self, app_settings: Settings = settings):
        self.settings = app_settings
        self.auth = KisAuth(app_settings)

    def get_current_price(self, symbol: str) -> PriceQuote:
        raise NotImplementedError(
            "KIS current price API is not implemented yet. "
            "Implement this using the official KIS Open API docs first."
        )

    def place_order(self, request: OrderRequest) -> OrderResult:
        raise NotImplementedError(
            "KIS order API is intentionally disabled in scaffold. "
            "Implement and verify with paper trading before use."
        )

    def cancel_order(self, broker_order_id: str) -> OrderResult:
        raise NotImplementedError(
            "KIS cancel API is intentionally disabled in scaffold."
        )

    def get_order_status(self, broker_order_id: str) -> OrderResult:
        raise NotImplementedError(
            "KIS order status API is not implemented yet."
        )

    def get_positions(self) -> list[Position]:
        raise NotImplementedError(
            "KIS positions API is not implemented yet."
        )
