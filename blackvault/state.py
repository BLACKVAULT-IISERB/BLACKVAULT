from dataclasses import dataclass, field
from decimal import Decimal
from threading import RLock
from typing import Any
from .models import Account, Policy

@dataclass
class AppState:
    customers: set[str] = field(default_factory=set)
    accounts: dict[str, Account] = field(default_factory=dict)
    payees: dict[str, str] = field(default_factory=dict)
    payee_balances: dict[str, Decimal] = field(default_factory=dict)
    policies: dict[str, Policy] = field(default_factory=dict)
    transactions: dict[str, dict[str, Any]] = field(default_factory=dict)
    approvals: dict[str, Any] = field(default_factory=dict)
    permits: dict[str, Any] = field(default_factory=dict)
    idempotency: dict[tuple[str, str], tuple[str, str]] = field(default_factory=dict)
    audit_events: list[dict[str, Any]] = field(default_factory=list)
    lock: RLock = field(default_factory=RLock, repr=False)

def seed_demo_state(state: AppState | None = None) -> AppState:
    """Initialize fictional disposable data; never called implicitly by services."""
    from .models import Account, Policy
    s = state or AppState()
    with s.lock:
        s.customers.update({"cust-001", "cust-002"})
        s.accounts.update({
            "acct-001": Account("acct-001", "cust-001", Decimal("25000.00")),
            "acct-002": Account("acct-002", "cust-002", Decimal("8000.00")),
        })
        s.payees.update({"payee-utilities": "Utilities Co", "payee-rent": "Rent Services",
                         "payee-friend": "Asha"})
        s.payee_balances.update({p: Decimal("0.00") for p in s.payees})
        s.policies["cust-001"] = Policy("cust-001", frozenset({"payee-utilities", "payee-rent"}),
                                         Decimal("10000.00"), Decimal("15000.00"), Decimal("5000.00"))
        s.policies["cust-002"] = Policy("cust-002", frozenset({"payee-utilities"}),
                                         Decimal("5000.00"), Decimal("8000.00"), Decimal("3000.00"))
    return s
