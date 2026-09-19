"""Response cache keyed by plan content. Owner: Person A.

This is worth more than the fallback chain.

You will rehearse the demo roughly thirty times against the same seeded plan.
Without a cache that is thirty identical LLM calls — free-tier rate limits,
thirty chances to be slow on stage, and thirty different wordings so you can
never rehearse the same pitch twice.

With it: one call, then instant replay. The demo becomes deterministic, which
is the same reason providers/mock.py has no randomness.

Key on a hash of the inputs that actually change the answer — chosen option,
rejections, hotel delta — not on a timestamp.

Persist in Postgres, not memory. `make reset` should NOT clear it: you want the
cache to survive the thirty resets you are about to do.
"""


def key_for(plan) -> str:
    raise NotImplementedError("A11")


def get(key: str) -> str | None:
    raise NotImplementedError("A11")


def put(key: str, value: str) -> None:
    raise NotImplementedError("A11")
