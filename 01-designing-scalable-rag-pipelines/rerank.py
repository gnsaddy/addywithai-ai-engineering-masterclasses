"""rerank.py: stage 2. Read the question and each chunk together, re-order.

Toy cross-scorer. In production use a cross-encoder or a rerank API.
"""
import re
from search import embed, tokens


def rerank_score(query, chunk):
    q, c = embed(query), embed(chunk["text"])
    covered = sum(1 for m in q if m in c) / max(1, len(q))   # meanings found
    exact = [w for w in tokens(query) if re.search(r"\d", w)]
    code_hit = all(w in chunk["text"].lower() for w in exact) if exact else 0
    return covered + (1.0 if code_hit else 0)


def rerank(query, candidates, top=3):
    scored = [(rerank_score(query, c), c) for c in candidates]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for s, c in scored[:top]]


if __name__ == "__main__":
    from chunking import build, section_chunks
    from search import Hybrid
    hybrid = Hybrid(build(section_chunks))
    q = "how long until my money comes back on a card"
    first = hybrid.search(q, k=10)            # stage 1: fast, wide net
    print("stage 1:", [c["id"] for c in first[:3]])
    best = rerank(q, first, top=3)            # stage 2: slow, precise
    print("stage 2:", [c["id"] for c in best])
