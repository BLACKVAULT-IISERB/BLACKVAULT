
"""Explicit confirmation flow for proposed banking transfers."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import RLock
from uuid import uuid4

from .agent_adapter import submit_transfer


@dataclass(frozen=True)
class PendingTransfer:
    proposal_id: str
    customer_id: str
    source_account_id: str
    payee_id: str
    amount: str
    currency: str
    idempotency_key: str
    expires_at: datetime


class TransferConfirmationService:
    """Keep proposals pending until explicitly confirmed or cancelled.

    This in-memory implementation is suitable for the prototype and tests.
    Production use would require durable, authenticated, per-user storage.
    """

    def __init__(self, app, ttl_seconds=300):
        self._app = app
        self._ttl = timedelta(seconds=ttl_seconds)
        self._pending = {}
        self._lock = RLock()

    def prepare_transfer(
        self,
        *,
        customer_id,
        source_account_id,
        payee_id,
        amount,
        currency="INR",
        idempotency_key,
    ):
        """Prepare a proposal without executing a transaction."""
        from decimal import Decimal, InvalidOperation

        if not all(
            isinstance(value, str) and value.strip()
            for value in (
                customer_id,
                source_account_id,
                payee_id,
                currency,
                idempotency_key,
            )
        ):
            raise ValueError("Required fields must be non-empty strings.")

        if isinstance(amount, bool):
            raise ValueError("Amount must be positive.")

        try:
            parsed = Decimal(str(amount))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Amount must be positive.") from None

        if not parsed.is_finite() or parsed <= 0:
            raise ValueError("Amount must be positive.")

        proposal_id = str(uuid4())
        expires_at = datetime.now(timezone.utc) + self._ttl

        pending = PendingTransfer(
            proposal_id=proposal_id,
            customer_id=customer_id,
            source_account_id=source_account_id,
            payee_id=payee_id,
            amount=str(parsed),
            currency=currency,
            idempotency_key=idempotency_key,
            expires_at=expires_at,
        )

        with self._lock:
            self._pending[proposal_id] = pending

        return {
            "status": "AWAITING_CONFIRMATION",
            "proposal_id": proposal_id,
            "customer_id": pending.customer_id,
            "source_account_id": pending.source_account_id,
            "payee_id": pending.payee_id,
            "amount": pending.amount,
            "currency": pending.currency,
            "expires_at": expires_at.isoformat(),
        }

    def confirm_transfer(self, proposal_id, *, customer_id):
        """Confirm and submit the exact pending proposal once."""
        with self._lock:
            pending = self._pending.get(proposal_id)

            if pending is None:
                return {"status": "REJECTED", "reason_code": "PROPOSAL_NOT_FOUND"}

            if pending.customer_id != customer_id:
                return {"status": "REJECTED", "reason_code": "CUSTOMER_MISMATCH"}

            if datetime.now(timezone.utc) >= pending.expires_at:
                del self._pending[proposal_id]
                return {"status": "REJECTED", "reason_code": "PROPOSAL_EXPIRED"}

            # Consume before submission to prevent concurrent double confirmation.
            del self._pending[proposal_id]

        return submit_transfer(
            self._app,
            customer_id=pending.customer_id,
            source_account_id=pending.source_account_id,
            payee_id=pending.payee_id,
            amount=pending.amount,
            currency=pending.currency,
            idempotency_key=pending.idempotency_key,
        )

    def cancel_transfer(self, proposal_id, *, customer_id):
        """Cancel a pending proposal without submitting it."""
        with self._lock:
            pending = self._pending.get(proposal_id)

            if pending is None:
                return {"status": "REJECTED", "reason_code": "PROPOSAL_NOT_FOUND"}

            if pending.customer_id != customer_id:
                return {"status": "REJECTED", "reason_code": "CUSTOMER_MISMATCH"}

            del self._pending[proposal_id]

        return {"status": "CANCELLED", "proposal_id": proposal_id}
