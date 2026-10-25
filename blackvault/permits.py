import hashlib, hmac, json, secrets
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from .models import Permit

def _canonical(claims):
    return json.dumps(claims, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()

class PermitManager:
    def __init__(self, state, key: bytes, ttl_seconds=60):
        if not isinstance(key, bytes) or len(key) < 32: raise ValueError("signing key must be >=32 bytes")
        self.state, self.key, self.ttl_seconds = state, key, ttl_seconds
    def issue(self, transaction):
        now = datetime.now(timezone.utc)
        claims = {**transaction, "permit_id": secrets.token_urlsafe(24),
                  "issued_at": now.isoformat(), "expires_at": (now+timedelta(seconds=self.ttl_seconds)).isoformat(),
                  "nonce": secrets.token_urlsafe(24)}
        sig = hmac.new(self.key, _canonical(claims), hashlib.sha256).hexdigest()
        permit = Permit(claims, sig)
        with self.state.lock: self.state.permits[claims["permit_id"]] = {"consumed": False}
        return permit
    def verify(self, permit: Permit, expected: dict, *, now=None):
        if not isinstance(permit, Permit): return "PERMIT_INVALID"
        try:
            claims = permit.claims
            if not isinstance(claims, dict) or not hmac.compare_digest(
                    hmac.new(self.key, _canonical(claims), hashlib.sha256).hexdigest(), permit.signature):
                return "PERMIT_INVALID"
            for k, v in expected.items():
                if claims.get(k) != v: return "PERMIT_INVALID"
            issued = datetime.fromisoformat(claims["issued_at"])
            expiry = datetime.fromisoformat(claims["expires_at"])
            current = now or datetime.now(timezone.utc)
            if issued.tzinfo is None or expiry.tzinfo is None: return "PERMIT_INVALID"
            if issued > current + timedelta(seconds=30): return "PERMIT_INVALID"
            if current >= expiry: return "PERMIT_EXPIRED"
            Decimal(claims["amount"])
            with self.state.lock:
                record = self.state.permits.get(claims.get("permit_id"))
                if record is None: return "PERMIT_INVALID"
                if record["consumed"]: return "PERMIT_ALREADY_USED"
            return None
        except (KeyError, TypeError, ValueError, ArithmeticError): return "PERMIT_INVALID"
