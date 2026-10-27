# Automated Tests

## Purpose

This directory contains automated tests for the BLACKVAULT backend and its security controls.

The tests verify expected behavior for valid transactions, rejected transactions, approval workflows, and other security-sensitive cases.

## What Is Tested

Depending on the test module, coverage may include:

- Valid and invalid transaction proposals
- Account ownership and account status
- Approved and unapproved payees
- Transaction and spending limits
- Required approval and rejected approval
- Forged, expired, or reused permits
- Insufficient funds
- Audit event behavior
- Duplicate requests and concurrency-sensitive operations

## Run the Tests

Run the following command from the repository root:

```powershell
python -m pytest -v
```

To run this directory only:

```powershell
python -m pytest tests -v
```

## Interpreting Results

- **Passed:** The tested assertion matched the expected behavior.
- **Failed:** Inspect the failure message and traceback before changing code.
- **Coverage limitation:** Passing tests do not prove that every attack is prevented.

When adding a security test, document the attack or behavior being tested, the expected decision, and whether the synthetic account balance or audit state should change.
