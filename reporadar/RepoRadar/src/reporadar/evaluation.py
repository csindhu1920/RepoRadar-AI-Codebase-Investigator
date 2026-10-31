from collections.abc import Callable, Iterable, Mapping


def evaluate_retrieval(
    index: dict,
    cases: Iterable[Mapping],
    search_fn: Callable,
    top_k: int = 5,
) -> dict:
    """
    Evaluate retrieval against manually verified expected file paths.

    Each case must contain:
        question: A retrieval question.
        expected_paths: A list of files considered relevant.

    search_fn must accept:
        search_fn(index, question, top_k=top_k)

    Returns aggregate Hit Rate@K, Recall@K, MRR, and per-question results.
    """
    if not isinstance(index, dict):
        raise ValueError("Index must be a dictionary")

    if not callable(search_fn):
        raise ValueError("search_fn must be callable")

    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
        raise ValueError("top_k must be a positive integer")

    cases = list(cases)

    if not cases:
        raise ValueError("At least one evaluation case is required")

    case_results = []

    for number, case in enumerate(cases, start=1):
        if not isinstance(case, Mapping):
            raise ValueError(f"Evaluation case {number} must be a mapping")

        question = case.get("question")
        expected_paths = case.get("expected_paths")

        if not isinstance(question, str) or not question.strip():
            raise ValueError(
                f"Evaluation case {number} needs a non-empty question"
            )

        if not isinstance(expected_paths, (list, tuple, set)):
            raise ValueError(
                f"Evaluation case {number} needs expected_paths as a list, "
                "tuple, or set"
            )

        expected = {
            path.replace("\\", "/")
            for path in expected_paths
            if isinstance(path, str) and path.strip()
        }

        if not expected:
            raise ValueError(
                f"Evaluation case {number} needs at least one valid "
                "expected path"
            )

        results = search_fn(index, question, top_k=top_k)

        if results is None:
            results = []

        if not isinstance(results, (list, tuple)):
            raise ValueError("Search function must return a list or tuple")

        ranked_paths = []

        for result in results[:top_k]:
            if isinstance(result, Mapping):
                path = result.get("path")
                if isinstance(path, str):
                    ranked_paths.append(path.replace("\\", "/"))

        retrieved = set(ranked_paths)
        relevant_found = retrieved & expected

        hit_rate = float(bool(relevant_found))
        recall = len(relevant_found) / len(expected)

        reciprocal_rank = 0.0

        for rank, path in enumerate(ranked_paths, start=1):
            if path in expected:
                reciprocal_rank = 1.0 / rank
                break

        case_results.append(
            {
                "question": question,
                "expected_paths": sorted(expected),
                "retrieved_paths": ranked_paths,
                "hit_rate_at_k": hit_rate,
                "recall_at_k": recall,
                "reciprocal_rank": reciprocal_rank,
            }
        )

    count = len(case_results)

    return {
        "top_k": top_k,
        "total_questions": count,
        "hit_rate_at_k": sum(
            item["hit_rate_at_k"] for item in case_results
        ) / count,
        "mean_recall_at_k": sum(
            item["recall_at_k"] for item in case_results
        ) / count,
        "mrr": sum(
            item["reciprocal_rank"] for item in case_results
        ) / count,
        "cases": case_results,
    }
