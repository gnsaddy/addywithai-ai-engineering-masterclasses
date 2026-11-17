"""advanced.py: an agentic, multi-hop RAG loop (toy planner, offline)."""
import re
from chunking import build, section_chunks
from search import Hybrid
from rerank import rerank
from generate import generate

search = Hybrid(build(section_chunks))


def retrieve(q):
    return rerank(q, search.search(q, 10), 3)


def plan(question):
    """Stand-in for an LLM planner: split 'X for the Y that Z?' in 2 hops."""
    m = re.match(r"(.+) for the (\w+) that (.+)\?", question)
    if not m:
        return [question]
    return [f"which {m[2]} {m[3]}", m[1] + " for {entity}"]


def agent(question, max_steps=3):
    entity, answer = "", ""
    for step, sub in enumerate(plan(question)[:max_steps], start=1):
        sub = sub.format(entity=entity)
        found = retrieve(sub)
        answer = generate(sub, found)
        print(f"  step {step}: {sub!r}\n          -> {answer}")
        names = re.findall(r"QuickCart [A-Z]\w+", found[0]["text"])
        entity = names[0] if names else entity
    return answer


if __name__ == "__main__":
    q = "Can I pay by EMI for the plan that gives free delivery?"
    print("single shot:", generate(q, retrieve(q)))
    print("agentic, multi-hop:")
    agent(q)
