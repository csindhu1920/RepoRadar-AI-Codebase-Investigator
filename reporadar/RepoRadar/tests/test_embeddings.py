
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from reporadar.embeddings import embed_query, embed_texts


def test_embed_texts_returns_one_vector_per_text():
    vectors = embed_texts([
        "Check whether a password is correct",
        "Format a date",
    ])

    assert vectors.shape == (2, 384)


def test_embeddings_are_normalized():
    vectors = embed_texts(["Authenticate a user"])

    norms = np.linalg.norm(vectors, axis=1)

    assert np.allclose(norms, 1.0, atol=1e-5)


def test_similar_meanings_have_higher_similarity():
    vectors = embed_texts([
        "Verify a user's password",
        "Check a user's login credentials",
        "Calculate the weather temperature",
    ])

    similarity_related = float(np.dot(vectors[0], vectors[1]))
    similarity_unrelated = float(np.dot(vectors[0], vectors[2]))

    assert similarity_related > similarity_unrelated


def test_embed_query_returns_one_vector():
    vector = embed_query("Find the login function")

    assert vector.shape == (384,)


def test_embed_query_rejects_empty_input():
    with pytest.raises(ValueError):
        embed_query("   ")


def test_embed_empty_list():
    vectors = embed_texts([])

    assert vectors.shape == (0, 384)
