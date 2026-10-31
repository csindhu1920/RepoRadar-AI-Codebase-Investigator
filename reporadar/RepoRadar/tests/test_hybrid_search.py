
import sys
from pathlib import Path

import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

import reporadar.hybrid_search as hybrid_module
from reporadar.hybrid_search import hybrid_search


def test_merges_keyword_hit_into_semantic_chunk(monkeypatch):
    monkeypatch.setattr(
        hybrid_module,
        "search_index",
        lambda index, query, top_k: [
            {
                "path": "auth.py",
                "line_number": 15,
                "score": 4,
                "matched_terms": ["password"],
                "snippet": "check_password(password)",
            }
        ],
    )

    monkeypatch.setattr(
        hybrid_module,
        "semantic_search",
        lambda index, query, top_k, chunk_size, overlap: [
            {
                "path": "auth.py",
                "start_line": 10,
                "end_line": 20,
                "text": "def verify_password(...): ...",
                "score": 0.8,
                "chunk_id": "auth.py:10-20",
            }
        ],
    )

    results = hybrid_search({}, "validate password")

    assert len(results) == 1

    result = results[0]
    assert result["path"] == "auth.py"
    assert result["start_line"] == 10
    assert result["end_line"] == 20
    assert result["keyword_score"] == 4
    assert result["semantic_score"] == 0.8
    assert set(result["source_types"]) == {
        "keyword",
        "semantic",
    }
    assert result["matched_terms"] == ["password"]
    assert result["hybrid_score"] == pytest.approx(2 / 61)


def test_keyword_only_result_is_preserved(monkeypatch):
    monkeypatch.setattr(
        hybrid_module,
        "search_index",
        lambda index, query, top_k: [
            {
                "path": "config.py",
                "line_number": 7,
                "score": 2,
                "matched_terms": ["DATABASE_URL"],
                "snippet": "DATABASE_URL = '...'",
            }
        ],
    )

    monkeypatch.setattr(
        hybrid_module,
        "semantic_search",
        lambda index, query, top_k, chunk_size, overlap: [],
    )

    results = hybrid_search({}, "DATABASE_URL")

    assert len(results) == 1
    assert results[0]["path"] == "config.py"
    assert results[0]["start_line"] == 7
    assert results[0]["source_types"] == ["keyword"]
    assert results[0]["hybrid_score"] == pytest.approx(1 / 61)


def test_empty_query_returns_no_results():
    assert hybrid_search({}, "   ") == []


def test_invalid_top_k_raises_error():
    with pytest.raises(ValueError):
        hybrid_search({}, "password", top_k=0)


def test_invalid_rrf_k_raises_error():
    with pytest.raises(ValueError):
        hybrid_search({}, "password", rrf_k=0)


def test_top_k_limits_final_results(monkeypatch):
    monkeypatch.setattr(
        hybrid_module,
        "search_index",
        lambda index, query, top_k: [],
    )

    monkeypatch.setattr(
        hybrid_module,
        "semantic_search",
        lambda index, query, top_k, chunk_size, overlap: [
            {
                "path": f"file{i}.py",
                "start_line": 1,
                "end_line": 5,
                "text": f"example {i}",
                "score": 0.9 - i * 0.1,
            }
            for i in range(3)
        ],
    )

    results = hybrid_search({}, "example", top_k=1)

    assert len(results) == 1
    assert results[0]["path"] == "file0.py"
