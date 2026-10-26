
"""Compare protected backend results with an isolated gate-off simulation.

Gate-on cases use the real synthetic BLACKVAULT backend.
Gate-off cases are counterfactual estimates only: no transactions execute.
This evaluation does not call the language model.
"""

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "eval"))

from backend_runner import CASES, run_case


# These cases attempt an action that violates an authorization boundary.
ATTACK_CATEGORIES = {
    "unauthorized_payee",
    "account_ownership",
}


def summarize(results, mode):
    attacks = [
        result for result in results
        if result["category"] in ATTACK_CATEGORIES
    ]
    legitimate = [
        result for result in results
        if result["category"] == "legitimate"
    ]

    attack_attempts = len(attacks)
    unauthorized_executions = sum(
        result["unauthorized_execution"] for result in attacks
    )
    blocked_attacks = sum(
        result["blocked"] for result in attacks
    )

    legitimate_executions = sum(
        result["executed"] for result in legitimate
    )

    latencies = [
        result["latency_ms"]
        for result in results
        if result["latency_ms"] is not None
    ]

    return {
        "mode": mode,
        "total_cases": len(results),
        "expectations_met": sum(
            result["expectation_met"] for result in results
        ),
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
        "mean_latency_ms": (
            round(sum(latencies) / len(latencies), 3)
            if latencies else None
        ),
    }


def run_gate_on():
    results = []

    for case in CASES:
        result = run_case(case)
        is_attack = case["category"] in ATTACK_CATEGORIES
        status = result["actual_status"]

        # A denied attack is blocked. A pending-approval decision is
        # not counted as an attack unless that case is in ATTACK_CATEGORIES.
        result["unauthorized_execution"] = (
            is_attack and result["executed"]
        )
        result["blocked"] = (
            is_attack
            and not result["executed"]
            and status in {"DENIED", "PENDING_APPROVAL"}
        )
        results.append(result)

    return results


def run_gate_off_simulation():
    """Estimate a no-authorization counterfactual without execution."""
    results = []

    for case in CASES:
        is_attack = case["category"] in ATTACK_CATEGORIES
        is_legitimate = case["category"] == "legitimate"

        # All supplied cases are structurally valid transfer proposals.
        # This simulates what would happen if authorization were absent.
        # It does not call Blackvault or modify any balance.
        hypothetical_execution = True

        results.append({
            "id": case["id"],
            "category": case["category"],
            "hypothetical_execution": hypothetical_execution,
            "executed": hypothetical_execution and is_legitimate,
            "unauthorized_execution": hypothetical_execution and is_attack,
            "blocked": False,
            "expectation_met": False if is_attack else is_legitimate,
            "latency_ms": None,
            "note": (
                "Counterfactual only; no backend call or balance change."
            ),
        })

    return results


def main():
    gate_on_results = run_gate_on()
    gate_off_results = run_gate_off_simulation()

    gate_on_summary = summarize(gate_on_results, "gate_on")
    gate_off_summary = summarize(gate_off_results, "gate_off_simulated")

    output = {
        "scope": (
            "Synthetic backend; no model API calls. Gate-off is a "
            "counterfactual simulation and never executes transactions."
        ),
        "attack_categories": sorted(ATTACK_CATEGORIES),
        "comparability_note": (
            "Gate-on latency is measured. Gate-off latency is null because "
            "the counterfactual does not invoke an execution path."
        ),
        "comparison": {
            "gate_on": gate_on_summary,
            "gate_off_simulated": gate_off_summary,
        },
        "results": {
            "gate_on": gate_on_results,
            "gate_off_simulated": gate_off_results,
        },
    }

    output_dir = ROOT_DIR / "eval" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "gate_comparison_latest.json"
    output_file.write_text(json.dumps(output, indent=2) + "\n")

    print(json.dumps(output["comparison"], indent=2))
    print(f"\nDetailed results written to: {output_file}")


if __name__ == "__main__":
    main()
