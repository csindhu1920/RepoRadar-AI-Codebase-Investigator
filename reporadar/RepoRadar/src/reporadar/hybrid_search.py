
from reporadar.search import search_index
from reporadar.semantic_search import semantic_search


def hybrid_search(
    index,
    query,
    top_k=5,
    chunk_size=30,
    overlap=5,
    rrf_k=60,
):
    """
    Combine keyword and semantic search using
    Reciprocal Rank Fusion (RRF).
    """
    if not query or not query.strip():
        return []

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    if rrf_k < 1:
        raise ValueError("rrf_k must be at least 1")

    # Step 1: Run both retrieval methods.
    keyword_results = search_index(
        index, query, top_k=top_k
    )

    semantic_results = semantic_search(
        index,
        query,
        top_k=top_k,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    # Each result uses a shared structure.
    combined = []

    def add_rrf_score(result, rank, source):
        result["hybrid_score"] += 1.0 / (rrf_k + rank)

        if source not in result["source_types"]:
            result["source_types"].append(source)

    # Step 2: Add semantic results first.
    for rank, item in enumerate(semantic_results, start=1):
        result = {
            "path": item["path"],
            "start_line": item["start_line"],
            "end_line": item["end_line"],
            "text": item["text"],
            "keyword_score": None,
            "semantic_score": item.get("score"),
            "hybrid_score": 0.0,
            "matched_terms": [],
            "source_types": [],
        }

        add_rrf_score(result, rank, "semantic")
        combined.append(result)

    # Step 3: Add keyword results.
    for rank, item in enumerate(keyword_results, start=1):
        line = item.get("line_number", 1)
        path = item["path"]

        # Prefer merging a keyword hit into a semantic
        # chunk when the matching line lies inside it.
        existing = next(
            (
                result
                for result in combined
                if result["path"] == path
                and result["start_line"] <= line
                <= result["end_line"]
            ),
            None,
        )

        if existing is None:
            # No semantic chunk contains this line.
            # Keep the keyword result as its own result.
            existing = {
                "path": path,
                "start_line": line,
                "end_line": line,
                "text": item.get("snippet", ""),
                "keyword_score": item.get("score"),
                "semantic_score": None,
                "hybrid_score": 0.0,
                "matched_terms": [],
                "source_types": [],
            }
            combined.append(existing)
        else:
            existing["keyword_score"] = item.get("score")

            # Keep the semantic chunk's full text as
            # the main evidence snippet.
            if not existing["text"]:
                existing["text"] = item.get("snippet", "")

        for term in item.get("matched_terms", []):
            if term not in existing["matched_terms"]:
                existing["matched_terms"].append(term)

        add_rrf_score(existing, rank, "keyword")

    # Step 4: Rank by the combined RRF score.
    combined.sort(
        key=lambda result: result["hybrid_score"],
        reverse=True,
    )

    # Step 5: Return only the requested number.
    return combined[:top_k]
