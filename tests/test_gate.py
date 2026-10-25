from dataclasses import replace
from decimal import Decimal
from blackvault.models import Proposal


def test_idempotent_pending_approval_returns_same_request(app):
    p = Proposal("cust-001", "acct-001", "payee-utilities", "6000.00", "INR", "pending-key")
    first = app.propose(p)
    again = app.propose(p)
    assert first.status == again.status == "PENDING_APPROVAL"
    assert first.transaction_id == again.transaction_id
    assert first.approval_id == again.approval_id
    assert len(app.state.approvals) == 1


def test_daily_limit_is_rechecked_and_only_success_counts(app, state):
    policy = state.policies["cust-001"]
    state.policies["cust-001"] = replace(policy, approval_threshold=Decimal("10000.00"))
    first = app.propose(Proposal("cust-001", "acct-001", "payee-utilities", "9000.00"))
    second = app.propose(Proposal("cust-001", "acct-001", "payee-utilities", "7000.00"))
    assert first.status == "EXECUTED"
    assert second.reason_code == "DAILY_LIMIT_EXCEEDED"


def test_insufficient_funds_failure_is_stored_and_repeatable(app, state):
    from dataclasses import replace
    policy = state.policies["cust-001"]
    state.policies["cust-001"] = replace(policy, transaction_limit=Decimal("50000"), daily_limit=Decimal("50000"), approval_threshold=Decimal("50000"))
    p = Proposal("cust-001", "acct-001", "payee-utilities", "30000.00", "INR", "poor-key")
    first = app.propose(p)
    again = app.propose(p)
    assert first.status == "FAILED" and first.reason_code == "INSUFFICIENT_FUNDS"
    assert again.status == "FAILED" and again.reason_code == "INSUFFICIENT_FUNDS"
    assert state.accounts["acct-001"].balance == Decimal("25000.00")
    assert app.transaction(first.transaction_id)["status"] == "FAILED"
