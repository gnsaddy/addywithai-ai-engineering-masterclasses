"""make_testset.py: turn real production logs into DRAFT trajectory test cases.

Rules: keep every thumbs-down chat, keep one chat per intent, keep chats whose
tool path looks unusual, and drop near-duplicates. A person then reviews each
draft and writes the expected trajectory into evalset.json.
"""
import json, re
from agent import read_request

logs = [json.loads(line) for line in open("logs/prod_traces.jsonl")]
norm = lambda q: re.sub(r"[^a-z0-9 -]", "", q.lower()).strip()

seen, by_intent, drafts = set(), {}, []
for log in logs:
    key = norm(log["question"])
    if key in seen:                                   # near-duplicate: skip
        continue
    seen.add(key)
    intent = read_request(log["question"])[0]
    usual = by_intent.setdefault(intent, log["tools"])
    why = ("thumbs-down" if log["feedback"] == "down" else
           "new intent" if usual is log["tools"] else
           "unusual tools" if log["tools"] != usual else None)
    if why:
        drafts.append({"from": log["id"], "why": why, "intent": intent,
                       "user": log["user"], "question": log["question"],
                       "logged_tools": log["tools"], "expect": "TODO: reviewer"})

json.dump(drafts, open("results/evalset_draft.json", "w"), indent=1)
print(f"{len(logs)} logs -> {len(drafts)} draft cases")
for d in drafts:
    print(f"  {d['from']}  {d['why']:<13} {d['intent']:<9} {d['question'][:44]}")
