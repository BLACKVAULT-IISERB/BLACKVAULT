
"""Connect AI-generated proposals to the trusted application workflow."""

from typing import Any

from .agent_coordinator import AgentCoordinator


class AgentWorkflow:
    """Convert model proposals into pending transfer proposals."""

    def __init__(self, coordinator: AgentCoordinator):
        self._coordinator = coordinator

    def handle_proposal(
        self,
        proposal: dict[str, Any],
        *,
        authenticated_customer_id: str,
        trusted_source_account_id: str,
    ) -> dict[str, Any]:
        """Prepare a transfer for review without executing it."""

        if not isinstance(proposal, dict):
            return {
                "status": "rejected",
                "reason": "Proposal must be an object.",
                "executed": False,
            }

        if proposal.get("status") != "proposal_only":
            return {
                "status": "rejected",
                "reason": "Proposal was not accepted by the agent interface.",
                "executed": False,
            }

        if proposal.get("executed") is not False:
            return {
                "status": "rejected",
                "reason": "Agent proposals cannot execute operations.",
                "executed": False,
            }

        if proposal.get("action") != "transfer":
            return {
                "status": "unsupported",
                "reason": "This workflow currently supports transfers only.",
                "executed": False,
            }

        arguments = proposal.get("arguments")
        if not isinstance(arguments, dict):
            return {
                "status": "rejected",
                "reason": "Transfer arguments must be an object.",
                "executed": False,
            }

        payee_id = arguments.get("payee_id")
        amount = arguments.get("amount")
        currency = arguments.get("currency", "INR")

        if not isinstance(payee_id, str) or not payee_id.strip():
            return {
                "status": "needs_clarification",
                "reason": "A valid payee ID is required.",
                "executed": False,
            }

        try:
            pending = self._coordinator.prepare_transfer(
                authenticated_customer_id=authenticated_customer_id,
                trusted_source_account_id=trusted_source_account_id,
                payee_id=payee_id,
                amount=amount,
                currency=currency,
            )
        except (ValueError, TypeError):
            return {
                "status": "rejected",
                "reason": "Transfer details are invalid.",
                "executed": False,
            }

        return {
            **pending,
            "executed": False,
            "message": (
                "Review the payee, amount, account, and currency. "
                "Explicit confirmation is required before submission."
            ),
        }
