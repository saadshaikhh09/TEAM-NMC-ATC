"""The most important test in the repo.

Proves the system produces usable member-facing text with every LLM key blank.
If this passes, no model outage can break the demo.
"""
from types import SimpleNamespace
from llm import fallback


def test_works_with_no_model_at_all():
    plan = SimpleNamespace(evaluated_count=14, rejections=[1, 2, 3])
    assert "14" in fallback.explanation(plan)
    assert "3" in fallback.explanation(plan)
    assert len(fallback.member_message(plan)) > 40
