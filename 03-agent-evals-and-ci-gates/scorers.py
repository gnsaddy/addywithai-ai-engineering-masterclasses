"""scorers.py: score a whole trajectory, not just the final answer.

1) Deterministic checks: cheap, exact, run on every change.
2) Judges (stand-ins for an LLM judge): one only reads the answer,
   one also checks the answer's claims against the trajectory.
"""


def in_order(called, expected):
    """True if the expected tools appear in this order (other calls may sit in between)."""
    it = iter(called)
    return all(tool in it for tool in expected)


def first_call(traj, tool):
    return next((s for s in traj if s["tool"] == tool), None)


def check_case(case, run):
    traj, called = run["trajectory"], [s["tool"] for s in run["trajectory"]]
    checks = {
        "tools in order": in_order(called, case["must_call"]),
        "never called": not any(t in called for t in case["never"]),
        "right args": all(
            (c := first_call(traj, tool)) is not None
            and all(c["args"].get(k) == v for k, v in want.items())
            for tool, want in case["args"].items()),
        "step budget": run["steps"] <= case["max_steps"],
        "answer": all(w.lower() in run["answer"].lower() for w in case["answer_has"]),
    }
    return all(checks.values()), checks


# ---------------------------------------------------------------- judges
def judge_answer_only(question, answer):
    """Naive judge: is the reply polite, clear and confident? (1-5) Never looks at tools."""
    score = 3
    score += any(w in answer for w in ("Done", "will", "is "))
    score += "!" in answer or "please" in answer.lower()
    score -= "can't" in answer
    return max(1, min(5, score))


def judge_grounded(answer, traj):
    """Rubric judge: every claim in the answer must be backed by a tool result."""
    tools = [s["tool"] for s in traj]
    if "Refund of" in answer:   # claims money was sent: needs lookup + policy + refund
        return 5 if in_order(tools, ["get_order", "refund_policy", "issue_refund"]) else 1
    if "support person" in answer:
        return 5 if "escalate" in tools else 1
    if answer.startswith("Order "):
        got = first_call(traj, "get_order")
        return 5 if got and got["result"].get("status", "") in answer else 1
    return 4                    # help text or "can't find": nothing risky claimed
