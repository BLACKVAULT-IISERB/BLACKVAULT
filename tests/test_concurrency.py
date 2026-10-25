from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from decimal import Decimal
from blackvault.models import Proposal


def test_concurrent_transfers_do_not_overspend(app, state):
    policy = state.policies["cust-001"]
    state.policies["cust-001"] = replace(policy, approval_threshold=policy.daily_limit)

    def send(i):
        return app.propose(Proposal("cust-001", "acct-001", "payee-utilities", "9000.00", "INR", f"parallel-{i}"))

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(send, range(8)))
    assert sum(result.status == "EXECUTED" for result in results) == 1
    assert state.accounts["acct-001"].balance == Decimal("16000.00")
    assert state.payee_balances["payee-utilities"] == Decimal("9000.00")
