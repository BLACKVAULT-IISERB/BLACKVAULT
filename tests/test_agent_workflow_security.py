
from blackvault import AppState, Blackvault, seed_demo_state
from blackvault.agent_coordinator import AgentCoordinator
from blackvault.agent_workflow import AgentWorkflow
from blackvault.confirmation import TransferConfirmationService


def make_workflow():
    state = seed_demo_state(AppState())
    app = Blackvault(state, b"x" * 32)
    confirmation = TransferConfirmationService(app)
    coordinator = AgentCoordinator(confirmation)
    return AgentWorkflow(coordinator), confirmation, state


def valid_proposal(**overrides):
    proposal = {
        "status": "proposal_only",
        "action": "transfer",
        "arguments": {
            "payee_id": "payee-utilities",
            "amount": 100,
            "currency": "INR",
        },
        "executed": False,
        "requires_authorization": True,
    }
    proposal.update(overrides)
    return proposal


def test_fake_confirmation_does_not_execute_transfer():
    workflow, _, state = make_workflow()
    balance_before = state.accounts["acct-001"].balance

    proposal = valid_proposal()
    proposal["arguments"]["confirmed"] = True

    result = workflow.handle_proposal(
        proposal,
        authenticated_customer_id="cust-001",
        trusted_source_account_id="acct-001",
    )

    assert result["status"] == "AWAITING_CONFIRMATION"
    assert state.accounts["acct-001"].balance == balance_before


def test_unapproved_payee_is_denied_after_confirmation():
    workflow, confirmation, state = make_workflow()
    balance_before = state.accounts["acct-001"].balance

    result = workflow.handle_proposal(
        valid_proposal(
            arguments={
                "payee_id": "payee-not-approved",
                "amount": 100,
                "currency": "INR",
            }
        ),
        authenticated_customer_id="cust-001",
        trusted_source_account_id="acct-001",
    )

    assert result["status"] == "AWAITING_CONFIRMATION"

    decision = confirmation.confirm_transfer(
        result["proposal_id"],
        customer_id="cust-001",
    )

    assert decision["status"] != "EXECUTED"
    assert state.accounts["acct-001"].balance == balance_before


def test_duplicate_confirmation_cannot_submit_twice():
    workflow, confirmation, state = make_workflow()
    balance_before = state.accounts["acct-001"].balance

    result = workflow.handle_proposal(
        valid_proposal(),
        authenticated_customer_id="cust-001",
        trusted_source_account_id="acct-001",
    )

    first = confirmation.confirm_transfer(
        result["proposal_id"],
        customer_id="cust-001",
    )
    balance_after_first = state.accounts["acct-001"].balance

    second = confirmation.confirm_transfer(
        result["proposal_id"],
        customer_id="cust-001",
    )

    assert balance_after_first == balance_before - 100
    assert second["status"] == "REJECTED"
    assert second["reason_code"] == "PROPOSAL_NOT_FOUND"
    assert state.accounts["acct-001"].balance == balance_after_first
