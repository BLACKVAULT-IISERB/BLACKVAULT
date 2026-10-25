from datetime import datetime, timezone
from uuid import uuid4

def record(state, category, outcome, reason_code=None, *, transaction_id=None,
           customer_id=None, metadata=None, request_id=None):
    event = {"timestamp": datetime.now(timezone.utc).isoformat(),
             "request_id": request_id or str(uuid4()), "transaction_id": transaction_id,
             "customer_id": customer_id, "category": category, "outcome": outcome,
             "reason_code": reason_code, "metadata": metadata or {}}
    with state.lock: state.audit_events.append(event)
    return event

def query(state, *, category=None, customer_id=None):
    with state.lock:
        return [dict(e) for e in state.audit_events
                if (category is None or e["category"] == category)
                and (customer_id is None or e["customer_id"] == customer_id)]
