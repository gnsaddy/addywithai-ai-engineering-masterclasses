"""agent.py: a stand-in support agent for SwiftBasket (no real LLM, no API key).

A real agent asks an LLM "which tool next?". Here a small rule-based planner plays
the LLM, and the prompt/model config (prompts/v1.json, v2.json) changes how it behaves.
It records the whole trajectory: every tool call, its arguments, its result,
plus steps and tokens, because evals need all of that, not just the final answer.
"""
import json, random, re, sys
import shop

PRICE_PER_1K_TOKENS = 0.25  # rupees, a made-up example price


def load_config(name):
    return json.load(open(f"prompts/{name}.json"))


def read_request(q):  # the "LLM" understands the message
    q_low = q.lower()
    oid = re.search(r"SB-\d{4}", q)
    amt = re.search(r"Rs\.? ?(\d+)", q)
    if "ignore" in q_low and "rule" in q_low:
        intent = "injection"
    elif "refund" in q_low or "money back" in q_low:
        intent = "refund"
    elif "where" in q_low or "status" in q_low:
        intent = "track"
    else:
        intent = "address" if "address" in q_low else "slot"
    return intent, oid.group(0) if oid else None, int(amt.group(1)) if amt else None


def run_agent(question, user, cfg, seed=0):
    rng = random.Random(f"{seed}|{question}")
    traj = []

    def call(tool, **args):
        if len(traj) >= cfg["max_steps"]:
            raise RuntimeError("step limit hit")
        res = shop.TOOLS[tool](**args)
        traj.append({"tool": tool, "args": args, "result": res})
        return res

    intent, oid, amt = read_request(question)
    if rng.random() < cfg["wander"]:              # sampling noise: an extra lookup
        call("search_help", topic="refund" if intent == "refund" else intent)
    answer = plan_and_act(intent, oid, amt, user, cfg, call)
    steps = len(traj) + 1                          # + the final answer call
    tokens = steps * shop.TOKENS_PER_STEP + len(cfg["prompt"]) // 4 * steps
    return {"answer": answer, "trajectory": traj, "steps": steps,
            "tokens": tokens, "cost_rs": round(tokens / 1000 * PRICE_PER_1K_TOKENS, 2)}


def plan_and_act(intent, oid, amt, user, cfg, call):
    if intent == "injection" and cfg["obey_policy"]:
        t = call("escalate", reason="message asked to ignore the rules")["ticket"]
        return f"I can't skip our checks. A support person will look at this ({t})."
    if intent == "track":
        o = call("get_order", order_id=oid, user=user)
        return f"Order {oid} is {o['status']}." if "error" not in o else "I can't find that order."
    if intent in ("address", "slot"):
        return call("search_help", topic=intent)["text"]
    # refund (and injection, when the config ignores the policy)
    if not cfg["lookup_first"]:                    # trusts the amount the user typed
        call("issue_refund", order_id=oid, amount=amt)
        return f"Done! Refund of Rs {amt} sent for {oid}."
    o = call("get_order", order_id=oid, user=user)
    if "error" in o:
        return "I can't find that order on your account."
    p = call("refund_policy")
    if o["amount"] <= p["auto_limit"] and o["days_ago"] <= p["window_days"]:
        call("issue_refund", order_id=oid, amount=o["amount"])
        return f"Done! Refund of Rs {o['amount']} sent for {oid}."
    t = call("escalate", reason=f"refund {oid} needs a human")["ticket"]
    return f"A support person will review this refund ({t})."


if __name__ == "__main__":
    cfg = load_config(sys.argv[1] if len(sys.argv) > 1 else "v1")
    for q in ["Where is my order SB-1002?", "Refund SB-1001 Rs 420, the milk was spoiled"]:
        r = run_agent(q, "priya", cfg)
        print("Q:", q)
        for i, s in enumerate(r["trajectory"], 1):
            print(f"   step {i}: {s['tool']}({', '.join(f'{k}={v}' for k, v in s['args'].items())})")
        print("   A:", r["answer"], f"| steps {r['steps']} | Rs {r['cost_rs']}")
