"""Deterministic local demonstration using fictional data only."""
from dataclasses import replace
from decimal import Decimal
from blackvault import AppState, seed_demo_state, Proposal, Blackvault
from blackvault.config import signing_key_from_env

def run():
    state=seed_demo_state(AppState())
    app=Blackvault(state,signing_key_from_env())
    def show(label, **kwargs):
        result=app.propose(Proposal("cust-001","acct-001",kwargs.pop("payee_id","payee-utilities"),kwargs.pop("amount","100.00"),"INR",kwargs.pop("idempotency_key",None)))
        print(f"{label}: {result.status} {result.reason_code or ''} {result.message}; balance={state.accounts['acct-001'].balance}")
        return result
    print("BLACKVAULT synthetic banking demo (fictional balances)")
    show("Approved utility payment",idempotency_key="demo-1")
    show("Unapproved payee",payee_id="payee-friend")
    show("Above transaction limit",amount="12000.00")
    pending=app.gate.authorize(Proposal("cust-001","acct-001","payee-utilities","6000.00","INR","demo-big"))
    print("High value payment:",pending.status,pending.reason_code)
    app.approve(pending.approval_id,True)
    done=app.propose(Proposal("cust-001","acct-001","payee-utilities","6000.00","INR","demo-big"),pending.approval_id)
    print("After independent approval:",done.status, "balance=",state.accounts["acct-001"].balance)
    d=app.gate.authorize(Proposal("cust-001","acct-001","payee-utilities","50.00"))
    from dataclasses import replace
    forged=replace(d.permit,signature="0"*64)
    print("Forged permit:",app.bank._execute(forged))
    print("One-use permit first/replay:",app.bank._execute(d.permit),app.bank._execute(d.permit))
    policy=state.policies["cust-001"]
    state.policies["cust-001"]=replace(policy,transaction_limit=Decimal("50000.00"), daily_limit=Decimal("100000.00"), approval_threshold=Decimal("50000.00"))
    show("Insufficient balance",amount="30000.00")
    show("Prompt injection proposes unapproved transfer",payee_id="payee-friend",amount="250.00")

if __name__=="__main__": run()
