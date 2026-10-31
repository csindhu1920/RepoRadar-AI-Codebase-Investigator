from functools import lru_cache

from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model():
    """
    Load the embedding model once and reuse it.

    The first load may download the model if it isn't cached.
    """
    return SentenceTransformer(MODEL_NAME)


def embed_texts(texts):
    """
    Convert a list of texts into numerical embedding vectors.

    Returns a NumPy array with one vector per input text.
    """
    if not texts:
        model = get_embedding_model()
        return model.encode([]).reshape(
            0, model.get_embedding_dimension()
        )

    return get_embedding_model().encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )


def embed_query(query):
    """Convert a single search query into an embedding vector."""
    if not query or not query.strip():
        raise ValueError("Query must not be empty")

    return embed_texts([query])[0]
