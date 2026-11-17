"""When a tool's API fails: retries with backoff, a circuit breaker and a
dead-letter queue. Waits are recorded, not slept, so the demo is instant."""
import random

random.seed(7)
WAITS, DLQ = [], []


class FlakyAPI:
    """A payments API that times out `fail` times, then works."""
    def __init__(self, fail): self.fail, self.calls = fail, 0

    def __call__(self, job):
        self.calls += 1
        if self.calls <= self.fail:
            raise TimeoutError("payments API timed out after 2 s")
        return f"{job} done"


def with_retry(fn, job, tries=4, base=0.5):
    for attempt in range(1, tries + 1):
        try:
            return fn(job), attempt
        except TimeoutError:
            if attempt == tries:
                raise
            wait = base * 2 ** (attempt - 1)      # backoff: 0.5, 1, 2 s
            WAITS.append(round(wait + random.uniform(0, 0.1), 2))  # + jitter


class Breaker:
    """After `limit` failures in a row, stop calling for a while:
    fail fast instead of piling up."""
    def __init__(self, limit=3): self.limit, self.fails = limit, 0

    def call(self, fn, job):
        if self.fails >= self.limit:
            raise RuntimeError("circuit open: skipped, try later")
        try:
            out = fn(job); self.fails = 0; return out
        except TimeoutError:
            self.fails += 1; raise


def process(job, fn):
    try:
        return with_retry(fn, job)
    except Exception as e:
        DLQ.append({"job": job, "error": str(e)})  # park it for later
        return None, "dead-letter queue"


if __name__ == "__main__":
    print("refund-1:", process("refund-1", FlakyAPI(fail=2)), "waits", WAITS)
    WAITS.clear()
    print("refund-2:", process("refund-2", FlakyAPI(fail=9)), "waits", WAITS)
    print("DLQ:", DLQ)
    b, api = Breaker(limit=3), FlakyAPI(fail=99)
    for i in range(1, 6):
        try:
            b.call(api, f"call-{i}")
        except Exception as e:
            print(f"call {i}: {e}")
    print("API calls actually made:", api.calls)
