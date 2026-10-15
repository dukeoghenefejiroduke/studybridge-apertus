"""Offline tests for StudyBridge's Apertus-compatible client."""

import json
import urllib.error
from unittest.mock import Mock

import pytest

from app.llm_client import ApertusClient
from app.tutor import TutorEngine
from app.retrieval import RetrievalEngine
from app.ingestion import IngestionManager


def make_response(payload):
    response = Mock()
    response.read.return_value = json.dumps(payload).encode("utf-8")
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    return response


def test_from_env_returns_none_without_endpoint(monkeypatch):
    monkeypatch.delenv("LLM_BASE_URL", raising=False)

    assert ApertusClient.from_env() is None


def test_from_env_reads_configuration(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://example.test/v1/")
    monkeypatch.setenv("LLM_NAME", "swiss-ai/apertus-v1.5-8b")
    monkeypatch.setenv("LLM_API_KEY", "test-key")

    client = ApertusClient.from_env()

    assert client is not None
    assert client.base_url == "https://example.test/v1"
    assert client.model == "swiss-ai/apertus-v1.5-8b"
    assert client.api_key == "test-key"


def test_generate_sends_grounded_chat_request(monkeypatch):
    client = ApertusClient(
        base_url="https://example.test/v1",
        model="swiss-ai/apertus-v1.5-8b",
        api_key="test-key",
    )
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["headers"] = request.headers
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return make_response({
            "choices": [{
                "message": {"content": "Grounding uses retrieved evidence. [1]"}
            }]
        })

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    answer = client.generate(
        "What is grounding?",
        [{
            "title": "Study Notes",
            "source": "Course material",
            "content": "Grounding connects answers to retrieved evidence.",
        }],
    )

    assert answer == "Grounding uses retrieved evidence. [1]"
    assert captured["url"] == (
        "https://example.test/v1/chat/completions"
    )
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["body"]["model"] == "swiss-ai/apertus-v1.5-8b"
    assert captured["body"]["temperature"] == 0.2

    messages = captured["body"]["messages"]
    assert "only the supplied study-material context" in messages[0]["content"]
    assert "Grounding connects answers to retrieved evidence." in messages[1]["content"]


def test_generate_rejects_empty_answer(monkeypatch):
    client = ApertusClient("https://example.test/v1", "test-model")

    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *args, **kwargs: make_response({
            "choices": [{"message": {"content": "  "}}]
        }),
    )

    with pytest.raises(RuntimeError, match="empty answer"):
        client.generate("Question?", [])


def test_generate_handles_network_error(monkeypatch):
    client = ApertusClient("https://example.test/v1", "test-model")

    def fail_request(*args, **kwargs):
        raise urllib.error.URLError("offline")

    monkeypatch.setattr("urllib.request.urlopen", fail_request)

    with pytest.raises(RuntimeError, match="inference request failed"):
        client.generate("Question?", [])


def test_generate_rejects_unexpected_response(monkeypatch):
    client = ApertusClient("https://example.test/v1", "test-model")

    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *args, **kwargs: make_response({"unexpected": "format"}),
    )

    with pytest.raises(RuntimeError, match="unexpected response"):
        client.generate("Question?", [])


def test_tutor_engine_auto_enables_with_base_url(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("STUDYBRIDGE_FORCE_LLM_TEST", "1")
    monkeypatch.delenv("STUDYBRIDGE_ENABLE_LLM", raising=False)

    ingestion = IngestionManager()
    retrieval = RetrievalEngine(ingestion)
    tutor = TutorEngine(retrieval)

    client = tutor._get_llm_client()
    assert client is not None
    assert client.base_url == "https://example.test/v1"
