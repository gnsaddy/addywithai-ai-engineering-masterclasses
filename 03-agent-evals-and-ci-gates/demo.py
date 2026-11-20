"""demo.py: the whole flow, like CI would run it on two pull requests.

1) main branch: run the evals on v1 and save it as the baseline.
2) PR 1 "reword the prompt" (v1b): evals + gate -> PASS.
3) PR 2 "make it faster" (v2): evals + gate -> FAIL, merge blocked.
"""
import json
from run_evals import evaluate
from gate import main as gate_main


def save(summary, path):
    json.dump(summary, open(path, "w"), indent=1)


print("== main branch: baseline ==")
base = evaluate("v1", repeats=3, quiet=True)
save(base, "results/baseline.json")
print(f"v1 pass rate {base['pass_rate']:.0%}, critical fails {len(base['critical_failures'])}, "
      f"Rs {base['avg_cost_rs']}/task -> saved results/baseline.json")

for pr, cfg in [("PR 1: reword the prompt", "v1b"), ("PR 2: make it faster", "v2")]:
    print(f"\n== {pr} ({cfg}) ==")
    cand = evaluate(cfg, repeats=3, quiet=True)
    save(cand, f"results/{cfg}.json")
    print(f"answer-only judge says {cand['answer_judge']}/5 (baseline {base['answer_judge']}/5)")
    code = gate_main("results/baseline.json", f"results/{cfg}.json")
    print(f"exit code {code}")

v2 = json.load(open("results/v2.json"))
bad = next(r for r in v2["rows"] if r["id"] == "refund-over-limit")
print("\nwhy PR 2 failed, one trajectory (refund-over-limit, Rs 1800):")
print("   expected: get_order -> refund_policy -> escalate")
print("   got:      " + " -> ".join(bad["tools"]) + "   (money sent, no checks)")
