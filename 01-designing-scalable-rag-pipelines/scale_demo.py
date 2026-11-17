"""scale_demo.py: why big data needs smarter retrieval (synthetic data)."""
import random
import time
from search import BM25
from pipeline import Cache

random.seed(7)
WORDS = ("battery screen charger warranty speaker camera storage cable "
         "setup reset update bluetooth wifi water heat sound").split()
N_DOCS, SECTIONS = 5000, 4

docs, chunks = [], []
for d in range(N_DOCS):
    name = f"P{d:04d}"
    docs.append({"id": name, "text": f"{name} product manual"})
    for s in range(SECTIONS):
        body = " ".join(random.choices(WORDS, k=30))
        chunks.append({"id": f"{name}#{s}", "doc": name,
                       "text": f"{name} {body}"})


def timed(label, fn, scored):
    t = time.perf_counter()
    top = fn()
    ms = (time.perf_counter() - t) * 1000
    print(f"{label:22} {ms:8.2f} ms  items scored {scored:6}  top {top}")


q = "P4321 battery warranty"
flat = BM25(chunks)
timed("flat: every chunk", lambda: flat.search(q, 1)[0]["id"], len(chunks))

router = BM25(docs)                  # level 1: small doc summaries
def hierarchical():
    pick = {d["id"] for d in router.search(q, 2)}
    inside = [c for c in chunks if c["doc"] in pick]  # a filter in a real DB
    return BM25(inside).search(q, 1)[0]["id"]        # level 2: inside docs
timed("hierarchical: 2 docs", hierarchical, N_DOCS + 2 * SECTIONS)

cache = Cache()
cache.put(q, hierarchical())    # first answer is saved
timed("cache hit", lambda: cache.get(q), 0)
