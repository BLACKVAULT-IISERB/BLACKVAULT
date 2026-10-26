# BLACKVAULT Tests

## Purpose

Contains automated tests that verify banking functionality, transaction authorization, security controls, and resistance to invalid or adversarial transaction requests.

## Test Files

| File | Purpose |
|---|---|
| `conftest.py` | Creates shared test fixtures for the application and demo state. |
| `test_security.py` | Tests transfers, access control, invalid transactions, idempotency, permit tampering, replay, and audit logging. |
| `test_gate.py` | Tests approval retries, daily limits, and transaction failure handling. |
| `test_policy.py` | Tests missing and inactive policies. |
| `test_permits.py` | Tests invalid, expired, tampered, and future-dated permits. |
| `test_approvals.py` | Tests rejected and expired approvals. |
| `test_bank.py` | Tests account access restrictions and currency mismatches. |
| `test_audit.py` | Tests audit event recording and querying. |
| `test_concurrency.py` | Tests whether simultaneous transfers can cause account overspending. |

## How the Tests Connect to the Backend

The tests import the `blackvault` package and use shared fixtures from `conftest.py` to create an application instance with fictional banking data.

They submit transaction proposals, trigger security checks, and verify the resulting status, rejection reason, account balances, permits, approvals, and audit events.

## Running the Tests

Run from the repository root:

```bash
python -m pytest -q
```

Run an individual test file:

```bash
python -m pytest tests/test_security.py -v
```

## Evaluation Scope

The tests verify the implemented backend controls, including authorization rules, permit integrity, approval handling, idempotency, audit logging, and concurrency safety.

These tests do not, by themselves, establish that the complete AI agent is resistant to all adversarial attacks. End-to-end attack evaluation must also test the integrated agent and security gate.
