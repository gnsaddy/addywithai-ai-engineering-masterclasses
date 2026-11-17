"""evaluate.py: measure retrieval and answers on a small golden test set."""
from chunking import build, section_chunks
from search import BM25, VectorIndex, Hybrid, tokens
from rerank import rerank
from generate import generate

# (question, the chunk that must be found, a fact the answer must contain)
GOLDEN = [
    ("what is E-204", "errors#E-204", "auto-reversed"),
    ("how long until my money comes back on a card",
     "refunds#Refund timeline", "5 to 7"),
    ("can I return a phone after 8 days", "returns#Return window", "7 day"),
    ("is delivery free for Plus members", "shipping#Delivery fee", "free"),
    ("how much does Plus cost", "plus#Price", "999"),
    ("can I pay for Plus in instalments", "payments#EMI", "3 parts"),
    ("I forgot my password", "account#Login problems", "Forgot Password"),
    ("where do electronics ship from", "shipping#Warehouses", "Pune"),
    ("what does E-310 mean", "errors#E-310", "pincode"),
    ("cash on delivery refund method", "refunds#Refund method", "NEFT"),
    ("delivery days in a metro city", "shipping#Delivery time", "1 to 2"),
    ("warranty on electronics", "warranty#Electronics warranty", "1 year"),
]


def faithfulness(answer, context):
    """Share of answer words that appear in the retrieved context."""
    if answer.startswith("I don't know"):
        return 1.0                       # refusing is always faithful
    words = [w for w in tokens(answer.split(" [")[0])]
    ctx = set(tokens(context))
    return sum(w in ctx for w in words) / max(1, len(words))


def run(name, search):
    hits = rr = faith = correct = 0
    for q, gold, fact in GOLDEN:
        top = search(q)
        ids = [c["id"] for c in top]
        hits += gold in ids                                  # recall@3
        rr += 1 / (ids.index(gold) + 1) if gold in ids else 0  # MRR
        answer = generate(q, top)
        faith += faithfulness(answer, " ".join(c["text"] for c in top))
        correct += fact.lower() in answer.lower()
    n = len(GOLDEN)
    print(f"{name:15} recall@3 {hits/n:.2f}  MRR {rr/n:.2f}  "
          f"faithful {faith/n:.2f}  correct {correct/n:.2f}")


if __name__ == "__main__":
    chunks = build(section_chunks)
    bm, vec, hy = BM25(chunks), VectorIndex(chunks), Hybrid(chunks)
    run("keyword", lambda q: bm.search(q, 3))
    run("vector", lambda q: vec.search(q, 3))
    run("hybrid", lambda q: hy.search(q, 3))
    run("hybrid+rerank", lambda q: rerank(q, hy.search(q, 10), 3))
    print("unfaithful example:", round(faithfulness(
        "Card refunds are instant and free", chunks[0]["text"]), 2))
