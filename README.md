# AI Engineering Masterclasses: code for every masterclass

Python code for **AI Engineering: Production Masterclasses** by **@addywithai**. Each folder is a standalone masterclass and has its own `README.md`.

## How to run any masterclass

```bash
cd <folder>
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt   # if the folder has one
cp .env.example .env              # only if the folder has one, then paste your own key
```

Then follow the run steps in that folder's `README.md`. Never commit your `.env` file; it is already in `.gitignore`.

Python 3.10 or newer.

## Masterclasses

| # | Masterclass | What it covers | Code |
|---|---|---|---|
| 1 | Learn Designing Scalable RAG Pipelines | Chunking, search, re-ranking, generation, evals and scaling a RAG pipeline (stdlib Python, CPU only) | [01-designing-scalable-rag-pipelines](01-designing-scalable-rag-pipelines) |
| 2 | Learn Enterprise AI Agents | Identity, permission-aware search, safe tool calls with approval + idempotency, retries, evals and an end-to-end demo (stdlib Python, CPU only) | [02-enterprise-ai-agents](02-enterprise-ai-agents) |
| 3 | Learn Agent Evals and CI Gates | Trajectory evals, calibrated LLM judge and a CI gate that blocks bad prompt/model changes (stdlib Python, CPU only) | [03-agent-evals-and-ci-gates](03-agent-evals-and-ci-gates) |
