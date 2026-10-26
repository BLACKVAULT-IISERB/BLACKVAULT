
from blackvault import AppState, Blackvault, seed_demo_state
from blackvault.agent_coordinator import AgentCoordinator
from blackvault.agent_workflow import AgentWorkflow
from blackvault.confirmation import TransferConfirmationService


def make_workflow():
    state = seed_demo_state(AppState())
    app = Blackvault(state, b"x" * 32)
    confirmation = TransferConfirmationService(app)
    coordinator = AgentCoordinator(confirmation)
    return AgentWorkflow(coordinator), state


def test_valid_transfer_creates_pending_proposal_only():
    workflow, state = make_workflow()
    original_balance = state.accounts["acct-001"].balance

    result = workflow.handle_proposal(
        {
            "status": "proposal_only",
            "action": "transfer",
            "arguments": {
                "payee_id": "payee-utilities",
                "amount": 100,
                "currency": "INR",
            },
            "executed": False,
            "requires_authorization": True,
        },
        authenticated_customer_id="cust-001",
        trusted_source_account_id="acct-001",
    )

    assert result["status"] == "AWAITING_CONFIRMATION"
    assert result["executed"] is False
    assert state.accounts["acct-001"].balance == original_balance


def test_agent_cannot_claim_execution():
    workflow, _ = make_workflow()

    result = workflow.handle_proposal(
        {
            "status": "proposal_only",
            "action": "transfer",
            "arguments": {
                "payee_id": "payee-utilities",
                "amount": 100,
            },
            "executed": True,
        },
        authenticated_customer_id="cust-001",
        trusted_source_account_id="acct-001",
    )

    assert result["status"] == "rejected"


def test_unsupported_action_does_not_prepare_transfer():
    workflow, state = make_workflow()
    original_balance = state.accounts["acct-001"].balance

    result = workflow.handle_proposal(
        {
            "status": "proposal_only",
            "action": "check_balance",
            "arguments": {},
            "executed": False,
        },
        authenticated_customer_id="cust-001",
        trusted_source_account_id="acct-001",
    )

    assert result["status"] == "unsupported"
    assert state.accounts["acct-001"].balance == original_balance
