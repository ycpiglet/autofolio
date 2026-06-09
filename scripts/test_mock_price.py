from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.brokers.mock.mock_client import MockBrokerClient


if __name__ == "__main__":
    broker = MockBrokerClient()
    for symbol in ["005930", "069500", "360750"]:
        quote = broker.get_current_price(symbol)
        print(symbol, quote.price)
