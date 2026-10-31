
import pytest

from reporadar.reliability import validate_answer_sources


def test_accepts_a_citation_from_retrieved_evidence():
    answer = "Authentication is handled in auth.py."
    evidence = [{"path": "auth.py"}]

    result = validate_answer_sources(answer, evidence)

    assert result["has_citations"] is True
    assert result["supported_paths"] == ["auth.py"]
    assert result["unsupported_paths"] == []
    assert result["citations_consistent"] is True


def test_flags_a_file_not_in_retrieved_evidence():
    answer = "Authentication is handled in secret_auth.py."
    evidence = [{"path": "auth.py"}]

    result = validate_answer_sources(answer, evidence)

    assert result["unsupported_paths"] == ["secret_auth.py"]
    assert result["citations_consistent"] is False


def test_flags_an_answer_without_file_citations():
    result = validate_answer_sources(
        "Authentication probably happens somewhere in the project.",
        [{"path": "auth.py"}],
    )

    assert result["has_citations"] is False
    assert result["citations_consistent"] is False


def test_accepts_line_number_citations():
    result = validate_answer_sources(
        "See auth.py:10-20 for the implementation.",
        [{"path": "auth.py"}],
    )

    assert result["supported_paths"] == ["auth.py"]
    assert result["unsupported_paths"] == []


def test_rejects_empty_answer():
    with pytest.raises(ValueError):
        validate_answer_sources("", [])


def test_rejects_invalid_evidence_container():
    with pytest.raises(ValueError):
        validate_answer_sources("See auth.py.", {})
