"""Generic adapter for anything speaking OpenAI's chat API. Owner: Person A.

    POST {base}/chat/completions
    Authorization: Bearer {key}
    {"model": ..., "messages": [{"role": "system"|"user", "content": ...}]}

Covers OpenRouter, and very likely xkiro — verify at hour 0. Most newer
providers are OpenAI-compatible, which is why this adapter exists rather than
one file per vendor.

If xkiro is NOT compatible, write a sibling module here and register it in
router.py. Timebox that to 20 minutes. Two working providers is enough.
"""


def make(base: str, key: str, model: str):
    """Returns fn(system, user, timeout) -> str. Raises on any failure —
    the router catches and moves on."""
    raise NotImplementedError("A11")
