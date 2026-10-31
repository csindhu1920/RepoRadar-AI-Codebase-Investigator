
import sys
from pathlib import Path

import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

import reporadar.rag as rag_module
from reporadar.rag import (
    retrieve_context,
    format_context,
    build_rag_prompt,
)


def test_retrieve_context_calls_hybrid_search(monkeypatch):
    expected = [
        {
            "path": "auth.py",
            "start_line": 1,
            "end_line": 2,
            "text": "def login(username): pass",
            "source_types": ["semantic"],
        }
    ]

    def fake_hybrid_search(index, query, top_k):
        assert query == "Where is login defined?"
        assert top_k == 3
        return expected

    monkeypatch.setattr(
        rag_module,
        "hybrid_search",
        fake_hybrid_search,
    )

    results = retrieve_context(
        {},
        "Where is login defined?",
        top_k=3,
    )

    assert results == expected


def test_retrieve_context_returns_empty_for_blank_question():
    assert retrieve_context({}, "   ") == []


def test_format_context_includes_file_lines_and_code():
    results = [
        {
            "path": "auth.py",
            "start_line": 1,
            "end_line": 2,
            "text": (
                "def login(username):\n"
                "    return username"
            ),
            "source_types": ["semantic", "keyword"],
        }
    ]

    context = format_context(results)

    assert "File: auth.py" in context
    assert "Lines: 1-2" in context
    assert "def login(username):" in context
    assert "semantic, keyword" in context


def test_format_context_handles_no_results():
    assert format_context([]) == (
        "No relevant code was retrieved."
    )


def test_prompt_contains_question_and_context():
    question = "What does login do?"
    context = "File: auth.py\nLines: 1-2\nCode: ..."

    prompt = build_rag_prompt(question, context)

    assert question in prompt
    assert context in prompt
    assert "Do not invent functions" in prompt
    assert "insufficient" in prompt.lower()


def test_prompt_rejects_blank_question():
    with pytest.raises(ValueError):
        build_rag_prompt("   ", "Some code")
