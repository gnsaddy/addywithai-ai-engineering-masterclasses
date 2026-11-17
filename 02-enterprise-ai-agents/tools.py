"""Safe tool calls: schema check, permission check, human approval for risky
actions, idempotency keys (no double refunds) and an audit trail."""
import company
from auth import can_call
from retrieval import search_docs

TOOLS = {  # name -> risk tier, argument schema, backend function
    "search_docs":   {"risk": "low", "args": {"query": str},
                      "fn": search_docs},
    "leave_balance": {"risk": "low", "args": {"user": str},
                      "fn": company.leave_balance},
    "create_ticket": {"risk": "medium", "args": {"title": str},
                      "fn": company.create_ticket},
    "issue_refund":  {"risk": "high", "args": {"order": str, "amount": int},
                      "fn": company.issue_refund},
}
AUDIT, DONE = [], {}
APPROVAL_LIMIT = 10000  # refunds above this need a second person


def record(claims, tool, args, status, result=None):
    AUDIT.append({"who": claims["sub"], "tool": tool, "args": args,
                  "status": status})
    return {"status": status, "result": result}


def run_tool(claims, tool, args, approved_by=None, key=None):
    spec = TOOLS.get(tool)
    if spec is None:
        return record(claims, tool, args, "rejected: unknown tool")
    schema = spec["args"]
    if set(args) != set(schema) or not all(
            isinstance(args[a], t) for a, t in schema.items()):
        return record(claims, tool, args, "rejected: bad arguments")
    ok, why = can_call(claims, tool, args)
    if not ok:
        return record(claims, tool, args, "denied: " + why)
    if spec["risk"] == "high" and args.get("amount", 0) > APPROVAL_LIMIT:
        if not approved_by:
            return record(claims, tool, args, "waiting for approval")
        boss = company.USERS[approved_by]["role"] == "finance_manager"
        if approved_by == claims["sub"] or not boss:
            return record(claims, tool, args, "denied: need another approver")
    writes = spec["risk"] != "low"  # actions need idempotency; reads don't
    if writes and key in DONE:
        return record(claims, tool, args, "duplicate: no second action",
                      DONE[key])
    result = spec["fn"](claims, **args)
    if writes and key:
        DONE[key] = result
    return record(claims, tool, args, "ok", result)


if __name__ == "__main__":
    from auth import issue_token, verify_token
    ravi = verify_token(issue_token("ravi"))
    refund = {"order": "A-1001", "amount": 25000}
    runs = [("bad args", {"order": "A-1001", "amount": "lots"}, None),
            ("no approval", refund, None), ("self approve", refund, "ravi"),
            ("approved", refund, "kiran"), ("retry", refund, "kiran")]
    for label, args, appr in runs:
        r = run_tool(ravi, "issue_refund", args, approved_by=appr,
                     key="ravi:refund:A-1001")
        extra = f" | {r['result']}" if r["result"] else ""
        print(f"{label:12} -> {r['status']}{extra}")
    print("refunds sent:", len(company.REFUNDS), "| audit rows:", len(AUDIT))
