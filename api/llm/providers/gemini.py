"""Gemini adapter. Owner: Person A.

Different request shape to OpenAI's: contents/parts rather than messages, and
the system prompt goes in system_instruction.

Free tier rate-limits aggressively. When it 429s the router trips the breaker
and skips it for LLM_BREAKER_COOLDOWN seconds — which is exactly the scenario
this chain exists for.
"""

import httpx


def make(key: str, model: str):
    """Returns fn(system, user, timeout) -> str. Raises on any failure."""
    def complete(system: str, user: str, timeout: float) -> str:
        response = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            params={"key": key},
            json={
                "system_instruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": user}]}],
            },
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

    return complete
