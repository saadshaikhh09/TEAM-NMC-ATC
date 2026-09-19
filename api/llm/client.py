"""LLM sidecar. Owner: Person A.

The model has three jobs: extract, explain, draft. It has no route to a
provider adapter and never writes a row. Every call is wrapped with a timeout
and falls back to llm/fallback.py.
"""
raise NotImplementedError("A11")
