from blackvault.models import Proposal

def test_private_account_access(app):
    assert app.account_info("cust-001","acct-002") is None
    assert app.account_info("cust-001","acct-001")["balance"]=="25000.00"

def test_currency_mismatch(app):
    d=app.propose(Proposal("cust-001","acct-001","payee-utilities","1.00","USD"))
    assert d.reason_code=="CURRENCY_MISMATCH"
