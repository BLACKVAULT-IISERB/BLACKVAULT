# AI Agent

## Purpose

This directory contains the AI agent component for the BLACKVAULT project. Its role is to interpret a user's banking-related request and generate a structured transaction proposal.

The agent does not have authority to approve or execute transactions independently.

## Responsibilities

- Interpret the user's request.
- Generate a structured transaction proposal.
- Return the proposal for backend authorization.
- Keep model-generated output separate from trusted banking policy.
- Allow the backend to make the final authorization decision.

## Main Files

- `agent.py` — agent logic and proposal generation.
- `.env.example` — example configuration, if provided.

Check the source files for the current implementation details.

## Configuration

If the agent uses Groq, configure the required API key in your local environment. Follow the variable names documented in the source code or example environment file.

Never commit API keys, tokens, or other secrets.

## Integration Contract

The intended flow is:

1. The agent generates a transaction proposal.
2. The proposal is passed to the trusted backend.
3. The backend checks the proposal against the customer's policy.
4. The backend returns a structured decision.
5. The agent reports that decision rather than treating its own output as authorization.

The agent must not receive the backend's signing key, mint permits, modify trusted policies, or approve its own transactions.

## Important

A model response is untrusted input. A valid-looking proposal is not proof of authorization.

This component is part of a research prototype and is not intended to connect directly to real banking systems.
