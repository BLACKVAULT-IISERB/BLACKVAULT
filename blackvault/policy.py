from decimal import Decimal, InvalidOperation
import re
from .models import Policy

def parse_amount(value, currency="INR") -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, Decimal, int)):
        raise ValueError("AMOUNT_INVALID")
    if not isinstance(value, str): value = str(value)
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.[0-9]{1,2})?", value):
        raise ValueError("AMOUNT_INVALID")
    try: amount = Decimal(value)
    except (InvalidOperation, ValueError): raise ValueError("AMOUNT_INVALID") from None
    if not amount.is_finite() or amount <= 0 or amount.as_tuple().exponent < -2:
        raise ValueError("AMOUNT_INVALID")
    if currency != "INR": raise ValueError("CURRENCY_MISMATCH")
    return amount.quantize(Decimal("0.01"))

def canonical(amount: Decimal) -> str: return format(amount, ".2f")

def check_policy(policy: Policy | None, payee_id: str, amount: Decimal, spent: Decimal):
    if policy is None: return "POLICY_MISSING"
    if not policy.active: return "POLICY_INACTIVE"
    if payee_id not in policy.approved_payees: return "PAYEE_NOT_APPROVED"
    if amount > policy.transaction_limit: return "TRANSACTION_LIMIT_EXCEEDED"
    if spent + amount > policy.daily_limit: return "DAILY_LIMIT_EXCEEDED"
    return None
