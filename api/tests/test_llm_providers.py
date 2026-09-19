from llm.providers import gemini, openai_compatible


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


def test_openai_compatible_adapter_uses_chat_api(monkeypatch):
    request = {}

    def post(url, **kwargs):
        request.update(url=url, **kwargs)
        return FakeResponse({"choices": [{"message": {"content": "answer"}}]})

    monkeypatch.setattr(openai_compatible.httpx, "post", post, raising=False)

    complete = openai_compatible.make("https://example.test/v1", "secret", "model")
    assert complete("system", "user", 4) == "answer"
    assert request["url"] == "https://example.test/v1/chat/completions"
    assert request["headers"]["Authorization"] == "Bearer secret"
    assert request["timeout"] == 4


def test_gemini_adapter_uses_generate_content_api(monkeypatch):
    request = {}

    def post(url, **kwargs):
        request.update(url=url, **kwargs)
        return FakeResponse(
            {"candidates": [{"content": {"parts": [{"text": "answer"}]}}]}
        )

    monkeypatch.setattr(gemini.httpx, "post", post, raising=False)

    complete = gemini.make("secret", "gemini-test")
    assert complete("system", "user", 4) == "answer"
    assert request["url"].endswith("/models/gemini-test:generateContent")
    assert request["params"] == {"key": "secret"}
    assert request["timeout"] == 4
