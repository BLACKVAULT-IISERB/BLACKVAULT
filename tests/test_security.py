from dataclasses import replace
from decimal import Decimal
from blackvault.models import Proposal

def proposal(**kw):
    d=dict(customer_id="cust-001",source_account_id="acct-001",payee_id="payee-utilities",amount="100.00",currency="INR")
    d.update(kw); return Proposal(**d)

def test_legitimate_transfer(app, state):
    d=app.propose(proposal()); assert d.status=="EXECUTED"
    assert state.accounts["acct-001"].balance==Decimal("24900.00")
    assert state.payee_balances["payee-utilities"]==Decimal("100.00")

def test_reject_unapproved_and_limit(app):
    assert app.propose(proposal(payee_id="payee-friend")).reason_code=="PAYEE_NOT_APPROVED"
    assert app.propose(proposal(amount="10001.00")).reason_code=="TRANSACTION_LIMIT_EXCEEDED"

def test_approval_required_and_exact_binding(app):
    d=app.gate.authorize(proposal(amount="6000.00")); assert d.status=="PENDING_APPROVAL"
    assert app.approve(d.approval_id)
    changed=app.propose(proposal(amount="6001.00"),d.approval_id)
    assert changed.reason_code=="APPROVAL_INVALID"

def test_approved_flow(app):
    p=proposal(amount="6000.00",idempotency_key="big1")
    d=app.gate.authorize(p); assert app.approve(d.approval_id)
    assert app.propose(p,d.approval_id).status=="EXECUTED"

def test_ownership_and_invalid_amount(app):
    assert app.propose(proposal(customer_id="cust-002")).reason_code=="ACCOUNT_ACCESS_DENIED"
    for value in ("0","-1","100.001","NaN","Infinity","","invalid",True):
        assert app.propose(proposal(amount=value)).reason_code=="AMOUNT_INVALID"

def test_idempotent_retry_and_conflict(app):
    p=proposal(idempotency_key="k1"); first=app.propose(p); second=app.propose(p)
    assert first.status==second.status=="EXECUTED"
    assert app.propose(replace(p,amount="101.00")).reason_code=="IDEMPOTENCY_CONFLICT"

def test_failed_authorization_audited(app):
    app.propose(proposal(payee_id="bad"))
    assert any(x["category"]=="authorization" and x["outcome"]=="DENIED" for x in app.audit_events())

def test_missing_signing_key_fails():
    import pytest
    with pytest.raises(ValueError):
        from blackvault.permits import PermitManager
        PermitManager(None,b"weak")

def test_permit_tamper_and_replay(app, state):
    d=app.gate.authorize(proposal())
    forged=replace(d.permit,signature="0"*64)
    assert app.bank._execute(forged)=="PERMIT_INVALID"
    assert app.bank._execute(d.permit)=="EXECUTED"
    assert app.bank._execute(d.permit)=="PERMIT_ALREADY_USED"
