# BLACKVAULT

BLACKVAULT is a synthetic banking sandbox for demonstrating how a backend can keep an AI agent within a customer's transaction permissions. It uses fictional customers, accounts, payees, and balances only. It does not connect to banks, payment services, or real funds.

## The problem

An AI agent may read invoices, emails, webpages, or payee notes while helping with a payment. Those sources can contain prompt injection: instructions that try to make the agent ignore the customer's intent and send money to an attacker. A model can propose an action, but text supplied to the model is not trusted authorization.

BLACKVAULT places a trusted backend permission gate between an agent proposal and synthetic balance changes. The gate checks customer-owned policy and the bank verifies a signed, short-lived permit before executing a transfer.

## Architecture and transaction flow

1. The agent submits a structured `Proposal` with customer ID, source account ID, payee ID, amount, currency, and optional idempotency key. Untrusted document contents are not policy inputs.
2. `PermissionGate` validates the request, checks account ownership and active status, confirms the payee is present and approved by the customer's active policy, validates INR amount precision, and enforces per-transaction and UTC-day spending limits.
3. If the amount exceeds the policy's approval threshold, the gate creates an expiring approval request bound to the exact transaction details and returns `PENDING_APPROVAL`. The simulated trusted operator callback records a decision. The caller then resubmits the same proposal with the returned approval ID. Natural-language claims by the agent are not accepted as approval.
4. After authorization (and any required approval), the gate issues an HMAC-SHA-256 permit bound to the transaction, customer, source account, payee, amount, currency, timestamps, and nonce.
5. The application service passes that permit to the bank's internal execution method. The bank independently verifies the signature, expiry, transaction binding, account ownership/status, policy, spending limit, approval, destination, and available balance. Under the shared in-process lock, it updates the synthetic balances, consumes the permit and approval, updates the transaction, and records the audit event.
6. Denials and approval events are also recorded in the in-memory audit list. Audit records do not include signing secrets or raw invoice/webpage content.

All production-facing integration should use `Blackvault.propose(...)`; the bank execution method is an internal helper. Do not expose the `Blackvault` object's permit manager, bank internals, signing key, or approval callback to the AI agent. Python-level internal names are not a security sandbox, so the process/API adapter must enforce that separation.

## Project layout

```text
blackvault-complete-source/
├── AI AGENT/                 # Separate agent component; not imported by this backend
├── blackvault/
│   ├── bank.py               # Account reads and internal permit-checked execution
│   ├── gate.py               # Central proposal validation and permit authorization
│   ├── policy.py             # Decimal validation and customer policy checks
│   ├── permits.py            # HMAC permit creation and verification
│   ├── approvals.py          # Simulated independent approval workflow
│   ├── audit.py               # In-memory audit event recording and queries
│   ├── models.py              # Proposal, decision, account, and policy models
│   ├── state.py               # Shared in-memory application state and demo seed
│   ├── service.py             # Stable Blackvault integration facade
│   ├── transaction_service.py # Compatibility export of the facade
│   ├── config.py              # Environment signing-key loader
│   ├── repositories.py        # Small state access facade
│   ├── exceptions.py
│   └── __init__.py
├── tests/                     # Pytest unit, adversarial, and concurrency tests
├── demo.py                    # Deterministic synthetic demonstration
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

Storage is in memory only. There is no SQL database or external persistence service.

## Setup (Windows PowerShell)

From this project root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The demo requires a base64-encoded signing key with at least 32 random bytes. Generate and set one for the current PowerShell session:

```powershell
$env:BLACKVAULT_HMAC_KEY = python -c "import secrets,base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

`demo.py` reads `BLACKVAULT_HMAC_KEY` using `blackvault.config.signing_key_from_env()` and fails closed when it is missing or too short. `.env.example` documents the variable; the project does not load `.env` files automatically. Do not commit a real local `.env` or signing key.

## Run the demo and tests

```powershell
python demo.py
python -m pytest -v
```

The demo shows an approved transfer, unapproved and over-limit proposals, independent approval, a forged permit, a permit replay, insufficient funds, and an unapproved prompt-injection-style proposal. Results use fictional accounts and balances.

## Backend integration API

The current integration surface is defined by the code in `blackvault/`:

```python
from blackvault import AppState, Blackvault, Proposal, seed_demo_state

state = seed_demo_state(AppState())
app = Blackvault(state, signing_key_bytes)  # at least 32 bytes

account = app.account_info(customer_id, account_id)
decision = app.propose(Proposal(
    customer_id=customer_id,
    source_account_id=account_id,
    payee_id=payee_id,
    amount="125.00",
    currency="INR",
    idempotency_key="agent-request-123",
))
# If status is PENDING_APPROVAL, show the exact request to a trusted operator,
# call app.approve(decision.approval_id, approved=True), then resubmit the same
# Proposal with approval_id=decision.approval_id.
app.transaction(decision.transaction_id)
app.audit_events(category=None, customer_id=None)
```

`Decision` reports a status, transaction ID, reason code, message, and optionally an approval ID. `app.propose(proposal, approval_id=None)` returns `EXECUTED`, `DENIED`, `PENDING_APPROVAL`, or `FAILED`. The `permit` field is internal and excluded from `Decision.as_dict()`.

### AI agent and backend team integration

The `AI AGENT/` folder is a separate team component; the backend does not import an agent implementation. Integrate the agent by having it produce a `Proposal` and call the backend facade, then consume the structured decision and transaction result. Only the backend/service process should hold the signing key. The agent must not set trusted policy, mint permits, or approve its own transactions.

The agent-facing request/response transport (for example, HTTP or a local process protocol) is not implemented in this repository. Team members should agree on the `Proposal` fields and the `Decision` status/reason codes before adding an adapter. The present backend API can also support the red-team harness through isolated `AppState` instances, explicit `seed_demo_state(...)`, `app.propose(...)`, `app.transaction(...)`, and `app.audit_events(...)`.

## Current limitations

- All customers, accounts, policies, transactions, permits, approvals, spending records, and audit events are held in process memory. They are lost on restart; replay protection and idempotency history do not survive it.
- The `RLock` coordinates threads in one process only; it does not coordinate multiple processes or hosts.
- Human approval is a simulated callback, not identity verification or a secure out-of-band approval product.
- Audit events are in-memory records, not durable or tamper-resistant evidence. Python standard-library logging is not a replacement for a production audit system.
- This repository has no HTTP server, authentication layer, production key-management integration, or real banking connection.
- The prototype has not been independently security-audited and is not suitable for real banking transactions. Passing tests is not proof of production security.
