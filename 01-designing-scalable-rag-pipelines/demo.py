"""demo.py: ask, add a new help page, re-index only that page, ask again."""
import hashlib
from kb import DOCS
from chunking import section_chunks
from search import Hybrid
from rerank import rerank
from generate import generate
from pipeline import RAGPipeline, Cache

seen = {}                                  # doc id -> content hash


def ingest(docs, chunks):
    """Incremental ingestion: only new or changed docs are chunked again."""
    for doc_id, text in docs.items():
        h = hashlib.sha256(text.encode()).hexdigest()
        if seen.get(doc_id) != h:
            chunks = [c for c in chunks if not c["id"].startswith(doc_id + "#")]
            chunks += section_chunks(doc_id, text)
            seen[doc_id] = h
            print(f"  indexed {doc_id}")
    return chunks


chunks = ingest(DOCS, [])
rag = RAGPipeline(Hybrid(chunks), rerank, generate, Cache())
q = "Do you sell gift cards?"
print("A:", rag.ask(q))

DOCS["giftcards"] = """# Gift cards
## Buying gift cards
Yes, we sell QuickCart gift cards from Rs 500 to Rs 10000.
Gift cards are valid for 1 year and cannot be refunded."""
chunks = ingest(DOCS, chunks)              # only the new page is processed
# new index + a fresh cache, so no old "I don't know" is served
rag = RAGPipeline(Hybrid(chunks), rerank, generate, Cache())
print("A:", rag.ask(q))
