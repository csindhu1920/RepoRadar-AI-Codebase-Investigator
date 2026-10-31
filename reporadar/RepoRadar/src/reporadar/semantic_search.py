import numpy as np

from reporadar.chunker import chunk_index
from reporadar.embeddings import embed_query, embed_texts


def semantic_search(index, query, top_k=5, chunk_size=30, overlap=5):
    """Return the most semantically similar source chunks."""
    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    chunks = chunk_index(
        index,
        chunk_size=chunk_size,
        overlap=overlap,
    )
    if not chunks:
        return []

    chunk_vectors = embed_texts([chunk["text"] for chunk in chunks])
    query_vector = embed_query(query)
    scores = np.dot(chunk_vectors, query_vector)

    results = [
        {**chunk, "score": float(score)}
        for chunk, score in zip(chunks, scores)
    ]
    results.sort(
        key=lambda result: (
            -result["score"],
            result["path"],
            result["start_line"],
        )
    )

    return results[:top_k]
