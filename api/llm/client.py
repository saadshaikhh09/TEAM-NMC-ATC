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
raise NotImplementedError("A11")
