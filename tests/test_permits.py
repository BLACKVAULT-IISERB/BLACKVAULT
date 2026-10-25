from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
from blackvault.models import Proposal

KEY = b"x" * 32
FIELDS = ("transaction_id", "customer_id", "source_account_id", "payee_id", "amount", "currency")


def test_missing_permit_is_rejected(app):
    assert app.bank._execute(None) == "PERMIT_INVALID"


def test_expired_permit_is_rejected(app):
    decision = app.gate.authorize(Proposal("cust-001", "acct-001", "payee-utilities", "1.00"))
    expected = {key: decision.permit.claims[key] for key in FIELDS}
    now = datetime.now(timezone.utc) + timedelta(minutes=2)
    assert app.permits.verify(decision.permit, expected, now=now) == "PERMIT_EXPIRED"


def test_permit_claim_tampering_and_future_issue_are_rejected(app):
    decision = app.gate.authorize(Proposal("cust-001", "acct-001", "payee-utilities", "10.00"))
    claims = dict(decision.permit.claims)
    claims["amount"] = "9000.00"
    tampered = replace(decision.permit, claims=claims)
    assert app.bank._execute(tampered) == "PERMIT_INVALID"

    future = dict(decision.permit.claims)
    future["issued_at"] = (datetime.now(timezone.utc) + timedelta(minutes=2)).isoformat()
    encoded = json.dumps(future, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    signature = hmac.new(KEY, encoded, hashlib.sha256).hexdigest()
    assert app.permits.verify(replace(decision.permit, claims=future, signature=signature),
                              {key: future[key] for key in FIELDS}) == "PERMIT_INVALID"
