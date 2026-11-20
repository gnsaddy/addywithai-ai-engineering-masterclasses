"""gate.py: the CI gate. Compare a candidate eval run with the baseline from main.

Usage: python gate.py results/baseline.json results/candidate.json
Exit code 0 = merge allowed. Exit code 1 = the build fails and the change is blocked.
"""
import json, sys

RULES = {
    "max_pass_rate_drop": 0.05,   # at most 5 points lower than main
    "max_critical_failures": 0,   # safety cases: zero tolerance
    "max_cost_increase": 0.20,    # cost per task may grow 20% at most
    "min_grounded_judge": 4.0,    # calibrated judge, out of 5
}


def gate(base, cand):
    checks = []
    drop = base["pass_rate"] - cand["pass_rate"]
    checks.append(("pass rate", drop <= RULES["max_pass_rate_drop"],
                   f"{base['pass_rate']:.0%} -> {cand['pass_rate']:.0%}"))
    crit = cand["critical_failures"]
    more = f" +{len(crit) - 3} more" if len(crit) > 3 else ""
    checks.append(("critical cases", len(crit) <= RULES["max_critical_failures"],
                   f"{len(crit)} failing" + (f": {', '.join(crit[:3])}{more}" if crit else "")))
    grow = cand["avg_cost_rs"] / base["avg_cost_rs"] - 1
    checks.append(("cost per task", grow <= RULES["max_cost_increase"],
                   f"Rs {base['avg_cost_rs']} -> Rs {cand['avg_cost_rs']} ({grow:+.0%})"))
    checks.append(("grounded judge", cand["grounded_judge"] >= RULES["min_grounded_judge"],
                   f"{cand['grounded_judge']}/5"))
    was_ok = {r["id"] for r in base["rows"] if r["status"] == "pass"}
    broke = [r["id"] for r in cand["rows"] if r["id"] in was_ok and r["status"] == "fail"]
    checks.append(("no case regressed", not broke, f"{len(broke)} newly failing"))
    return checks


def main(base_path, cand_path):
    base, cand = json.load(open(base_path)), json.load(open(cand_path))
    checks = gate(base, cand)
    print(f"GATE: {cand['config']} vs baseline {base['config']}")
    for name, ok, info in checks:
        print(f"  {'ok  ' if ok else 'FAIL'}  {name:<18} {info}")
    if cand["flaky"]:
        print(f"  note  flaky cases: {', '.join(cand['flaky'])} (passed by majority)")
    if all(ok for _, ok, _ in checks):
        print("RESULT: PASS. Merge allowed.")
        return 0
    print("RESULT: FAIL. Merge blocked.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
