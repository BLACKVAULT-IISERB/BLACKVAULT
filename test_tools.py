
import sys
from pathlib import Path

import pytest

AGENT_DIR = Path(__file__).parent / "AI AGENT"
sys.path.insert(0, str(AGENT_DIR))

from tools import propose_banking_action


def test_transfer_is_only_a_proposal():
    result = propose_banking_action(
        "transfer",
        {"amount": 500, "payee": "test-payee"},
    )

    assert result["status"] == "proposal_only"
    assert result["executed"] is False
    assert result["requires_authorization"] is True


def test_unsupported_action_is_rejected():
    result = propose_banking_action(
        "delete_bank_database",
        {},
    )

    assert result["status"] == "rejected"


def test_invalid_arguments_are_rejected():
    result = propose_banking_action(
        "transfer",
        ["not", "a", "dictionary"],
    )

    assert result["status"] == "rejected"


@pytest.mark.parametrize(
    "action",
    ["check_balance", "list_transactions", "transfer"],
)
def test_supported_actions_never_execute_directly(action):
    result = propose_banking_action(action, {})

    assert result["status"] == "proposal_only"
    assert result["executed"] is False
    assert result["requires_authorization"] is True
