"""Small state access facade; business authorization remains in services."""
from .state import AppState

class Repository:
    def __init__(self, state: AppState): self.state = state
    def account(self, account_id): return self.state.accounts.get(account_id)
    def policy(self, customer_id): return self.state.policies.get(customer_id)
    def audit_events(self):
        with self.state.lock: return [dict(e) for e in self.state.audit_events]
