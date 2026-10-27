
"""Connect AI-generated proposals to the trusted application workflow."""

from typing import Any

from .agent_coordinator import AgentCoordinator


class AgentWorkflow:
    """Convert model proposals into pending transfer proposals."""

    def __init__(self, coordinator: AgentCoordinator):
        self._coordinator = coordinator

    def _resolve_payee_name(self, recipient: str) -> str | None:
        """Resolve a display name or alias against the trusted payee directory."""
        app = self._coordinator._confirmation._app
        payees = app.state.payees

        normalized = recipient.strip().casefold().rstrip(" .,!?;:")
        if not normalized:
            return None

        matches = []

        for payee_id, display_name in payees.items():
            name = display_name.casefold()
            aliases = {name}

            # Permit natural references such as "utilities" and "rent".
            for suffix in (" co", " services"):
                if name.endswith(suffix):
                    aliases.add(name[:-len(suffix)].strip())

            if normalized in aliases:
                matches.append(payee_id)

        # Do not guess when the name is unknown or ambiguous.
        return matches[0] if len(matches) == 1 else None

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
        payee_name = arguments.get("payee_name")
        amount = arguments.get("amount")
        currency = arguments.get("currency", "INR")

        if payee_id is not None:
            # Preserve explicit IDs, including unknown IDs. The backend
            # must reject nonexistent or unapproved payees at submission.
            if not isinstance(payee_id, str) or not payee_id.strip():
                return {
                    "status": "needs_clarification",
                    "reason": "A valid payee ID is required.",
                    "executed": False,
                }

            payee_id = payee_id.strip()

        elif isinstance(payee_name, str) and payee_name.strip():
            payee_id = self._resolve_payee_name(payee_name)

            if payee_id is None:
                return {
                    "status": "needs_clarification",
                    "reason": (
                        "The recipient could not be uniquely matched "
                        "to a known payee."
                    ),
                    "executed": False,
                }

        else:
            return {
                "status": "needs_clarification",
                "reason": "A recipient name or payee ID is required.",
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
