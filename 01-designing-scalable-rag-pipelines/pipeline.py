"""pipeline.py: a modular RAG pipeline with a cache and monitoring logs."""
import json
import time
from chunking import build, section_chunks
from search import Hybrid
from rerank import rerank
from generate import generate, build_prompt


class Cache:
    """Exact-match cache on the normalised question, with a time limit."""
    def __init__(self, ttl=3600):
        self.ttl, self.store = ttl, {}

    def key(self, q):
        return " ".join(q.lower().strip(" ?!.").split())

    def get(self, q):
        hit = self.store.get(self.key(q))
        return hit[1] if hit and time.time() - hit[0] < self.ttl else None

    def put(self, q, answer):
        self.store[self.key(q)] = (time.time(), answer)


class RAGPipeline:
    def __init__(self, retriever, reranker, generator, cache, k=10, top=3):
        self.retriever, self.reranker = retriever, reranker
        self.generator, self.cache = generator, cache
        self.k, self.top = k, top

    def ask(self, q, user="demo"):
        t0, ms = time.perf_counter(), {}
        def lap(name):
            ms[name] = round((time.perf_counter() - t0) * 1000, 2)
        answer = self.cache.get(q)
        hit, best, tokens = answer is not None, [], 0
        if not hit:
            found = self.retriever.search(q, self.k); lap("retrieve")
            best = self.reranker(q, found, self.top); lap("rerank")
            answer = self.generator(q, best); lap("generate")
            tokens = int(len(build_prompt(q, best).split()) * 1.3)
            self.cache.put(q, answer)
        else:
            lap("cache")
        log = {"user": user, "hit": hit, "ms": ms, "tokens": tokens,
               "src": [c["id"] for c in best]}
        print("LOG", json.dumps(log))
        return answer


if __name__ == "__main__":
    rag = RAGPipeline(Hybrid(build(section_chunks)), rerank, generate, Cache())
    for q in ["How long until my money comes back on a card?",
              "how long until my money comes back on a card",
              "Do you sell gift cards?"]:
        print("A:", rag.ask(q), "\n")
