# Learn Agent Evals and CI Gates (hands-on code)

Code for the **AI Engineering: Production Masterclasses** video *Learn Agent Evals and CI Gates*.
It shows how to test an AI agent's **whole trajectory** (which tools it called, in what order, with which
arguments, how many steps, what it cost), not just its final answer, and how to block a bad prompt or
model change in CI before it reaches users.

Everything runs on a normal laptop: **CPU only, Python standard library, no API keys.**
The agent is a stand-in: a small rule-based planner plays the LLM, so results are fast, free and repeatable.
SwiftBasket, its orders and its customers are made up.

## Files

| File | What it does |
|---|---|
| `shop.py` | Fake SwiftBasket systems + 5 tools: `get_order`, `refund_policy`, `issue_refund`, `escalate`, `search_help` |
| `agent.py` | Stand-in support agent. Records the full trajectory, steps, tokens and cost |
| `prompts/v1.json` | The current prompt + config (main branch) |
| `prompts/v1b.json` | A harmless reword (should pass the gate) |
| `prompts/v2.json` | "Make it faster" change (should be blocked) |
| `logs/prod_traces.jsonl` | Sample production logs |
| `make_testset.py` | Turns logs into draft test cases (thumbs-down, new intent, unusual tools, no duplicates) |
| `evalset.json` | 12 reviewed trajectory test cases (7 critical) |
| `scorers.py` | Deterministic trajectory checks + two judge stand-ins |
| `human_labels.json`, `calibrate.py` | Check a judge against human labels before trusting it |
| `run_evals.py` | Runs every case k times, pass^k for critical cases, majority for the rest |
| `gate.py` | Compares candidate vs baseline with thresholds; exit code 1 blocks the merge |
| `workflow-example/agent-evals.yml` | GitHub Actions example that runs the evals + gate on pull requests |
| `demo.py` | End to end: baseline, PR 1 passes, PR 2 is blocked |

GitHub Actions example: workflow-example/agent-evals.yml, copy it to .github/workflows/ in your own repo.

## Run it

```bash
python agent.py v1              # see one trajectory
python make_testset.py          # logs -> draft cases
python run_evals.py v1          # 12 cases x 3 runs
python run_evals.py v2          # the "faster" prompt
python calibrate.py             # judge vs human labels
python demo.py                  # baseline -> PR 1 PASS -> PR 2 FAIL
python gate.py results/baseline.json results/v2.json; echo $?   # 1 = blocked
```

Python 3.9 or newer. `requirements.txt` is empty on purpose.

## What to notice

* v2 gets a **higher** answer-only judge score and is **26% cheaper**, but its trajectory pass rate drops
  from 100% to 42% with 7 critical failures: it sends refunds without looking up the order or the policy.
* The answer-only judge agrees with humans 54% of the time with 4 false passes; the grounded judge
  (claims checked against tool results) agrees 92% with 0 false passes.
* `status-delivered` is flaky (2/3): the stand-in sometimes takes an extra step, like a real model at
  temperature above zero. Critical cases must pass every run; others pass by majority.

## Use it with a real agent

Replace `run_agent()` in `agent.py` with your agent, but keep the same return shape
(`answer`, `trajectory` with `tool`/`args`/`result`, `steps`, `tokens`, `cost_rs`).
Swap the judge stand-ins for an LLM judge prompt with the same rubric, and calibrate it on your own
human labels first.
