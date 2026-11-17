"""generate.py: stand-in generator. Answers ONLY from the given chunks.

A real app sends the prompt below to an LLM. The stand-in copies the best
matching sentence, so the demo runs offline on any CPU.
"""
import re
from search import embed

PROMPT = """Answer using ONLY the context. Cite sources like [id].
If the context does not have the answer, say "I don't know".
Context:
{context}
Question: {question}"""


def build_prompt(question, chunks):
    context = "\n".join(f"[{c['id']}] {c['text']}" for c in chunks)
    return PROMPT.format(context=context, question=question)


def generate(question, chunks):
    q = embed(question)
    best, best_s = None, 0.0
    for c in chunks:
        sents = re.split(r"(?<=\.)\s+", c["text"].split(": ", 1)[-1])
        for i, sent in enumerate(sents):
            s = sum(1 for m in q if m in embed(sent)) / max(1, len(q))
            if s > best_s:   # keep the best sentence + the one after it
                best, best_s = (" ".join(sents[i:i + 2]), c["id"]), s
    if best_s < 0.34:
        return "I don't know. Please contact support."
    return f"{best[0]} [{best[1]}]"
