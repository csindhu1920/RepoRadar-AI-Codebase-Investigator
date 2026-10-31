
import json
from io import BytesIO
import sys
from pathlib import Path
from urllib.error import HTTPError

import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

import reporadar.llm as llm_module
from reporadar.llm import generate_answer


class FakeResponse:
    """Simulates an HTTP response from Ollama."""

    def __init__(self, data):
        self.data = json.dumps(data).encode("utf-8")

    def read(self):
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def test_generate_answer_returns_model_response(monkeypatch):
    def fake_urlopen(request, timeout):
        assert request.full_url == llm_module.DEFAULT_API_URL
        assert timeout == 180

        payload = json.loads(request.data.decode("utf-8"))
        assert payload["model"] == "llama3.2:1b"
        assert payload["stream"] is False
        assert "Explain login" in payload["prompt"]

        return FakeResponse({
            "response": "The function returns a welcome message."
        })

    monkeypatch.setattr(llm_module, "urlopen", fake_urlopen)

    answer = generate_answer("Explain login")

    assert answer == "The function returns a welcome message."


def test_generate_answer_rejects_blank_prompt():
    with pytest.raises(ValueError, match="Prompt must not be empty"):
        generate_answer("   ")


def test_generate_answer_rejects_blank_model():
    with pytest.raises(ValueError, match="Model name must not be empty"):
        generate_answer("Explain login", model="   ")


def test_generate_answer_rejects_empty_model_response(monkeypatch):
    def fake_urlopen(request, timeout):
        return FakeResponse({"response": "   "})

    monkeypatch.setattr(llm_module, "urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match="empty answer"):
        generate_answer("Explain login")


def test_generate_answer_includes_ollama_http_error_detail(monkeypatch):
    def fake_urlopen(request, timeout):
        raise HTTPError(
            request.full_url,
            500,
            "Internal Server Error",
            {},
            BytesIO(b'{"error":"model requires more memory"}'),
        )

    monkeypatch.setattr(llm_module, "urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match="model requires more memory"):
        generate_answer("Explain login")
