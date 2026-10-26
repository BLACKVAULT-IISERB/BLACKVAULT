
from typing import Any


ALLOWED_ACTIONS = {
    "check_balance",
    "list_transactions",
    "transfer",
}


def propose_banking_action(
    action: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Create a proposal for the application to validate.

    This function never executes banking operations and never
    authorizes a transaction. Validation and authorization are
    handled separately by the application and backend.
    """
    if action not in ALLOWED_ACTIONS:
        return {
            "status": "rejected",
            "reason": "Unsupported banking action.",
            "executed": False,
        }

    if not isinstance(arguments, dict):
        return {
            "status": "rejected",
            "reason": "Arguments must be a dictionary.",
            "executed": False,
        }

    return {
        "status": "proposal_only",
        "action": action,
        "arguments": arguments,
        "executed": False,
        "requires_authorization": True,
    }
