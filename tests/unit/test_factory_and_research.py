"""Tests for broker factory and research agent."""
import pytest
from unittest.mock import patch


# ── create_broker_client (app/brokers/factory.py) ────────────────────────────

def test_create_broker_client_mock_env_returns_mock_client():
    from app.brokers.factory import create_broker_client
    from app.brokers.mock.mock_client import MockBrokerClient
    from app.config.settings import settings
    with patch.object(settings.__class__, "kis_env", new="mock"):
        # Reset the module-level settings binding
        import app.brokers.factory as factory_module
        original_env = factory_module.settings.kis_env
        try:
            # Patch at the module level
            with patch("app.brokers.factory.settings") as mock_settings:
                mock_settings.kis_env = "mock"
                client = create_broker_client()
                assert isinstance(client, MockBrokerClient)
        finally:
            pass  # settings is frozen dataclass


def test_create_broker_client_invalid_env_raises():
    import app.brokers.factory as factory_module
    with patch("app.brokers.factory.settings") as mock_settings:
        mock_settings.kis_env = "invalid_env_xyz"
        with pytest.raises(ValueError, match="Unsupported KIS_ENV"):
            factory_module.create_broker_client()


# ── ResearchAgent (app/agents/research_agent.py) ─────────────────────────────

def test_research_agent_propose_buy_condition():
    from app.agents.research_agent import ResearchAgent, ConditionProposal
    agent = ResearchAgent()
    proposal = agent.propose_price_condition(
        symbol="005930", current_price=70000.0, side="BUY", quantity=5
    )
    assert isinstance(proposal, ConditionProposal)
    assert proposal.symbol == "005930"
    assert proposal.side == "BUY"
    assert proposal.target_price == round(70000.0 * 0.99)
    assert proposal.quantity == 5
    assert proposal.order_type == "LIMIT"
    assert proposal.allow_market_fallback is False


def test_research_agent_propose_sell_condition():
    from app.agents.research_agent import ResearchAgent
    agent = ResearchAgent()
    proposal = agent.propose_price_condition(
        symbol="005930", current_price=70000.0, side="SELL", quantity=3
    )
    assert proposal.side == "SELL"
    assert proposal.target_price == round(70000.0 * 1.03)


def test_research_agent_propose_lowercase_side():
    from app.agents.research_agent import ResearchAgent
    agent = ResearchAgent()
    proposal = agent.propose_price_condition(
        symbol="069500", current_price=35000.0, side="buy"
    )
    assert proposal.side == "BUY"


def test_research_agent_invalid_side_raises():
    from app.agents.research_agent import ResearchAgent
    agent = ResearchAgent()
    with pytest.raises(ValueError, match="side must be BUY or SELL"):
        agent.propose_price_condition(symbol="005930", current_price=70000.0, side="HOLD")


def test_condition_proposal_is_frozen():
    from app.agents.research_agent import ConditionProposal
    p = ConditionProposal(
        symbol="005930",
        side="BUY",
        target_price=69300.0,
        quantity=5,
        order_type="LIMIT",
        allow_market_fallback=False,
        rationale="test",
        risk_note="test risk",
    )
    with pytest.raises((AttributeError, TypeError)):
        p.symbol = "000000"  # type: ignore
