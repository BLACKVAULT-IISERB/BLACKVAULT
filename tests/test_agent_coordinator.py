
from blackvault import AppState, Blackvault, seed_demo_state
from blackvault.agent_coordinator import AgentCoordinator
from blackvault.confirmation import TransferConfirmationService


def make_coordinator():
    state = seed_demo_state(AppState())
    app = Blackvault(state, b"x" * 32)
    confirmation = TransferConfirmationService(app)
    return AgentCoordinator(confirmation), state


def test_preparation_does_not_execute_transfer():
    coordinator, state = make_coordinator()
    original_balance = state.accounts["acct-001"].balance

    proposal = coordinator.prepare_transfer(
        authenticated_customer_id="cust-001",
        trusted_source_account_id="acct-001",
        payee_id="payee-utilities",
        amount=100,
    )

    assert proposal["status"] == "AWAITING_CONFIRMATION"
    assert state.accounts["acct-001"].balance == original_balance


def test_confirmation_submits_transfer_to_backend():
    coordinator, state = make_coordinator()
    original_balance = state.accounts["acct-001"].balance

    proposal = coordinator.prepare_transfer(
        authenticated_customer_id="cust-001",
        trusted_source_account_id="acct-001",
        payee_id="payee-utilities",
        amount=100,
    )

    result = coordinator.confirm_transfer(
        proposal["proposal_id"],
        authenticated_customer_id="cust-001",
    )

    assert state.accounts["acct-001"].balance == original_balance - 100
    assert result["status"] not in {"AWAITING_CONFIRMATION", "CANCELLED"}


def test_wrong_customer_cannot_confirm_transfer():
    coordinator, state = make_coordinator()
    original_balance = state.accounts["acct-001"].balance

    proposal = coordinator.prepare_transfer(
        authenticated_customer_id="cust-001",
        trusted_source_account_id="acct-001",
        payee_id="payee-utilities",
        amount=100,
    )

    result = coordinator.confirm_transfer(
        proposal["proposal_id"],
        authenticated_customer_id="cust-002",
    )

    assert result["status"] == "REJECTED"
    assert result["reason_code"] == "CUSTOMER_MISMATCH"
    assert state.accounts["acct-001"].balance == original_balance


def test_cancellation_prevents_transfer():
    coordinator, state = make_coordinator()
    original_balance = state.accounts["acct-001"].balance

    proposal = coordinator.prepare_transfer(
        authenticated_customer_id="cust-001",
        trusted_source_account_id="acct-001",
        payee_id="payee-utilities",
        amount=100,
    )

    result = coordinator.cancel_transfer(
        proposal["proposal_id"],
        authenticated_customer_id="cust-001",
    )

    assert result["status"] == "CANCELLED"
    assert state.accounts["acct-001"].balance == original_balance
