"""Permission-aware retrieval: filter by tenant and role INSIDE the search,
and treat document text as data, never as instructions."""
import re
from company import DOCS

STOP = {"the", "a", "an", "for", "to", "is", "of", "and", "my", "i", "how",
        "many", "do", "what", "with", "me"}
INJECTION = re.compile(r"ignore (all|previous|the) (rules|instructions)", re.I)


def visible(doc, claims):
    """Tenant isolation first, then the document's access list."""
    if doc["tenant"] != claims["tenant"]:
        return False
    return "*" in doc["allow"] or claims["role"] in doc["allow"]


def guard(text):
    """Documents can hide instructions. We never follow them: we drop them."""
    if INJECTION.search(text):
        return "[removed: instructions found inside a document]"
    return text


def search_docs(claims, query, k=2):
    words = set(re.findall(r"\w+", query.lower())) - STOP
    hits = []
    for doc in DOCS:
        if not visible(doc, claims):
            continue  # filtered before ranking: the model never sees it
        score = len(words & set(re.findall(r"\w+", doc["text"].lower())))
        if score:
            hits.append((score, doc["id"], guard(doc["text"])))
    return sorted(hits, reverse=True)[:k]


if __name__ == "__main__":
    from auth import issue_token, verify_token
    salary = "salary bands for engineer level 2"
    for user, q in [("asha", salary), ("meera", salary),
                    ("tom", "how many days of paid leave"), ("asha", "vpn tips")]:
        c = verify_token(issue_token(user))
        print(f"{user:5} {c['tenant']:6} {c['role']:15} '{q}'")
        hits = search_docs(c, q)
        for score, doc_id, text in hits:
            print(f"      {doc_id:13} {text[:58]}")
        if not hits:
            print("      (no documents this user may see)")
