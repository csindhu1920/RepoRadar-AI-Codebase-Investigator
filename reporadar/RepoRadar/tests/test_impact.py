
import pytest

from reporadar.impact import build_reverse_graph, analyze_impact


def test_build_reverse_graph():
    forward_graph = {
        "app.py": ["auth.py"],
        "tests/test_auth.py": ["auth.py"],
    }

    reverse_graph = build_reverse_graph(forward_graph)

    assert reverse_graph["auth.py"] == {
        "app.py",
        "tests/test_auth.py",
    }
    assert reverse_graph["app.py"] == set()


def test_finds_directly_affected_files():
    graph = {
        "app.py": ["auth.py"],
        "tests/test_auth.py": ["auth.py"],
    }

    result = analyze_impact("auth.py", graph)

    assert result["directly_affected"] == [
        "app.py",
        "tests/test_auth.py",
    ]
    assert result["transitively_affected"] == []
    assert result["total_affected"] == 2


def test_finds_transitive_impact():
    graph = {
        "app.py": ["auth.py"],
        "main.py": ["app.py"],
        "tests/test_auth.py": ["auth.py"],
    }

    result = analyze_impact("auth.py", graph)

    assert result["directly_affected"] == [
        "app.py",
        "tests/test_auth.py",
    ]
    assert result["transitively_affected"] == ["main.py"]
    assert result["total_affected"] == 3


def test_returns_explanation_path():
    graph = {
        "app.py": ["auth.py"],
        "main.py": ["app.py"],
    }

    result = analyze_impact("auth.py", graph)

    assert result["impact_paths"]["app.py"] == [
        "auth.py",
        "app.py",
    ]
    assert result["impact_paths"]["main.py"] == [
        "auth.py",
        "app.py",
        "main.py",
    ]


def test_handles_dependency_cycles():
    graph = {
        "a.py": ["b.py"],
        "b.py": ["a.py"],
    }

    result = analyze_impact("a.py", graph)

    # The changed file must not be reported as affected by itself.
    assert "a.py" not in result["impact_paths"]
    assert result["directly_affected"] == ["b.py"]
    assert result["total_affected"] == 1


def test_unknown_file_has_no_impact():
    result = analyze_impact("missing.py", {})

    assert result["directly_affected"] == []
    assert result["transitively_affected"] == []
    assert result["impact_paths"] == {}
    assert result["total_affected"] == 0


def test_rejects_blank_changed_file():
    with pytest.raises(ValueError, match="Changed file must not be empty"):
        analyze_impact("   ", {})
