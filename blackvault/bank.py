from decimal import Decimal
from . import audit

class Bank:
    def __init__(self, state, permit_manager, approval_service):
        self.state, self.permits, self.approvals = state, permit_manager, approval_service
    def account_info(self, customer_id, account_id):
        with self.state.lock:
            a = self.state.accounts.get(account_id)
            if not a or not a.active or a.customer_id != customer_id: return None
            return {"account_id": a.account_id, "currency": a.currency, "balance": format(a.balance, ".2f")}
    def _execute(self, permit, approval_id=None):
        claims = permit.claims if hasattr(permit, "claims") else {}
        expected = {k: claims.get(k) for k in ("transaction_id", "customer_id", "source_account_id", "payee_id", "amount", "currency")}
        with self.state.lock:
            err = self.permits.verify(permit, expected)
            if err: audit.record(self.state, "permit_verification", "DENIED", err, transaction_id=expected.get("transaction_id")); return err
            txid = expected["transaction_id"]
            if txid in self.state.transactions and self.state.transactions[txid]["status"] == "EXECUTED": return "EXECUTED"
            stored = self.state.transactions.get(txid)
            if not stored or any(stored.get(k) != v for k, v in expected.items()): return "PERMIT_INVALID"
            a = self.state.accounts.get(expected["source_account_id"])
            if not a or not a.active or a.customer_id != expected["customer_id"]: return "ACCOUNT_ACCESS_DENIED"
            amount = Decimal(expected["amount"]); policy = self.state.policies.get(a.customer_id)
            day = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).date().isoformat()
            spent = sum((Decimal(t["amount"]) for t in self.state.transactions.values() if t.get("customer_id")==a.customer_id and t.get("day")==day and t.get("status")=="EXECUTED"), Decimal("0"))
            if not policy: return "POLICY_MISSING"
            if not policy.active: return "POLICY_INACTIVE"
            if expected["payee_id"] not in policy.approved_payees: return "PAYEE_NOT_APPROVED"
            if spent + amount > policy.daily_limit: return "DAILY_LIMIT_EXCEEDED"
            if amount > policy.transaction_limit: return "TRANSACTION_LIMIT_EXCEEDED"
            approval = None
            if amount > policy.approval_threshold:
                approval = self.state.approvals.get(approval_id)
                approval_claims = {k: claims[k] for k in ("transaction_id", "customer_id", "source_account_id", "payee_id", "amount", "currency")}
                if not approval or not self.approvals.verify(approval_id, approval_claims): return "APPROVAL_INVALID"
            if expected["payee_id"] not in self.state.payees: return "PAYEE_NOT_APPROVED"
            if a.currency != expected["currency"]: return "CURRENCY_MISMATCH"
            if a.balance < amount: return "INSUFFICIENT_FUNDS"
            # All validations are complete; single lock makes the commit atomic.
            b = self.state.accounts[expected["source_account_id"]]
            from dataclasses import replace
            self.state.accounts[b.account_id] = replace(b, balance=b.balance-amount)
            self.state.payee_balances[expected["payee_id"]] = self.state.payee_balances.get(expected["payee_id"], Decimal("0.00")) + amount
            self.state.transactions[txid] = {**expected, "status":"EXECUTED", "day":day}
            self.state.permits[claims["permit_id"]]["consumed"] = True
            if approval: approval["consumed"] = True
            audit.record(self.state, "transfer", "EXECUTED", transaction_id=txid, customer_id=a.customer_id, metadata={"amount":expected["amount"], "currency":expected["currency"], "payee_id":expected["payee_id"]})
            return "EXECUTED"
