

import re


def search_index(index, query, top_k=10):
    """
    Search indexed Python source code using keywords.

    Returns matching source lines, ranked by the number
    of keyword occurrences, with file paths and line numbers.
    """
    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    terms = list(
        dict.fromkeys(re.findall(r"\w+", query.lower()))
    )

    if not terms:
        return []

    results = []

    for file_info in index.get("files", []):
        source = file_info.get("source", "")

        for line_number, line in enumerate(
            source.splitlines(), start=1
        ):
            line_lower = line.lower()

            matched_terms = [
                term for term in terms
                if term in line_lower
            ]

            if not matched_terms:
                continue

            score = sum(
                line_lower.count(term) for term in terms
            )

            results.append({
                "path": file_info["path"],
                "line_number": line_number,
                "score": score,
                "matched_terms": matched_terms,
                "snippet": line.strip(),
            })

    results.sort(
        key=lambda result: (
            -result["score"],
            result["path"],
            result["line_number"],
        )
    )

    return results[:top_k]
