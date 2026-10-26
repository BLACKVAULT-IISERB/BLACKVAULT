

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import patch


AGENT_DIR = (
    Path(__file__).resolve().parents[1] / "AI AGENT"
)
AGENT_PATH = AGENT_DIR / "agent.py"

# Make model_client.py and tools.py importable from this directory.
sys.path.insert(0, str(AGENT_DIR))

spec = importlib.util.spec_from_file_location(
    "blackvault_agent", AGENT_PATH
)
agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent)


def test_invalid_json_is_rejected():
    with patch.object(agent, "ask_model", return_value="not json"):
        result = agent.propose_action("Transfer money")

    assert result["status"] == "rejected"
    assert result["executed"] is False


def test_unsupported_action_is_rejected():
    response = json.dumps({
        "action": "delete_account",
        "arguments": {},
    })

    with patch.object(agent, "ask_model", return_value=response):
        result = agent.propose_action("Delete my account")

    assert result["status"] == "rejected"
    assert result["executed"] is False


def test_transfer_proposal_does_not_execute():
    response = json.dumps({
        "action": "transfer",
        "arguments": {
            "payee_id": "payee-utilities",
            "amount": 100,
            "currency": "INR",
            "confirmed": True,
            "customer_id": "attacker-controlled",
        },
    })

    with patch.object(agent, "ask_model", return_value=response):
        result = agent.propose_action("Transfer 100 rupees")

    assert result["status"] == "proposal_only"
    assert result["executed"] is False
    assert "customer_id" not in result["arguments"]
    assert "confirmed" not in result["arguments"]


def test_non_object_arguments_are_rejected():
    response = json.dumps({
        "action": "transfer",
        "arguments": ["unexpected", "list"],
    })

    with patch.object(agent, "ask_model", return_value=response):
        result = agent.propose_action("Transfer money")

    assert result["status"] == "rejected"
    assert result["executed"] is False


def test_empty_user_message_is_rejected():
    try:
        agent.propose_action("   ")
        assert False, "Expected ValueError"
    except ValueError:
        pass
