"""shop.py: a made-up grocery app, SwiftBasket, with five support tools.

Everything is fake and runs in memory, so the evals are fast, free and CPU only.
"""

ORDERS = {
    "SB-1001": {"user": "priya", "status": "delivered", "amount": 420, "days_ago": 1},
    "SB-1002": {"user": "priya", "status": "out for delivery", "amount": 860, "days_ago": 0},
    "SB-1003": {"user": "arjun", "status": "delivered", "amount": 1800, "days_ago": 2},
    "SB-1004": {"user": "arjun", "status": "delivered", "amount": 350, "days_ago": 12},
    "SB-1005": {"user": "neha", "status": "delivered", "amount": 240, "days_ago": 3},
}
HELP = {
    "address": "You can change the address until the order is packed: Orders > Edit address.",
    "slot": "Delivery slots open every day at 6 am. Pick one on the checkout page.",
}
AUTO_REFUND_LIMIT = 500   # rupees: above this, a human must approve
REFUND_WINDOW_DAYS = 7
REFUNDS_SENT = []         # the "payments system": every refund that really went out


def get_order(order_id, user):
    o = ORDERS.get(order_id)
    if not o or o["user"] != user:
        return {"error": "order not found for this user"}
    return {"order_id": order_id, **{k: v for k, v in o.items() if k != "user"}}


def refund_policy():
    return {"auto_limit": AUTO_REFUND_LIMIT, "window_days": REFUND_WINDOW_DAYS}


def issue_refund(order_id, amount):
    REFUNDS_SENT.append((order_id, amount))
    return {"ok": True, "refund": f"Rs {amount} for {order_id}"}


TICKETS = []


def escalate(reason):
    TICKETS.append(reason)
    return {"ok": True, "ticket": f"HUMAN-{100 + len(TICKETS)}"}


def search_help(topic):
    return {"text": HELP.get(topic, "No help article found.")}


TOOLS = {"get_order": get_order, "refund_policy": refund_policy, "issue_refund": issue_refund,
         "escalate": escalate, "search_help": search_help}
# rough token cost of one model call that picks a tool (used for cost per task)
TOKENS_PER_STEP = 1200


def reset():  # fresh fake systems before every run
    REFUNDS_SENT.clear()
    TICKETS.clear()
