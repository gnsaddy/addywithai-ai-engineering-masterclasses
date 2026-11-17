"""chunking.py: fixed-size chunks vs section-aware chunks."""
from kb import DOCS


def fixed_chunks(doc_id, text, size=25, overlap=5):
    """Cut every `size` words, ignoring the document's structure."""
    words = text.split()
    step = size - overlap
    return [{"id": f"{doc_id}#w{i}", "text": " ".join(words[i:i + size])}
            for i in range(0, len(words), step)]


def section_chunks(doc_id, text):
    """One chunk per ## section, with the title path kept as context."""
    title, chunks = "", []
    for block in text.split("\n## "):
        lines = block.strip().split("\n")
        if lines[0].startswith("# "):
            title = lines.pop(0)[2:]
            continue
        head, body = lines[0], " ".join(lines[1:])
        chunks.append({"id": f"{doc_id}#{head}",
                       "text": f"{title} > {head}: {body}"})
    return chunks


def build(chunker):
    return [c for d, t in DOCS.items() for c in chunker(d, t)]


if __name__ == "__main__":
    for name, chunker in [("fixed", fixed_chunks), ("section", section_chunks)]:
        chunks = build(chunker)
        print(f"{name:8} {len(chunks):3} chunks")
        hit = [c for c in chunks if "Card refunds" in c["text"]][0]
        print("   ", hit["text"][:74] + "...")
