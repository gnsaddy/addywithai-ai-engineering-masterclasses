# Enterprise AI agents masterclass: code

Tiny, offline versions of the layers a production AI agent needs. Python 3.10+ standard library only: no API keys, no installs, runs on any laptop CPU.
The company (Nimbus Corp, Acme), people and documents are made up. `plan()` in agent.py is an LLM stand-in so the demo is repeatable; a real model returns the same shape (a tool call or a final answer).

| File | What it shows |
|---|---|
| company.py | made-up users, tenants, documents with access lists, tiny backends |
| auth.py | signed token (JWT-style, simplified), RBAC + ABAC checks |
| retrieval.py | permission-aware search: tenant + role filter inside the search, prompt-injection guard |
| tools.py | safe tool calls: schema check, permission, human approval, idempotency key, audit trail |
| agent.py | the agent loop: identity from the token, model proposes, tools run safely, step limit |
| reliability.py | retries with backoff + jitter, circuit breaker, dead-letter queue |
| evaluate.py | task eval set: success rate, rule breaks, steps; catches a v1 bug |
| demo.py | end-to-end demo: 3 employees, approval flow, no double refund, audit trail |

Run each file:
```
python auth.py
python retrieval.py
python tools.py
python agent.py
python reliability.py
python evaluate.py
python demo.py
```
Real output of every file is in `run_output.txt`.

In production, swap the stand-ins: a real identity provider (OAuth 2.0 / OpenID Connect, verified JWTs), a policy engine, a vector store with metadata filters, a real LLM, a queue with a dead-letter queue, and a tracing tool. Never hard-code secrets: read them from the environment or a vault.
