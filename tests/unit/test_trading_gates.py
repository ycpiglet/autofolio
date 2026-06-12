"""Unit tests for app.services.trading.save_condition_with_gates."""
from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from app.services.trading import GateResult, save_condition_with_gates


def test_blocked_disclosure():
    """공시 게이트가 차단 상태이면 blocked_disclosure 를 반환한다."""
    mock_add = Mock()
    with (
        patch(
            "app.ui.backend.disclosure_gate_state",
            return_value={"blocked": True, "reason": "거래정지"},
        ),
        patch("app.ui.backend.add_condition", mock_add),
    ):
        result = save_condition_with_gates("005930", "BUY", 70000.0, 1, False)
    assert result.status == "blocked_disclosure"
    assert "거래정지" in result.message
    mock_add.assert_not_called()


def test_compliance_reject():
    """compliance-officer 가 REJECT 를 반환하면 rejected 를 반환한다."""
    mock_add = Mock()
    with (
        patch(
            "app.ui.backend.disclosure_gate_state",
            return_value={"blocked": False, "reason": ""},
        ),
        patch(
            "app.ui.agents_runtime.ask",
            return_value="REJECT: 위험",
        ),
        patch("app.ui.backend.add_condition", mock_add),
    ):
        result = save_condition_with_gates("005930", "BUY", 70000.0, 1, False)
    assert result.status == "rejected"
    assert "REJECT" in result.message
    mock_add.assert_not_called()


def test_compliance_caution_without_ack():
    """CAUTION 반환 + caution_acknowledged=False → needs_acknowledgement 반환."""
    mock_add = Mock()
    with (
        patch(
            "app.ui.backend.disclosure_gate_state",
            return_value={"blocked": False, "reason": ""},
        ),
        patch(
            "app.ui.agents_runtime.ask",
            return_value="CAUTION: 주의",
        ),
        patch("app.ui.backend.add_condition", mock_add),
    ):
        result = save_condition_with_gates(
            "005930", "BUY", 70000.0, 1, False, caution_acknowledged=False
        )
    assert result.status == "needs_acknowledgement"
    assert "CAUTION" in result.message
    mock_add.assert_not_called()


def test_compliance_caution_with_ack():
    """CAUTION 반환 + caution_acknowledged=True → 저장 진행, saved 반환, compliance='caution_acked'."""
    with (
        patch(
            "app.ui.backend.disclosure_gate_state",
            return_value={"blocked": False, "reason": ""},
        ),
        patch(
            "app.ui.agents_runtime.ask",
            return_value="CAUTION: 주의",
        ),
        patch(
            "app.ui.backend.add_condition",
            return_value=42,
        ),
    ):
        result = save_condition_with_gates(
            "005930", "BUY", 70000.0, 1, False, caution_acknowledged=True
        )
    assert result.status == "saved"
    assert result.condition_id == 42
    assert result.compliance == "caution_acked"


def test_compliance_check_false():
    """compliance_check=False 이면 에이전트 호출 없이 즉시 저장한다."""
    mock_ask = Mock()
    with (
        patch(
            "app.ui.backend.disclosure_gate_state",
            return_value={"blocked": False, "reason": ""},
        ),
        patch("app.ui.agents_runtime.ask", mock_ask),
        patch(
            "app.ui.backend.add_condition",
            return_value=7,
        ),
    ):
        result = save_condition_with_gates(
            "005930", "BUY", 70000.0, 1, False, compliance_check=False
        )
    mock_ask.assert_not_called()
    assert result.status == "saved"
    assert result.condition_id == 7
    assert result.compliance == "skipped"


def test_compliance_pass():
    """compliance-officer 가 REJECT/CAUTION 없이 통과 응답 → saved 반환, compliance='passed'."""
    with (
        patch(
            "app.ui.backend.disclosure_gate_state",
            return_value={"blocked": False, "reason": ""},
        ),
        patch(
            "app.ui.agents_runtime.ask",
            return_value="통과합니다",
        ),
        patch(
            "app.ui.backend.add_condition",
            return_value=1,
        ),
    ):
        result = save_condition_with_gates("005930", "BUY", 70000.0, 1, False)
    assert result.status == "saved"
    assert result.condition_id == 1
    assert result.compliance == "passed"
