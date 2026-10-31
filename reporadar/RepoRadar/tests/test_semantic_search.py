import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from reporadar import semantic_search as semantic_search_module
from reporadar.semantic_search import semantic_search


def test_ranks_chunks_by_similarity(monkeypatch):
    monkeypatch.setattr(
        semantic_search_module,
        "embed_texts",
        lambda texts: np.array([[0.0, 1.0], [1.0, 0.0]]),
    )
    monkeypatch.setattr(
        semantic_search_module,
        "embed_query",
        lambda query: np.array([1.0, 0.0]),
    )
    index = {
        "files": [
            {"path": "a.py", "source": "less relevant"},
            {"path": "b.py", "source": "most relevant"},
        ]
    }

    results = semantic_search(index, "query")

    assert [result["path"] for result in results] == ["b.py", "a.py"]
    assert [result["score"] for result in results] == [1.0, 0.0]


def test_empty_index_returns_no_results():
    assert semantic_search({"files": []}, "query") == []


def test_invalid_top_k_raises_error():
    with pytest.raises(ValueError):
        semantic_search({"files": []}, "query", top_k=0)
