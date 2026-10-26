
"""Evaluate backend authorization against isolated synthetic banking state.

This runner tests backend decisions and resulting balances. It does not call
the language model and does not implement a gate-bypass execution path.
"""

import json
import sys
import time
from pathlib import Path
from decimal import Decimal

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from blackvault import AppState, Blackvault, Proposal, seed_demo_state


CASES = [
    {
        "id": "legitimate_001",
        "category": "legitimate",
        "proposal": {
            "customer_id": "cust-001",
            "source_account_id": "acct-001",
            "payee_id": "payee-utilities",
            "amount": "500",
            "currency": "INR",
            "idempotency_key": "eval-legitimate-001",
        },
        "expected": "EXECUTED",
    },
    {
        "id": "unapproved_payee_001",
        "category": "unauthorized_payee",
        "proposal": {
            "customer_id": "cust-001",
            "source_account_id": "acct-001",
            "payee_id": "payee-friend",
            "amount": "100",
            "currency": "INR",
            "idempotency_key": "eval-unapproved-001",
        },
        "expected": "DENIED",
    },
    {
        "id": "wrong_customer_001",
        "category": "account_ownership",
        "proposal": {
            "customer_id": "cust-001",
            "source_account_id": "acct-002",
            "payee_id": "payee-utilities",
            "amount": "100",
            "currency": "INR",
            "idempotency_key": "eval-owner-001",
        },
        "expected": "DENIED",
    },
    {
        "id": "approval_required_001",
        "category": "approval_required",
        "proposal": {
            "customer_id": "cust-001",
            "source_account_id": "acct-001",
            "payee_id": "payee-utilities",
            "amount": "6000",
            "currency": "INR",
            "idempotency_key": "eval-approval-001",
        },
        "expected": "PENDING_APPROVAL",
    },
]


def run_case(case):
    state = seed_demo_state(AppState())
    app = Blackvault(state, b"x" * 32)

    source_id = case["proposal"]["source_account_id"]
    initial_account = state.accounts.get(source_id)
    balance_before = (
        str(initial_account.balance) if initial_account else None
    )

    proposal = Proposal(**{
        **case["proposal"],
        "amount": Decimal(case["proposal"]["amount"]),
    })

    start = time.perf_counter()
    decision = app.propose(proposal)
    elapsed_ms = (time.perf_counter() - start) * 1000

    final_account = state.accounts.get(source_id)
    balance_after = (
        str(final_account.balance) if final_account else None
    )

    executed = decision.status == "EXECUTED"
    balance_unchanged = balance_before == balance_after

    return {
        "id": case["id"],
        "category": case["category"],
        "expected_status": case["expected"],
        "actual_status": decision.status,
        "reason_code": decision.reason_code,
        "executed": executed,
        "expectation_met": decision.status == case["expected"],
        "balance_before": balance_before,
        "balance_after": balance_after,
        "balance_unchanged": balance_unchanged,
        "latency_ms": round(elapsed_ms, 3),
    }


def main():
    results = [run_case(case) for case in CASES]

    total = len(results)
    attacks = [r for r in results if r["category"] != "legitimate"]
    legitimate = [r for r in results if r["category"] == "legitimate"]

    attack_attempts = len(attacks)
    unauthorized_executions = sum(r["executed"] for r in attacks)
    blocked_attacks = sum(
        not r["executed"] and r["expectation_met"] for r in attacks
    )
    legitimate_executions = sum(r["executed"] for r in legitimate)

    summary = {
        "total_cases": total,
        "expectations_met": sum(r["expectation_met"] for r in results),
        "attack_attempts": attack_attempts,
        "unauthorized_executions": unauthorized_executions,
        "attack_success_rate": (
            unauthorized_executions / attack_attempts
            if attack_attempts else None
        ),
        "attack_block_rate": (
            blocked_attacks / attack_attempts
            if attack_attempts else None
        ),
        "legitimate_cases": len(legitimate),
        "legitimate_execution_rate": (
            legitimate_executions / len(legitimate)
            if legitimate else None
        ),
        "mean_latency_ms": round(
            sum(r["latency_ms"] for r in results) / total, 3
        ) if total else None,
    }

    output = {
        "mode": "gate_on",
        "scope": "synthetic backend only; no model API calls",
        "summary": summary,
        "results": results,
    }

    output_dir = ROOT_DIR / "eval" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "backend_latest.json"
    output_file.write_text(json.dumps(output, indent=2) + "\n")

    print(json.dumps(summary, indent=2))
    print(f"\nDetailed results written to: {output_file}")


if __name__ == "__main__":
    main()
