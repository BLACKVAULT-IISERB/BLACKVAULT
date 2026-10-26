
from decimal import Decimal

from blackvault import seed_demo_state, AppState, Blackvault
from blackvault.agent_adapter import submit_transfer


def make_app():
    state = seed_demo_state(AppState())
    return Blackvault(state, b"x" * 32), state


def test_approved_payee_transfer_executes():
    app, state = make_app()

    result = submit_transfer(
        app,
        customer_id="cust-001",
        source_account_id="acct-001",
        payee_id="payee-utilities",
        amount="100",
        idempotency_key="adapter-test-001",
    )

    assert result["status"] == "EXECUTED"
    assert state.accounts["acct-001"].balance == Decimal("24900.00")
    assert state.payee_balances["payee-utilities"] == Decimal("100.00")


def test_unapproved_payee_is_rejected():
    app, state = make_app()

    result = submit_transfer(
        app,
        customer_id="cust-001",
        source_account_id="acct-001",
        payee_id="payee-friend",
        amount="100",
        idempotency_key="adapter-test-002",
    )

    assert result["status"] == "DENIED"
    assert result["reason_code"] == "PAYEE_NOT_APPROVED"
    assert state.accounts["acct-001"].balance == Decimal("25000.00")


def test_invalid_amount_is_rejected_before_submission():
    app, state = make_app()

    result = submit_transfer(
        app,
        customer_id="cust-001",
        source_account_id="acct-001",
        payee_id="payee-utilities",
        amount="NaN",
        idempotency_key="adapter-test-003",
    )

    assert result["status"] == "REJECTED"
    assert result["reason_code"] == "AMOUNT_INVALID"
    assert state.accounts["acct-001"].balance == Decimal("25000.00")


def test_customer_cannot_claim_another_customers_account():
    app, state = make_app()

    result = submit_transfer(
        app,
        customer_id="cust-001",
        source_account_id="acct-002",
        payee_id="payee-utilities",
        amount="100",
        idempotency_key="adapter-test-004",
    )

    assert result["status"] == "DENIED"
    assert result["reason_code"] == "ACCOUNT_ACCESS_DENIED"
    assert state.accounts["acct-002"].balance == Decimal("8000.00")


def test_large_transfer_requires_approval():
    app, state = make_app()

    result = submit_transfer(
        app,
        customer_id="cust-001",
        source_account_id="acct-001",
        payee_id="payee-utilities",
        amount="6000",
        idempotency_key="adapter-approval-001",
    )

    assert result["status"] == "PENDING_APPROVAL"
    assert state.accounts["acct-001"].balance == Decimal("25000.00")


def test_repeated_request_does_not_transfer_twice():
    app, state = make_app()

    kwargs = {
        "customer_id": "cust-001",
        "source_account_id": "acct-001",
        "payee_id": "payee-utilities",
        "amount": "100",
        "idempotency_key": "adapter-idempotency-001",
    }

    first = submit_transfer(app, **kwargs)
    balance_after_first = state.accounts["acct-001"].balance

    second = submit_transfer(app, **kwargs)

    assert first["status"] == "EXECUTED"
    assert second["status"] == "EXECUTED"
    assert state.accounts["acct-001"].balance == balance_after_first
    assert state.accounts["acct-001"].balance == Decimal("24900.00")
