# BLACKVAULT

**A security layer for AI agents that propose banking transactions.**

BLACKVAULT is a research prototype that tests whether a trusted backend can prevent an AI agent from making unauthorized transactions, even when its inputs contain malicious or misleading instructions.

It uses a **synthetic banking environment** with fictional customers, accounts, payees, and balances. It does not connect to real banks or move real money.

## The Problem

AI agents can process invoices, emails, webpages, and payment instructions. These sources may contain prompt-injection attempts that try to redirect payments or override the user's intent.

An AI model should not be trusted to authorize its own financial actions.

## Our Approach

BLACKVAULT separates the AI agent's proposed action from the backend's authorization decision.

1. **Agent:** Produces a structured transaction proposal.
2. **Permission gate:** Checks account ownership, approved payees, transaction limits, and applicable approval requirements.
3. **Approval workflow:** Holds transactions that require additional approval.
4. **Permit verification:** Validates a signed, transaction-bound permit before execution.
5. **Mock bank:** Independently checks authorization and available funds before changing synthetic balances.
6. **Audit trail:** Records transaction decisions and relevant security events.

**Core principle:** The agent may propose a transaction, but only the trusted backend can authorize it.

## Key Features

- Policy-based transaction authorization
- Approved-payee and spending-limit checks
- Signed permits with expiry and transaction binding
- Approval workflow for higher-value transactions
- Protection against forged and reused permits
- Synthetic banking environment for safe testing
- Unit, adversarial, and concurrency tests
- Evaluation scripts for measuring authorization outcomes

## Architecture

```text
AI Agent / Test Input
        |
        v
Structured Transaction Proposal
        |
        v
Permission Gate
        |
        +---- Denied
        |
        +---- Approval Required
        |
        v
Signed Transaction Permit
        |
        v
Mock Bank Verification
        |
        v
Synthetic Balance Update + Audit Event
```

## Project Structure

| Directory / File | Purpose |
|---|---|
| `AI AGENT/` | AI agent component that generates transaction proposals |
| `blackvault/` | Backend authorization, policy, permit, approval, bank, and audit logic |
| `tests/` | Automated tests for backend behavior and security controls |
| `eval/` | Evaluation cases, runners, and reports, if present in the checked-out version |
| `demo.py` | Deterministic demonstration of transaction security scenarios |
| `requirements.txt` | Python dependencies |
| `.env.example` | Example environment configuration |

## Setup

Requirements: Python 3.10 or later is recommended. Use the Python version supported by the project's dependencies.

### Windows PowerShell

```powershell
git clone https://github.com/BLACKVAULT-IISERB/BLACKVAULT.git
cd BLACKVAULT

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Set a temporary signing key for the current PowerShell session:

```powershell
$env:BLACKVAULT_HMAC_KEY = python -c "import secrets,base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

The key is for local testing only. Do not commit real secrets or share signing keys with the AI agent.

## Run the Demo

```powershell
python demo.py
```

The demo illustrates approved transfers, denied payees, transaction limits, approval requirements, forged permits, permit replay, insufficient funds, and a prompt-injection-style proposal.

All transactions use fictional data.

## Run the Tests

```powershell
python -m pytest -v
```

Tests help verify the implemented controls; they do not prove that the system is secure against every possible attack.

If the evaluation scripts are present in your checkout, consult `eval/README.md` for their commands and interpretation.

## Current Status

BLACKVAULT is a **research prototype**, not a production banking product.

Its current design demonstrates backend-enforced authorization in a synthetic environment. The AI agent and backend are separate components; a production transport or API adapter between them is not yet implemented.

## Limitations

- Application state and audit events are held in memory.
- Human approval is simulated.
- Replay and idempotency history do not persist across restarts.
- There is no production identity system, durable database, or real banking integration.
- The prototype has not undergone an independent security audit.

## Future Work

- Add a secure interface between the agent and backend.
- Introduce durable storage and stronger audit integrity.
- Integrate bank-managed identity and approval systems in a controlled test environment.
- Expand adversarial testing and evaluation coverage.
- Assess deployment requirements with banking security and compliance teams.

## Intended Use

BLACKVAULT is intended for research, demonstration, and controlled testing of AI-agent transaction security. It must not be used to authorize real financial transactions in its current form.
