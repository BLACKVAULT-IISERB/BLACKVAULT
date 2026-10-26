
from typing import Any


def propose_banking_action(
    action: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Return an action proposal for the application to validate.

    This function deliberately does not execute banking operations.
    """
    allowed_actions = {
        "check_balance",
        "list_transactions",
        "transfer",
    }

    if action not in allowed_actions:
        return {
            "status": "rejected",
            "reason": "Unsupported banking action.",
        }

    if not isinstance(arguments, dict):
        return {
            "status": "rejected",
            "reason": "Arguments must be a dictionary.",
        }

    return {
        "status": "proposal_only",
        "action": action,
        "arguments": arguments,
        "executed": False,
        "requires_authorization": True,
    }
