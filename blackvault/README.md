# BLACKVAULT Backend

## Purpose

Implements the banking backend and transaction security controls used to authorize, validate, and execute banking transactions requested by the AI agent.

## File Structure

| File | Purpose |
|---|---|
| `__init__.py` | Exposes the main classes and functions. |
| `service.py` | Coordinates authorization, approvals, permits, and transfers. |
| `transaction_service.py` | Re-exports the `Blackvault` interface. |
| `gate.py` | Authorizes transaction proposals and enforces security rules. |
| `policy.py` | Validates amounts, approved payees, and spending limits. |
| `permits.py` | Issues and verifies signed, time-limited transaction permits. |
| `approvals.py` | Handles additional approval for high-value transactions. |
| `bank.py` | Retrieves account information and executes validated transfers. |
| `audit.py` | Records and retrieves security events. |
| `models.py` | Defines accounts, policies, proposals, permits, approvals, and decisions. |
| `state.py` | Stores application data and initializes fictional demo data. |
| `config.py` | Loads and validates the permit signing key. |
| `repositories.py` | Provides access to account, policy, and audit data. |
| `exceptions.py` | Defines custom application exceptions. |

## Transaction Pipeline

1. `service.py` receives a transaction proposal.
2. `gate.py` validates the request using `policy.py`.
3. `approvals.py` handles additional approval when required.
4. `permits.py` issues a signed permit after authorization.
5. `bank.py` verifies the permit and rechecks transaction constraints before execution.
6. `state.py` stores transaction and account data.
7. `audit.py` records relevant events and outcomes.
8. `service.py` returns the transaction result.

## Integration with BLACKVAULT

The AI agent submits transaction proposals to this backend. The security gate independently checks whether each proposed transaction is permitted before the banking backend executes it.

This package provides the controlled banking environment used to evaluate whether adversarial manipulation of the AI agent can result in unauthorized transactions.

## Security Scope

The backend uses fictional accounts and synthetic balances. Its approval workflow simulates a trusted-human callback and does not independently verify human identity.
