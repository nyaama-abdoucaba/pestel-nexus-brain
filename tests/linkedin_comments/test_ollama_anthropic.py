from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.linkedin_comments.ollama_anthropic import AnthropicOllamaClient, LlmResponseError, OllamaUnavailable


SCHEMA = {
    "type": "object",
    "properties": {"decision": {"type": "string"}},
    "required": ["decision"],
}


class FakeResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_healthcheck_uses_ollama_tags(monkeypatch):
    called = {}

    def fake_urlopen(url, timeout):
        called.update(url=url, timeout=timeout)
        return FakeResponse()

    monkeypatch.setattr("app.linkedin_comments.ollama_anthropic.urlopen", fake_urlopen)
    AnthropicOllamaClient("http://localhost:11434", "gemma4:31b-cloud", timeout_seconds=7).healthcheck()
    assert called == {"url": "http://localhost:11434/api/tags", "timeout": 7}


def test_complete_extracts_text_and_usage():
    message = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="{\"decision\":\"skip\"}")],
        usage=SimpleNamespace(input_tokens=12, output_tokens=34),
    )
    calls = []
    client = SimpleNamespace(messages=SimpleNamespace(create=lambda **kwargs: calls.append(kwargs) or message))

    completion = AnthropicOllamaClient("http://localhost:11434", "gemma4:31b-cloud", client=client).complete(
        system="system", user="user", max_tokens=100, temperature=0.1, schema=SCHEMA
    )

    assert completion.text == '{"decision":"skip"}'
    assert completion.output_tokens == 34
    assert calls[0]["model"] == "gemma4:31b-cloud"


def test_complete_rejects_empty_text():
    message = SimpleNamespace(content=[SimpleNamespace(type="tool_use")], usage=None)
    client = SimpleNamespace(messages=SimpleNamespace(create=lambda **kwargs: message))
    adapter = AnthropicOllamaClient("http://localhost:11434", "gemma4:31b-cloud", client=client)

    with pytest.raises(LlmResponseError):
        adapter.complete(system="system", user="user", max_tokens=100, temperature=0.1, schema=SCHEMA)
