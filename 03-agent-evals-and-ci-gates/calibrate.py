"""calibrate.py: before you trust a judge, check it against human labels.

A person labelled 13 real agent runs as pass or fail. We ask each judge the
same question and count how often it agrees. The worst error is a FALSE PASS:
the judge says fine, the human says the agent did something wrong.
"""
import json
from scorers import judge_answer_only, judge_grounded

labels = json.load(open("human_labels.json"))
JUDGES = {
    "answer-only judge": lambda x: judge_answer_only(x["question"], x["answer"]),
    "grounded judge": lambda x: judge_grounded(x["answer"], x["trajectory"]),
}
for name, judge in JUDGES.items():
    agree, false_pass, false_fail = 0, [], []
    for x in labels:
        says = "pass" if judge(x) >= 4 else "fail"   # threshold: 4 out of 5
        if says == x["human"]:
            agree += 1
        elif says == "pass":
            false_pass.append(x["id"])
        else:
            false_fail.append(x["id"])
    print(f"{name:<18} agrees {agree}/{len(labels)} = {agree / len(labels):.0%}"
          f" | false pass {len(false_pass)} | false fail {len(false_fail)}")
    for i in false_pass:
        print(f"   false pass: {i}")
    for i in false_fail:
        print(f"   false fail: {i}")
