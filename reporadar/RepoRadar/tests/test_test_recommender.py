
import pytest

from reporadar.test_recommender import recommend_tests


def test_recommends_test_that_directly_imports_changed_file():
    graph = {
        "src/reporadar/impact.py": [],
        "tests/test_impact.py": [
            "src/reporadar/impact.py"
        ],
    }

    impact = {
        "directly_affected": [],
        "transitively_affected": [],
    }

    result = recommend_tests(
        "src/reporadar/impact.py",
        impact,
        graph,
    )

    assert len(result) == 1
    assert result[0]["path"] == "tests/test_impact.py"
    assert result[0]["priority"] == 100


def test_recommends_test_importing_directly_affected_file():
    graph = {
        "src/reporadar/impact.py": [],
        "src/reporadar/parser.py": [],
        "tests/test_parser.py": [
            "src/reporadar/parser.py"
        ],
    }

    impact = {
        "directly_affected": ["src/reporadar/parser.py"],
        "transitively_affected": [],
    }

    result = recommend_tests(
        "src/reporadar/impact.py",
        impact,
        graph,
    )

    assert any(
        item["path"] == "tests/test_parser.py"
        for item in result
    )


def test_recommends_test_by_matching_filename():
    graph = {
        "src/reporadar/impact.py": [],
        "tests/test_impact.py": [],
    }

    result = recommend_tests(
        "src/reporadar/impact.py",
        {
            "directly_affected": [],
            "transitively_affected": [],
        },
        graph,
    )

    assert result[0]["path"] == "tests/test_impact.py"
    assert result[0]["priority"] == 60


def test_returns_empty_list_when_no_tests_match():
    graph = {
        "src/reporadar/impact.py": [],
        "src/reporadar/parser.py": [],
    }

    result = recommend_tests(
        "src/reporadar/impact.py",
        {
            "directly_affected": [],
            "transitively_affected": [],
        },
        graph,
    )

    assert result == []


def test_does_not_duplicate_test_recommendations():
    graph = {
        "src/reporadar/impact.py": [],
        "tests/test_impact.py": [
            "src/reporadar/impact.py"
        ],
    }

    impact = {
        "directly_affected": ["tests/test_impact.py"],
        "transitively_affected": [],
    }

    result = recommend_tests(
        "src/reporadar/impact.py",
        impact,
        graph,
    )

    paths = [item["path"] for item in result]
    assert len(paths) == len(set(paths))


def test_rejects_empty_changed_file():
    with pytest.raises(ValueError):
        recommend_tests(
            "",
            {},
            {},
        )


def test_prioritizes_direct_import_over_name_match():
    graph = {
        "src/reporadar/impact.py": [],
        "tests/test_impact.py": [],
        "tests/test_other.py": [
            "src/reporadar/impact.py"
        ],
    }

    result = recommend_tests(
        "src/reporadar/impact.py",
        {
            "directly_affected": [],
            "transitively_affected": [],
        },
        graph,
    )

    assert result[0]["path"] == "tests/test_other.py"
    assert result[0]["priority"] == 100
