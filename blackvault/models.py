from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime
from typing import Any

@dataclass(frozen=True)
class Account:
    account_id: str
    customer_id: str
    balance: Decimal
    currency: str = "INR"
    active: bool = True

@dataclass(frozen=True)
class Policy:
    customer_id: str
    approved_payees: frozenset[str]
    transaction_limit: Decimal
    daily_limit: Decimal
    approval_threshold: Decimal
    active: bool = True

@dataclass(frozen=True)
class Proposal:
    customer_id: str
    source_account_id: str
    payee_id: str
    amount: Any
    currency: str = "INR"
    idempotency_key: str | None = None

@dataclass(frozen=True)
class Permit:
    claims: dict[str, Any]
    signature: str

@dataclass
class Approval:
    approval_id: str
    claims: dict[str, Any]
    expires_at: datetime
    decision: str | None = None
    consumed: bool = False

@dataclass(frozen=True)
class Decision:
    status: str
    transaction_id: str | None = None
    reason_code: str | None = None
    message: str = ""
    approval_id: str | None = None
    permit: Permit | None = field(default=None, repr=False, compare=False)
    def as_dict(self):
        return {"status": self.status, "transaction_id": self.transaction_id,
                "reason_code": self.reason_code, "message": self.message,
                "approval_id": self.approval_id}
