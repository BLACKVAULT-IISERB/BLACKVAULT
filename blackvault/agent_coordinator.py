
"""Application-level coordinator for AI-proposed banking transfers."""

from uuid import uuid4

from .confirmation import TransferConfirmationService


class AgentCoordinator:
    """Coordinate transfer proposals, confirmation, and backend submission.

    Customer identity and account context must come from trusted
    application authentication, never from model-generated claims.
    """

    def __init__(self, confirmation_service: TransferConfirmationService):
        self._confirmation = confirmation_service

    def prepare_transfer(
        self,
        *,
        authenticated_customer_id: str,
        trusted_source_account_id: str,
        payee_id: str,
        amount,
        currency: str = "INR",
    ) -> dict:
        """Prepare a transfer for review without executing it."""
        return self._confirmation.prepare_transfer(
            customer_id=authenticated_customer_id,
            source_account_id=trusted_source_account_id,
            payee_id=payee_id,
            amount=amount,
            currency=currency,
            idempotency_key=str(uuid4()),
        )

    def confirm_transfer(
        self,
        proposal_id: str,
        *,
        authenticated_customer_id: str,
    ) -> dict:
        """Submit a pending proposal after explicit user confirmation."""
        return self._confirmation.confirm_transfer(
            proposal_id,
            customer_id=authenticated_customer_id,
        )

    def cancel_transfer(
        self,
        proposal_id: str,
        *,
        authenticated_customer_id: str,
    ) -> dict:
        """Cancel a pending proposal."""
        return self._confirmation.cancel_transfer(
            proposal_id,
            customer_id=authenticated_customer_id,
        )
