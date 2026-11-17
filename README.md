# AI Engineering Masterclasses: code for every masterclass

Python code for the **AI Engineering Masterclasses** series by **@addywithai**. Each folder matches one masterclass and has its own `README.md`.

## How to run any lecture

```bash
cd <folder>
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt   # if the folder has one
cp .env.example .env              # only if the folder has one, then paste your own key
```

Then follow the run steps in that folder's `README.md`. Never commit your `.env` file; it is already in `.gitignore`.

Python 3.10 or newer.

## Masterclasss

| # | Masterclass | Code |
|---|---|---|
| 1 | Learn Designing Scalable RAG Pipelines | [01-designing-scalable-rag-pipelines](01-designing-scalable-rag-pipelines) |
