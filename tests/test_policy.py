from blackvault.models import Proposal, Policy
from decimal import Decimal

def test_policy_missing_and_inactive(app,state):
    del state.policies["cust-001"]
    assert app.propose(Proposal("cust-001","acct-001","payee-utilities","1.00")).reason_code=="POLICY_MISSING"
    state.policies["cust-001"]=Policy("cust-001",frozenset({"payee-utilities"}),Decimal("100"),Decimal("200"),Decimal("100"),False)
    assert app.propose(Proposal("cust-001","acct-001","payee-utilities","1.00")).reason_code=="POLICY_INACTIVE"
