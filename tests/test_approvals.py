from blackvault.models import Proposal

def test_rejected_approval(app):
    d=app.gate.authorize(Proposal("cust-001","acct-001","payee-utilities","6000.00"))
    assert not app.approve(d.approval_id,False)
    assert app.propose(Proposal("cust-001","acct-001","payee-utilities","6000.00"),d.approval_id).reason_code=="APPROVAL_INVALID"
from datetime import datetime, timedelta, timezone
from blackvault.models import Proposal


def test_approval_expires(app):
    decision = app.gate.authorize(Proposal("cust-001", "acct-001", "payee-utilities", "6000.00"))
    approval = app.state.approvals[decision.approval_id]
    approval["expires_at"] = datetime.now(timezone.utc) - timedelta(seconds=1)
    assert app.approve(decision.approval_id, True) is False
