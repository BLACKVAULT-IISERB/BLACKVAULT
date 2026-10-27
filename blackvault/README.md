# BLACKVAULT Backend

## Purpose

This package implements the trusted authorization layer for the BLACKVAULT synthetic banking environment.

It receives structured transaction proposals, applies customer-specific security policies, and allows the mock bank to execute a transaction only after the required checks succeed.

## Responsibilities

- Validate transaction proposals.
- Check account ownership and status.
- Enforce approved-payee rules and spending limits.
- Handle transactions requiring additional approval.
- Issue and verify transaction-bound permits.
- Prevent permit forgery and reuse.
- Record transaction decisions and audit events.
- Update synthetic account balances after authorization.

## Main Modules

| Module | Responsibility |
|---|---|
| `bank.py` | Synthetic account operations and protected transaction execution |
| `gate.py` | Proposal validation and authorization decisions |
| `policy.py` | Customer policy and spending-limit checks |
| `permits.py` | Signed permit creation and verification |
| `approvals.py` | Approval workflow |
| `audit.py` | Audit event recording and queries |
| `models.py` | Transaction, decision, account, and policy models |
| `state.py` | In-memory application state and demo data |
| `service.py` | Main application-facing backend interface |
| `config.py` | Signing-key configuration |

## Transaction Flow

1. Receive a structured proposal.
2. Validate the customer, source account, payee, amount, and currency.
3. Check account ownership, payee approval, and spending limits.
4. Request additional approval when required.
5. Issue a signed permit for an authorized transaction.
6. Verify the permit and relevant transaction constraints.
7. Update the synthetic balance and record the outcome.

## Using the Backend

From the repository root, initialize the synthetic state and create the application service using the integration API documented in the root `README.md`.

Use `app.propose(...)` as the application-facing transaction entry point. Do not expose internal bank execution methods, permit-management internals, or signing keys to the AI agent.

## Security Notes

- Authorization decisions must be made by trusted backend code.
- Model-generated text must not override customer policy.
- The signing key must remain within the trusted backend process.
- Approval must be bound to the specific transaction being approved.
- Internal Python methods alone are not a security boundary.

## Limitations

The implementation uses in-memory state and simulated approval. It does not provide durable storage, production identity verification, distributed locking, or real banking connectivity.

This package is for controlled research and testing only.
