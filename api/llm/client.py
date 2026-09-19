"""LLM entrypoint. Owner: Person A.

Builds the chain from LLM_CHAIN and registers each provider with the router.
Skips any provider whose key is empty — an unset xkiro key must not cost a
timeout on every call.

The model has three jobs: extract, explain, draft. It has no route to a
provider adapter, never writes a row, and never picks a flight.

    text = llm.client.ask(system, user, cache_key=...)   # str | None
    if text is None: use llm.fallback

Nothing outside llm/ calls a model API directly.
"""

from llm import cache, router


_configured = False


def ask(system: str, user: str, cache_key: str | None = None) -> str | None:
    """Return cached/model text, or None. Never raises."""
    global _configured

    if cache_key:
        try:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
        except Exception:
            pass

    try:
        if not _configured:
            router.configure()
            _configured = True
        response = router.complete(system, user, cache_key=cache_key)
    except Exception:
        return None

    if response is not None and cache_key:
        try:
            cache.put(cache_key, response)
        except Exception:
            pass
    return response
