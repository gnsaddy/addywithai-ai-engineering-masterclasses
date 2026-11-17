# Designing Scalable RAG Pipelines: masterclass code

Small, offline, CPU-only Python project used in the masterclass video. Only the Python standard library is used (Python 3.10+), so there is nothing to install.

The data is a fictional help centre for a demo shop called **QuickCart** (`kb.py`). The embedding, re-ranker, generator and planner are **toy stand-ins** so everything runs offline. Each file says where a real system would plug in a real embedding model, a cross-encoder / rerank API and an LLM.

| File | What it shows | Run |
|---|---|---|
| `kb.py` | the documents (with `##` sections) | - |
| `chunking.py` | fixed-size chunks vs section-aware chunks | `python chunking.py` |
| `search.py` | BM25 keyword search, vector search, hybrid with Reciprocal Rank Fusion | `python search.py` |
| `rerank.py` | two-stage retrieval: wide net, then re-rank | `python rerank.py` |
| `generate.py` | grounded prompt + stand-in generator that cites sources or says "I don't know" | - |
| `pipeline.py` | modular pipeline + cache + one JSON monitoring log per request | `python pipeline.py` |
| `evaluate.py` | golden test set: recall@3, MRR, faithfulness, answer correctness | `python evaluate.py` |
| `advanced.py` | agentic multi-hop loop (plan, retrieve, read, next hop) | `python advanced.py` |
| `scale_demo.py` | 20,000 synthetic chunks: flat scan vs hierarchical vs cache | `python scale_demo.py` |

Tested output (Python 3.13, Linux, CPU): see `run_output.txt`. Timings in `scale_demo.py` and `pipeline.py` change from machine to machine.

To make it real: replace `embed()` with an embedding model + a vector database (HNSW index), `rerank()` with a cross-encoder, `generate()` with an LLM call using `build_prompt()`, and the `Cache` with Redis. Keep the same interfaces; that is the point of the modular design.
