"""Turns a finished plan into prose. Owner: Person A. Off the critical path."""

from llm import cache, client, fallback


def _narrate(plan, purpose: str, system: str, fallback_text: str) -> str:
    key = f"{purpose}:{cache.key_for(plan)}"
    text = client.ask(system, fallback.explanation(plan), cache_key=key)
    if text is None:
        text = fallback_text
        try:
            cache.put(key, text)
        except Exception:
            pass
    return text


def explain(plan) -> str:
    return _narrate(
        plan,
        "explain",
        "Explain only the supplied recovery recommendation. Do not choose or change "
        "an option, and do not imply live airline write access or a confirmed booking.",
        fallback.explanation(plan),
    )


def draft(plan) -> str:
    return _narrate(
        plan,
        "draft",
        "Draft a concise member message using only the supplied recovery facts. Do "
        "not imply live airline write access or a confirmed booking.",
        fallback.member_message(plan),
    )
