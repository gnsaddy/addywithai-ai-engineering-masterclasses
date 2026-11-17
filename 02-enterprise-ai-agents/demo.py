"""End-to-end demo: three employees, one agent. Identity, permission-aware
search, a risky action with human approval, a retry that does NOT pay twice,
and the audit trail."""
import company
from agent import run_agent
from auth import issue_token
from tools import AUDIT


def ask(user, question, approved_by=None):
    answer, trace = run_agent(issue_token(user), question,
                              approved_by=approved_by)
    role = company.USERS[user]["role"]
    note = f"  [approved by {approved_by}]" if approved_by else ""
    print(f"\n{user} ({role}): {question}{note}")
    print("   trace:", " | ".join(trace))
    print("   A:", answer)


ask("asha", "How many leave days do I have left?")
ask("asha", "Show the salary bands for engineer level 2")
ask("ravi", "Refund order A-5001 for Rs 25000")
ask("ravi", "Refund order A-5001 for Rs 25000", approved_by="kiran")
# the app timed out and sent the same request again:
ask("ravi", "Refund order A-5001 for Rs 25000", approved_by="kiran")

print(f"\nrefunds actually sent: {len(company.REFUNDS)}")
print("audit trail:")
for row in AUDIT:
    print(f"   {row['who']:5} {row['tool']:13} {row['status']}")
