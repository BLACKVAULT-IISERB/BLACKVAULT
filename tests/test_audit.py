from blackvault.models import Proposal

def test_audit_query(app):
    app.propose(Proposal("cust-001","acct-001","payee-friend","1.00"))
    rows=app.audit_events(category="authorization")
    assert rows and rows[-1]["reason_code"]=="PAYEE_NOT_APPROVED"
