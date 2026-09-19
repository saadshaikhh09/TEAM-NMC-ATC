"""Gemini adapter. Owner: Person A.

Different request shape to OpenAI's: contents/parts rather than messages, and
the system prompt goes in system_instruction.

Free tier rate-limits aggressively. When it 429s the router trips the breaker
and skips it for LLM_BREAKER_COOLDOWN seconds — which is exactly the scenario
this chain exists for.
"""


def make(key: str, model: str):
    """Returns fn(system, user, timeout) -> str. Raises on any failure."""
    raise NotImplementedError("A11")
