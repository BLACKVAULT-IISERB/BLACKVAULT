from datetime import datetime, timedelta, timezone
from uuid import uuid4
from . import audit

class ApprovalService:
    """Simulated trusted-human callback; not identity verification."""
    def __init__(self, state, ttl_seconds=300): self.state, self.ttl_seconds = state, ttl_seconds
    def request(self, claims):
        aid = str(uuid4()); a = {"claims": dict(claims), "expires_at": datetime.now(timezone.utc)+timedelta(seconds=self.ttl_seconds), "decision": None, "consumed": False}
        with self.state.lock: self.state.approvals[aid] = a
        audit.record(self.state, "approval_request", "PENDING", transaction_id=claims["transaction_id"], customer_id=claims["customer_id"])
        return aid
    def decide(self, approval_id, approved: bool):
        with self.state.lock:
            a = self.state.approvals.get(approval_id)
            if not a or a["decision"] is not None or datetime.now(timezone.utc) >= a["expires_at"]: return False
            a["decision"] = "APPROVED" if approved else "REJECTED"
        audit.record(self.state, "approval_decision", a["decision"], transaction_id=a["claims"]["transaction_id"], customer_id=a["claims"]["customer_id"])
        return approved
    def verify(self, approval_id, claims):
        with self.state.lock:
            a = self.state.approvals.get(approval_id)
            if not a or a["decision"] != "APPROVED" or a["consumed"] or datetime.now(timezone.utc) >= a["expires_at"] or a["claims"] != claims: return False
            return True
