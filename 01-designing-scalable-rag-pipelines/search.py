"""search.py: keyword search (BM25), vector search and hybrid search (RRF)."""
import math
import re
from collections import Counter

STOP = set("a an the is are was to of in on for my i do does can how what "
           "when it and or be by with from your our we you get".split())
# Toy embedding: words -> meaning ids. A real system uses an embedding model.
MEANING = {"money": "refund", "back": "refund", "refund": "refund",
           "refunds": "refund", "reversed": "refund", "cash": "pay",
           "pay": "pay", "payment": "pay", "emi": "pay", "instalments": "pay",
           "parts": "pay", "ship": "ship", "delivery": "ship", "arrive": "time",
           "days": "time", "long": "time", "take": "time", "fee": "price",
           "costs": "price", "price": "price", "free": "price",
           "cost": "price", "much": "price", "returned": "return",
           "phones": "phone", "refunded": "refund",
           "password": "login", "forgot": "login", "login": "login"}


def tokens(text):
    return [w for w in re.findall(r"[a-z0-9-]+", text.lower()) if w not in STOP]


class BM25:
    """Classic keyword ranking: rare words that match count the most."""
    def __init__(self, chunks, k1=1.5, b=0.75):
        self.chunks, self.k1, self.b = chunks, k1, b
        self.docs = [Counter(tokens(c["text"])) for c in chunks]
        self.avg = sum(sum(d.values()) for d in self.docs) / len(self.docs)
        df = Counter(w for d in self.docs for w in d)
        n = len(self.docs)
        self.idf = {w: math.log(1 + (n - f + .5) / (f + .5))
                    for w, f in df.items()}

    def search(self, query, k=5):
        q, out = tokens(query), []
        for i, d in enumerate(self.docs):
            size = sum(d.values()) / self.avg
            s = sum(self.idf.get(w, 0) * d[w] * (self.k1 + 1) /
                    (d[w] + self.k1 * (1 - self.b + self.b * size)) for w in q)
            out.append((s, i))
        best = sorted(out, reverse=True)[:k]
        return [self.chunks[i] for s, i in best if s > 0]


def embed(text):
    """Toy vector: count of meanings. Swap in a real embedding model."""
    # Like many real models, the toy blurs exact codes and numbers.
    return Counter("<num>" if re.search(r"\d", w) else MEANING.get(w, w)
                   for w in tokens(text))


def cosine(a, b):
    dot = sum(a[w] * b[w] for w in a)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


class VectorIndex:
    def __init__(self, chunks):
        self.chunks = chunks
        self.vecs = [embed(c["text"]) for c in chunks]

    def search(self, query, k=5):
        q = embed(query)
        scores = sorted(((cosine(q, v), i) for i, v in enumerate(self.vecs)),
                        reverse=True)[:k]
        return [self.chunks[i] for s, i in scores if s > 0]


def rrf(*ranked_lists, k=60, top=5):
    """Reciprocal Rank Fusion: 1 / (k + rank), summed over the lists."""
    score = Counter()
    by_id = {}
    for ranked in ranked_lists:
        for rank, c in enumerate(ranked, start=1):
            score[c["id"]] += 1 / (k + rank)
            by_id[c["id"]] = c
    return [by_id[i] for i, _ in score.most_common(top)]


class Hybrid:
    def __init__(self, chunks):
        self.bm25, self.vec = BM25(chunks), VectorIndex(chunks)

    def search(self, query, k=5):
        keyword = self.bm25.search(query, 20)
        meaning = self.vec.search(query, 20)
        return rrf(keyword, meaning, top=k)


if __name__ == "__main__":
    from chunking import build, section_chunks
    chunks = build(section_chunks)
    engines = {"keyword": BM25(chunks), "vector": VectorIndex(chunks),
               "hybrid": Hybrid(chunks)}
    for q in ["what is E-204", "how long until my money comes back on a card"]:
        print(f'Q: "{q}"')
        for name, eng in engines.items():
            top = [c["id"] for c in eng.search(q, 3)]
            print(f"  {name:8}", " | ".join(top) or "-")
