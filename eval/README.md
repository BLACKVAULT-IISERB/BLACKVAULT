# Security Evaluation

## Purpose

This directory contains the test cases and evaluation scripts used to measure BLACKVAULT's behavior against legitimate requests and adversarial transaction proposals.

The evaluation complements unit tests by recording outcomes across defined scenarios.

## Contents

- `cases.json` — evaluation inputs, if present.
- `runner.py` — model-assisted proposal evaluation, if present.
- `backend_runner.py` — backend authorization evaluation, if present.
- `gate_comparison.py` — gate-on results and simulated gate-off comparison, if present.
- `results/` — saved evaluation outputs, if present.
- `reports/` — summarized evaluation reports, if present.

Use the actual filenames in the current repository if they differ.

## Running the Evaluations

From the repository root, run only the scripts that exist in your checkout:

```powershell
python eval/runner.py
python eval/backend_runner.py
python eval/gate_comparison.py
```

The model-assisted runner may require a configured API key. Check its source and environment configuration before running it.

## Metrics

Depending on the evaluation script, results may include:

- Attack success rate
- Attack block rate
- Unauthorized execution count
- Legitimate-request execution rate
- Expected outcomes met
- Request latency

## Interpretation

- **Attack success rate:** Fraction of evaluated attack attempts that achieved the defined unsafe outcome.
- **Attack block rate:** Fraction of evaluated attack attempts blocked by the system.
- **Legitimate execution rate:** Fraction of eligible legitimate requests executed as expected.
- **Latency:** Time recorded by the specific runner; do not compare results unless measurement methods are consistent.

Gate-off results are counterfactual or simulated if no actual unprotected transaction was executed. Label them clearly and do not present them as real-world attack outcomes.

## Limitations

Evaluation results depend on the scenario set, test assumptions, and implementation. Small test sets and heuristic model flags are preliminary evidence, not proof of security. Record the number of cases, execution conditions, and limitations with every reported result.
