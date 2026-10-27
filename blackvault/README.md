# BLACKVAULT Backend

## Overview

The `blackvault/` package implements the backend security layer for BLACKVAULT. It evaluates transaction proposals, enforces authorization policies, manages approvals and permits, and controls transactions in a synthetic banking environment.

The AI agent can propose a transaction, but **the trusted backend is responsible for authorization and execution**.

## Core Responsibilities

- Validate transaction proposals.
- Enforce account ownership and transaction policies.
- Check approved payees and spending limits.
- Handle explicit confirmation and additional approval requirements.
- Verify transaction permits and prevent unauthorized reuse.
- Execute authorized transactions against synthetic accounts.
- Record transaction outcomes and security events.

## Module Guide

| File | Description |
|---|---|
| `__init__.py` | Initializes the Python package and may expose package-level interfaces. |
| `agent_adapter.py` | Provides an adapter between the AI agent and backend functionality. |
| `agent_coordinator.py` | Coordinates agent-related operations. |
| `agent_workflow.py` | Manages the workflow for processing agent-generated transaction proposals. |
| `approvals.py` | Handles transaction approval requirements and decisions. |
| `audit.py` | Records transaction decisions and security-related events. |
| `bank.py` | Implements synthetic banking operations and account transactions. |
| `config.py` | Contains backend configuration and security-related settings. |
| `confirmation.py` | Handles explicit confirmation of pending transactions. |
| `exceptions.py` | Defines application-specific exceptions. |
| `file_guide.md` | Provides additional documentation about the package's files. |
| `gate.py` | Enforces authorization checks before transactions can proceed. |
| `models.py` | Defines data structures used by the backend. |
| `permits.py` | Handles transaction permit creation and verification. |
| `policy.py` | Defines authorization rules, approved payees, and spending limits. |
| `repositories.py` | Provides interfaces or implementations for accessing application data. |
| `service.py` | Provides the main application-facing backend service. |
| `state.py` | Manages application state and synthetic data. |
| `transaction_service.py` | Handles transaction-related operations. |

## Transaction Workflow

1. The AI agent submits a structured transaction proposal.
2. The backend validates the proposal and relevant account details.
3. The permission gate checks the applicable authorization policies.
4. Transactions requiring additional approval or confirmation are held until the required step is completed.
5. The backend verifies the applicable permit and transaction constraints.
6. The synthetic bank processes an authorized transaction.
7. The transaction outcome is recorded for auditing.

## Security Principles

- AI-generated proposals are treated as untrusted input.
- The agent cannot authorize its own transactions.
- Backend policies determine which transactions are permitted.
- Transaction permits must be validated before execution.
- Approval and confirmation requirements must be enforced by trusted application logic.
- Failed or denied transactions must not improperly modify account balances.

## Testing

Run the automated tests from the repository root:

```bash
python -m pytest -v
```

Refer to the root `README.md` for project setup and demonstration instructions.

## Limitations

BLACKVAULT is a research prototype that uses synthetic banking data. It is not connected to real banking infrastructure and is not intended for production financial transactions.

Production deployment would require additional work on persistent storage, identity management, concurrency control, monitoring, audit integrity, and independent security testing.
