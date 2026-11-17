"""The agent loop: verify who is asking, let the model pick a tool,
run it safely, repeat, and stop."""
import json, re
from auth import verify_token
from tools import run_tool

VERSION = 2  # v1 raised a ticket for ANY vpn question; the eval caught it


def plan(question, claims, history):
    """LLM stand-in (offline, no API key). A real model returns the same
    shape: a tool call, or a final answer."""
    q = question.lower()
    if history:  # we already have a tool result: answer from it
        tool, r = history[-1]
        fails = VERSION == 1 or "fail" in q
        if tool == "search_docs" and "vpn" in q and len(history) == 1 and fails:
            return ("create_ticket", {"title": "VPN failing: " + question})
        if r["status"] == "waiting for approval":
            return ("final", "Sent for approval. A second finance manager "
                             "must approve it.")
        if r["result"] is None:  # denied or rejected: say so, never guess
            return ("final", "I can't do that: " + r["status"])
        if tool == "search_docs":
            safe = [t for _, _, t in r["result"]
                    if not t.startswith("[removed")]
            return ("final", safe[0] if safe else
                    "I don't know. No document you can see covers this.")
        if tool == "create_ticket":
            ticket = r["result"].split(":")[0]
            return ("final", "Restart the VPN app first. "
                             f"If it still fails: {ticket}.")
        return ("final", r["result"])
    if "leave" in q and "left" in q:
        return ("leave_balance", {"user": claims["sub"]})
    m = re.search(r"refund order (\S+) for rs (\d+)", q)
    if m:
        return ("issue_refund", {"order": m.group(1).upper(),
                                 "amount": int(m.group(2))})
    return ("search_docs", {"query": question})


def run_agent(token, question, max_steps=4, approved_by=None):
    claims = verify_token(token)          # 1. identity comes from the token
    history, trace = [], []
    for step in range(1, max_steps + 1):  # 2. the loop, with a step limit
        action = plan(question, claims, history)
        if action[0] == "final":
            trace.append(f"step {step}: answer")
            return action[1], trace
        tool, args = action               # 3. the model only PROPOSES a call
        key = f"{claims['sub']}:{tool}:{json.dumps(args, sort_keys=True)}"
        r = run_tool(claims, tool, args, approved_by=approved_by, key=key)
        trace.append(f"step {step}: {tool} -> {r['status']}")
        history.append((tool, r))
    return "Stopped: step limit reached.", trace


if __name__ == "__main__":
    from auth import issue_token
    for user, q in [("asha", "How many leave days do I have left?"),
                    ("asha", "My VPN keeps failing with error V-12"),
                    ("asha", "Refund order A-2001 for Rs 500")]:
        answer, trace = run_agent(issue_token(user), q)
        print(f"{user}: {q}")
        for t in trace:
            print("   ", t)
        print("    A:", answer)
