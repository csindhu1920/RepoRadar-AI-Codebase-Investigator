
import re
from pathlib import PurePosixPath


PYTHON_PATH_PATTERN = re.compile(
    r"(?<![\w.-])"
    r"((?:[\w.-]+/)*[\w.-]+\.py)"
    r"(?::(?:lines?\s*)?\d+(?:-\d+)?)?"
)


def validate_answer_sources(answer: str, retrieved_results: list) -> dict:
    """
    Check whether Python file paths mentioned in an answer
    appear in the retrieved evidence.

    This checks citation consistency, not factual correctness.
    """
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("Answer must not be empty")

    if not isinstance(retrieved_results, list):
        raise ValueError("Retrieved results must be a list")

    known_paths = set()

    for result in retrieved_results:
        if not isinstance(result, dict):
            continue

        path = result.get("path")

        if isinstance(path, str) and path.strip():
            known_paths.add(path.replace("\\", "/"))

    cited_paths = {
        match.replace("\\", "/")
        for match in PYTHON_PATH_PATTERN.findall(answer)
    }

    supported_paths = sorted(cited_paths & known_paths)
    unsupported_paths = sorted(cited_paths - known_paths)

    return {
        "has_citations": bool(cited_paths),
        "cited_paths": sorted(cited_paths),
        "supported_paths": supported_paths,
        "unsupported_paths": unsupported_paths,
        "citations_consistent": bool(cited_paths)
        and not unsupported_paths,
    }
