"""Who is asking, and what may they do?
A JWT-style signed token (simplified) + RBAC and ABAC checks."""
import base64, hashlib, hmac, json, time
from company import USERS

SECRET = b"demo-only-secret"  # real systems: a key from a vault, rotated


def b64(raw): return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
def unb64(s): return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def sign(body):
    return b64(hmac.new(SECRET, body.encode(), hashlib.sha256).digest())


def issue_token(user, ttl=900, now=None):
    """The identity provider signs who you are. The agent never decides."""
    exp = int((now or time.time()) + ttl)
    claims = {"sub": user, **USERS[user], "exp": exp}
    body = b64(json.dumps(claims).encode())
    return body + "." + sign(body)


def verify_token(token, now=None):
    body, sig = token.split(".")
    if not hmac.compare_digest(sig, sign(body)):
        raise PermissionError("bad signature")
    claims = json.loads(unb64(body))
    if claims["exp"] < (now or time.time()):
        raise PermissionError("token expired")
    return claims


ROLE_TOOLS = {  # RBAC: which tools each role may call
    "engineer": {"search_docs", "leave_balance", "create_ticket"},
    "hr_admin": {"search_docs", "leave_balance", "create_ticket"},
    "finance_manager": {"search_docs", "leave_balance", "create_ticket",
                        "issue_refund"},
}


def can_call(claims, tool, args):
    if tool not in ROLE_TOOLS.get(claims["role"], set()):
        return False, f"role {claims['role']} cannot use {tool}"
    # ABAC: a rule on attributes. Only HR may read someone else's leave.
    other = tool == "leave_balance" and args["user"] != claims["sub"]
    if other and claims["role"] != "hr_admin":
        return False, "you can only read your own leave"
    return True, "ok"


if __name__ == "__main__":
    t = issue_token("asha")
    print("token  ", t[:28] + "...")
    print("verify ", verify_token(t)["role"])
    body, sig = t.split(".")
    fake = json.loads(unb64(body))
    fake["role"] = "hr_admin"
    try:
        verify_token(b64(json.dumps(fake).encode()) + "." + sig)
    except PermissionError as e:
        print("tamper ", e)
    try:
        verify_token(issue_token("asha", ttl=-1))
    except PermissionError as e:
        print("old    ", e)
    c = verify_token(t)
    for tool, args in [("leave_balance", {"user": "asha"}),
                       ("leave_balance", {"user": "ravi"}),
                       ("issue_refund", {"order": "A-1", "amount": 500})]:
        print(f"asha -> {tool}:", can_call(c, tool, args))
