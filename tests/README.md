# BLACKVAULT – Automated Test Suite

## 1. Overview

The `tests/` directory contains automated tests for validating the security, reliability and correctness of the BLACKVAULT banking backend and its AI-agent workflow.

The tests verify that:
- Unauthorized banking operations are rejected.
- Account ownership and beneficiary policies are enforced.
- Transaction limits are respected.
- Additional approvals are required when applicable.
- Cryptographic permits cannot be forged, modified or replayed.
- Concurrent transactions do not cause unintended overspending.
- AI-generated transaction proposals are handled safely.
- Security decisions are recorded in the audit system.

The test suite uses **pytest**.

## 2. Test File Documentation

### 2.1 `conftest.py` – Shared Test Configuration

Provides common pytest fixtures and test setup.

Its responsibilities include:
- Initializing reusable test objects.
- Providing synthetic banking accounts and test data.
- Configuring shared backend components.
- Avoiding repeated setup code across test files.

### 2.2 `test_agent_adapter.py` – AI Agent Adapter Tests

Tests the adapter responsible for translating AI-generated transaction proposals into backend-compatible requests.

Covers:
- Proposal-to-backend data conversion.
- Transaction field validation.
- Handling missing or malformed proposal data.
- Rejection of invalid transaction requests.
- Safe communication between the AI agent and banking backend.

### 2.3 `test_agent_coordinator.py` – Agent Coordinator Tests

Tests the component coordinating AI-generated banking actions.

Covers:
- Coordination of transaction requests.
- Correct sequencing of workflow operations.
- Interaction between proposal generation and transaction handling.
- Handling authorization failures.
- Preventing unintended execution during workflow errors.

### 2.4 `test_agent_proposals.py` – Structured AI Proposal Tests

Tests whether AI-generated transaction proposals follow the expected structure.

Covers:
- Required transaction fields.
- Proposal status validation.
- Recipient and amount extraction.
- Handling incomplete proposals.
- Rejection of malformed or invalid proposals.

### 2.5 `test_agent_workflow.py` – AI Agent Workflow Tests

Tests the overall banking workflow involving the AI agent.

Covers:
- Processing transaction requests.
- Recipient identification and resolution.
- Confirmation requirements.
- Correct transaction workflow progression.
- Handling cancellation and incomplete requests.

### 2.6 `test_agent_workflow_security.py` – Adversarial Agent Workflow Tests

Tests security weaknesses that may arise during AI-agent banking workflows.

Covers:
- Unauthorized beneficiary rejection.
- Security checks after transaction confirmation.
- Prevention of bypassing authorization through workflow manipulation.
- Ensuring that confirmation does not override backend security policies.

### 2.7 `test_approvals.py` – Transaction Approval Tests

Tests the additional authorization mechanisms required for sensitive transactions.

Covers:
- Rejection of denied approvals.
- Approval expiration.
- Validation of approval status.
- Enforcement of approval requirements before execution.

### 2.8 `test_audit.py` – Audit Logging Tests

Tests the backend's audit functionality.

Covers:
- Recording security-relevant events.
- Retrieving audit records.
- Ensuring transaction decisions can be inspected.
- Supporting traceability of banking operations.

### 2.9 `test_bank.py` – Synthetic Banking Tests

Tests the core mock banking functionality.

Covers:
- Account access restrictions.
- Private account ownership checks.
- Currency mismatch handling.
- Correct handling of banking account data.

### 2.10 `test_concurrency.py` – Concurrent Transaction Tests

Tests the banking backend under simultaneous transaction requests.

Covers:
- Multiple concurrent transfers.
- Prevention of overspending.
- Correct balance handling under concurrent operations.
- Consistency of transaction execution.

### 2.11 `test_confirmation.py` – Transaction Confirmation Tests

Tests the confirmation stage before executing banking transactions.

Covers:
- Preparing a transfer without changing account balances.
- Executing a transfer after valid confirmation.
- Cancelling a pending transfer.
- Preventing repeated confirmation.
- Rejecting confirmation by the wrong customer.
- Preventing execution of expired proposals.
- Rejecting unapproved beneficiaries even after confirmation.

### 2.12 `test_gate.py` – Permission Gate Tests

Tests the central BLACKVAULT authorization gate.

Covers:
- Idempotent handling of pending approval requests.
- Rechecking daily transaction limits.
- Counting only successful transactions towards applicable limits.
- Recording and replaying insufficient-funds failures.
- Enforcing authorization rules before transaction execution.

### 2.13 `test_permits.py` – Cryptographic Permit Tests

Tests the integrity and validity of transaction authorization permits.

Covers:
- Rejection of missing permits.
- Rejection of expired permits.
- Detection of permit claim tampering.
- Rejection of invalid or improperly issued permits.
- Validation of permit integrity and authorization claims.

### 2.14 `test_policy.py` – Banking Policy Tests

Tests the rules that determine which transactions are permitted.

Covers:
- Handling missing policy configurations.
- Rejecting inactive or invalid policies.
- Enforcing beneficiary restrictions.
- Validating applicable banking authorization rules.

### 2.15 `test_security.py` – Core Banking Security Tests

Tests the main security properties of the banking backend.

Covers:
- Successful execution of legitimate transfers.
- Rejection of unapproved beneficiaries.
- Enforcement of transaction limits.
- Additional approval requirements.
- Exact transaction and authorization binding.
- Account ownership validation.
- Invalid transaction amount rejection.
- Idempotent transaction retry handling.
- Conflict detection.
- Audit logging of failed authorization attempts.
- Rejection when signing keys are missing.
- Detection of permit tampering and replay attempts.

## 3. Running the Tests

### Run the entire test suite

From the repository root:

```bash
python -m pytest -v
```

The `-v` flag displays each individual test and its result.

### Run a particular test file

For example:

```bash
python -m pytest -v tests/test_security.py
```

### Run a particular test category

```bash
python -m pytest -v tests/test_agent_workflow_security.py
```

### Generate a concise summary

```bash
python -m pytest -q
```

### Save test output

```bash
mkdir -p judge_evidence
python -m pytest -v | tee judge_evidence/test_results.txt
```

## 4. Test Result Interpretation

Each test produces one of the following outcomes:

| Result | Meaning |
|---|---|
| PASSED | The test's expected behaviour was observed. |
| FAILED | The observed behaviour differed from the expected behaviour. |
| ERROR | The test could not execute successfully, often due to a setup or runtime problem. |
| SKIPPED | The test was intentionally not executed. |

### Previously observed result

The project's terminal output showed:

**57 passed in 1.19 seconds.**

This indicates that all 57 tests in that particular run passed.

The result should be reproduced on the current repository revision before being presented as the latest result.

## 5. Security Coverage Summary

| Security area | Relevant test files |
|---|---|
| AI proposal validation | `test_agent_proposals.py` |
| Agent workflow security | `test_agent_workflow_security.py` |
| Agent/backend adapter | `test_agent_adapter.py` |
| Workflow coordination | `test_agent_coordinator.py` |
| Transaction confirmation | `test_confirmation.py` |
| Account ownership | `test_bank.py`, `test_security.py` |
| Beneficiary authorization | `test_security.py`, `test_agent_workflow_security.py` |
| Spending limits | `test_gate.py`, `test_security.py` |
| Additional approvals | `test_approvals.py`, `test_security.py` |
| Cryptographic permits | `test_permits.py`, `test_security.py` |
| Replay protection | `test_permits.py`, `test_security.py` |
| Concurrent transactions | `test_concurrency.py` |
| Audit and traceability | `test_audit.py`, `test_security.py` |
| Policy enforcement | `test_policy.py` |

## 6. Important Note

Passing automated tests demonstrates that the tested implementation behaves according to the expected outcomes for the covered scenarios.

It does not establish that the system is immune to every possible attack.

Test coverage, adversarial robustness, integration testing and real-world security validation are separate evaluation requirements.

The test descriptions in this document are based on the test filenames and visible test names. For exact test-by-test documentation, inspect the individual test functions in each Python file.
