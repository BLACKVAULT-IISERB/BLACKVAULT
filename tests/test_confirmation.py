
from decimal import Decimal

from blackvault import AppState, Blackvault, seed_demo_state
from blackvault.confirmation import TransferConfirmationService


def make_service():
    state = seed_demo_state(AppState())
    app = Blackvault(state, b"x" * 32)
    return TransferConfirmationService(app), state


def prepare(service, key="confirmation-test-001"):
    return service.prepare_transfer(
        customer_id="cust-001",
        source_account_id="acct-001",
        payee_id="payee-utilities",
        amount="100",
        idempotency_key=key,
    )


def test_preparing_transfer_does_not_change_balance():
    service, state = make_service()

    proposal = prepare(service)

    assert proposal["status"] == "AWAITING_CONFIRMATION"
    assert state.accounts["acct-001"].balance == Decimal("25000.00")


def test_confirming_transfer_executes_through_backend():
    service, state = make_service()
    proposal = prepare(service)

    result = service.confirm_transfer(
        proposal["proposal_id"],
        customer_id="cust-001",
    )

    assert result["status"] == "EXECUTED"
    assert state.accounts["acct-001"].balance == Decimal("24900.00")


def test_cancellation_does_not_execute_transfer():
    service, state = make_service()
    proposal = prepare(service)

    result = service.cancel_transfer(
        proposal["proposal_id"],
        customer_id="cust-001",
    )

    assert result["status"] == "CANCELLED"
    assert state.accounts["acct-001"].balance == Decimal("25000.00")


def test_second_confirmation_cannot_repeat_transfer():
    service, state = make_service()
    proposal = prepare(service)

    first = service.confirm_transfer(
        proposal["proposal_id"],
        customer_id="cust-001",
    )
    second = service.confirm_transfer(
        proposal["proposal_id"],
        customer_id="cust-001",
    )

    assert first["status"] == "EXECUTED"
    assert second["status"] == "REJECTED"
    assert state.accounts["acct-001"].balance == Decimal("24900.00")


def test_wrong_customer_cannot_confirm():
    service, state = make_service()
    proposal = prepare(service)

    result = service.confirm_transfer(
        proposal["proposal_id"],
        customer_id="cust-002",
    )

    assert result["reason_code"] == "CUSTOMER_MISMATCH"
    assert state.accounts["acct-001"].balance == Decimal("25000.00")
