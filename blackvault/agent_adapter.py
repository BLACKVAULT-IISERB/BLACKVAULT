
"""Validated adapter from agent proposals to the BLACKVAULT backend."""

from decimal import Decimal, InvalidOperation
from typing import Any

from .models import Proposal
from .service import Blackvault


def submit_transfer(
    app: Blackvault,
    *,
    customer_id: str,
    source_account_id: str,
    payee_id: str,
    amount: Any,
    currency: str = "INR",
    idempotency_key: str,
) -> dict[str, Any]:
    """Submit a transfer proposal through the existing authorization gate.

    Customer identity and source account must come from trusted application
    context, not from the model's claims or the user's prompt.
    """
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
        return {
            "status": "REJECTED",
            "reason_code": "INVALID_REQUEST",
            "message": "Required fields must be non-empty strings.",
        }

    if isinstance(amount, bool):
        return {
            "status": "REJECTED",
            "reason_code": "AMOUNT_INVALID",
            "message": "Amount must be a valid positive number.",
        }

    try:
        parsed_amount = Decimal(str(amount))
    except (InvalidOperation, ValueError, TypeError):
        return {
            "status": "REJECTED",
            "reason_code": "AMOUNT_INVALID",
            "message": "Amount must be a valid positive number.",
        }

    if not parsed_amount.is_finite() or parsed_amount <= 0:
        return {
            "status": "REJECTED",
            "reason_code": "AMOUNT_INVALID",
            "message": "Amount must be a valid positive number.",
        }

    proposal = Proposal(
        customer_id=customer_id,
        source_account_id=source_account_id,
        payee_id=payee_id,
        amount=parsed_amount,
        currency=currency,
        idempotency_key=idempotency_key,
    )

    decision = app.propose(proposal)
    return decision.as_dict()
