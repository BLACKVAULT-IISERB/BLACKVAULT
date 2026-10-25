"""Central proposal authorization boundary."""
from uuid import uuid4
from .models import Decision
from .policy import parse_amount, canonical, check_policy
from . import audit

class PermissionGate:
    def __init__(self, state, permits, approvals): self.state, self.permits, self.approvals = state, permits, approvals
    def authorize(self, proposal, approval_id=None):
        request_id = str(uuid4())
        try:
            customer, account_id, payee = proposal.customer_id, proposal.source_account_id, proposal.payee_id
            amount = parse_amount(proposal.amount, proposal.currency)
            if not all(isinstance(x, str) and x for x in (customer, account_id, payee)): raise ValueError("INVALID_REQUEST")
            if not isinstance(proposal.currency, str): raise ValueError("INVALID_REQUEST")
            if proposal.idempotency_key is not None and (not isinstance(proposal.idempotency_key, str) or not proposal.idempotency_key): raise ValueError("INVALID_REQUEST")
        except (AttributeError, ValueError, TypeError) as e:
            code = str(e) if str(e) in {"AMOUNT_INVALID", "CURRENCY_MISMATCH"} else "INVALID_REQUEST"
            audit.record(self.state, "authorization", "DENIED", code, request_id=request_id)
            return Decision("DENIED", reason_code=code, message=code)
        norm = canonical(amount)
        fingerprint = "|".join((customer, account_id, payee, norm, proposal.currency))
        key = proposal.idempotency_key
        with self.state.lock:
            if key:
                prior = self.state.idempotency.get((customer, key))
                if prior:
                    oldfp, txid = prior
                    if oldfp != fingerprint: return Decision("DENIED", txid, "IDEMPOTENCY_CONFLICT", "Idempotency key is bound to different transaction details")
                    tx = self.state.transactions.get(txid)
                    if tx and tx.get("status") == "EXECUTED": return Decision("EXECUTED", txid, message="Already executed")
                    if tx and tx.get("status") == "PENDING_APPROVAL":
                        if not approval_id:
                            return Decision("PENDING_APPROVAL", txid, "APPROVAL_REQUIRED", "Independent approval required", tx.get("approval_id"))
                        if approval_id != tx.get("approval_id"):
                            return Decision("DENIED", txid, "APPROVAL_INVALID", "Approval request does not match this idempotent transaction")
                    if tx and tx.get("status") == "FAILED":
                        return Decision("FAILED", txid, tx.get("reason_code"), tx.get("reason_code", "Transfer failed"))
            a = self.state.accounts.get(account_id)
            if not a or not a.active or a.customer_id != customer:
                reason = "ACCOUNT_ACCESS_DENIED"
            elif proposal.currency != a.currency:
                reason = "CURRENCY_MISMATCH"
            elif payee not in self.state.payees:
                reason = "PAYEE_NOT_APPROVED"
            else:
                pol = self.state.policies.get(customer)
                from datetime import datetime, timezone
                day = datetime.now(timezone.utc).date().isoformat()
                spent = sum((__import__("decimal").Decimal(t["amount"]) for t in self.state.transactions.values() if t.get("customer_id")==customer and t.get("day")==day and t.get("status")=="EXECUTED"), __import__("decimal").Decimal("0"))
                reason = check_policy(pol, payee, amount, spent)
            if reason:
                audit.record(self.state, "authorization", "DENIED", reason, customer_id=customer, metadata={"payee_id":payee,"amount":norm}, request_id=request_id)
                return Decision("DENIED", reason_code=reason, message=reason)
            txid = str(uuid4())
            if approval_id:
                approval = self.state.approvals.get(approval_id)
                if approval:
                    txid = approval["claims"].get("transaction_id", txid)
            claims = {"transaction_id":txid,"customer_id":customer,"source_account_id":account_id,"payee_id":payee,"amount":norm,"currency":proposal.currency}
            if amount > self.state.policies[customer].approval_threshold:
                if not approval_id:
                    aid = self.approvals.request(claims)
                    self.state.transactions[txid] = {**claims,"status":"PENDING_APPROVAL", "approval_id":aid}
                    if key: self.state.idempotency[(customer,key)] = (fingerprint,txid)
                    return Decision("PENDING_APPROVAL",txid,"APPROVAL_REQUIRED","Independent approval required",aid)
                if not self.approvals.verify(approval_id, claims):
                    return Decision("DENIED",txid,"APPROVAL_INVALID","Approval does not match this transaction")
            permit = self.permits.issue(claims)
            self.state.transactions.setdefault(txid,{**claims,"status":"AUTHORIZED"})
            if key: self.state.idempotency[(customer,key)] = (fingerprint,txid)
            audit.record(self.state,"authorization","AUTHORIZED",transaction_id=txid,customer_id=customer,metadata={"payee_id":payee,"amount":norm})
            audit.record(self.state,"permit","ISSUED",transaction_id=txid,customer_id=customer)
            return Decision("AUTHORIZED",txid,message="Transaction authorized",permit=permit)
