"""Stable integration facade for the local agent and red-team harness."""
from .state import AppState
from .permits import PermitManager
from .approvals import ApprovalService
from .gate import PermissionGate
from .bank import Bank
from . import audit

class Blackvault:
    def __init__(self, state: AppState, signing_key: bytes):
        self.state = state
        self.approvals = ApprovalService(state)
        self.permits = PermitManager(state, signing_key)
        self.gate = PermissionGate(state, self.permits, self.approvals)
        self.bank = Bank(state, self.permits, self.approvals)
    def account_info(self, customer_id, account_id): return self.bank.account_info(customer_id, account_id)
    def propose(self, proposal, approval_id=None):
        decision = self.gate.authorize(proposal, approval_id)
        if decision.status != "AUTHORIZED": return decision
        result = self.bank._execute(decision.permit, approval_id)
        if result != "EXECUTED":
            with self.state.lock:
                tx = self.state.transactions.get(decision.transaction_id)
                if tx:
                    tx["status"] = "FAILED"
                    tx["reason_code"] = result
            audit.record(self.state, "transfer", "FAILED", result, transaction_id=decision.transaction_id)
            return type(decision)("FAILED", decision.transaction_id, result, result)
        return type(decision)("EXECUTED", decision.transaction_id, message="Transfer executed")
    def approve(self, approval_id, approved=True): return self.approvals.decide(approval_id, approved)
    def transaction(self, transaction_id):
        with self.state.lock:
            t = self.state.transactions.get(transaction_id)
            return dict(t) if t else None
    def audit_events(self, **filters): return audit.query(self.state, **filters)
