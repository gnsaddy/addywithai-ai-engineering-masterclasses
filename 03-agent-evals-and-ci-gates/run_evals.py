"""run_evals.py: run every trajectory test case k times and save the scores.

Usage: python run_evals.py <prompt config> [--repeats 3] [--out results/x.json]
Agents are not deterministic, so each case runs k times:
critical cases must pass every run (pass^k), the rest need a majority.
"""
import argparse, json
import shop
from agent import load_config, run_agent
from scorers import check_case, judge_answer_only, judge_grounded


def evaluate(cfg_name, repeats=3, quiet=False):
    cfg, cases = load_config(cfg_name), json.load(open("evalset.json"))
    rows, tokens = [], 0
    for case in cases:
        passes, runs = 0, []
        for seed in range(repeats):
            shop.reset()
            run = run_agent(case["question"], case["user"], cfg, seed)
            ok, checks = check_case(case, run)
            passes += ok
            tokens += run["tokens"]
            runs.append({"ok": ok, "failed": [k for k, v in checks.items() if not v], **run})
        need = repeats if case["critical"] else repeats // 2 + 1
        status = "pass" if passes >= need else "fail"
        flaky = 0 < passes < repeats
        r0 = runs[0]
        rows.append({"id": case["id"], "critical": case["critical"], "passes": passes,
                     "status": status, "flaky": flaky,
                     "failed": sorted({f for r in runs for f in r["failed"]}),
                     "steps": sum(r["steps"] for r in runs) / repeats,
                     "cost_rs": sum(r["cost_rs"] for r in runs) / repeats,
                     "answer_judge": judge_answer_only(case["question"], r0["answer"]),
                     "grounded_judge": judge_grounded(r0["answer"], r0["trajectory"]),
                     "tools": [s["tool"] for s in r0["trajectory"]]})
    n = len(rows)
    summary = {"config": cfg_name, "repeats": repeats, "cases": n,
               "pass_rate": round(sum(r["status"] == "pass" for r in rows) / n, 3),
               "critical_failures": [r["id"] for r in rows if r["critical"] and r["status"] == "fail"],
               "flaky": [r["id"] for r in rows if r["flaky"]],
               "avg_steps": round(sum(r["steps"] for r in rows) / n, 2),
               "avg_cost_rs": round(sum(r["cost_rs"] for r in rows) / n, 2),
               "answer_judge": round(sum(r["answer_judge"] for r in rows) / n, 2),
               "grounded_judge": round(sum(r["grounded_judge"] for r in rows) / n, 2),
               "eval_tokens": tokens, "rows": rows}
    if not quiet:
        report(summary)
    return summary


def report(s):
    print(f"--- {s['config']}: {s['cases']} cases x {s['repeats']} runs")
    for r in s["rows"]:
        mark = "PASS" if r["status"] == "pass" else "FAIL"
        extra = " (flaky)" if r["flaky"] else ""
        why = "" if not r["failed"] else "  <- " + ", ".join(r["failed"])
        print(f"{mark}  {r['id']:<18} {r['passes']}/{s['repeats']}{extra}{why}")
    print(f"pass rate {s['pass_rate']:.0%} | critical fails {len(s['critical_failures'])} | "
          f"avg steps {s['avg_steps']} | Rs {s['avg_cost_rs']}/task | eval tokens {s['eval_tokens']:,}")
    print(f"answer-only judge {s['answer_judge']}/5 | grounded judge {s['grounded_judge']}/5")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--out")
    a = ap.parse_args()
    s = evaluate(a.config, a.repeats)
    json.dump(s, open(a.out or f"results/{a.config}.json", "w"), indent=1)
