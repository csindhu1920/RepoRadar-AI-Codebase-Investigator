
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from reporadar.dependency import (
    build_dependency_graph,
    build_reverse_dependency_graph,
)


def make_index():
    return {
        "files": [
            {
                "path": "app.py",
                "source": "from auth import login\n",
            },
            {
                "path": "auth.py",
                "source": "def login(username):\n    return username\n",
            },
            {
                "path": "tests/test_auth.py",
                "source": "from auth import login\n",
            },
        ]
    }


def test_builds_local_dependency_graph():
    graph = build_dependency_graph(make_index())

    assert graph["app.py"] == ["auth.py"]
    assert graph["auth.py"] == []
    assert graph["tests/test_auth.py"] == ["auth.py"]


def test_builds_reverse_dependency_graph():
    graph = build_dependency_graph(make_index())
    reverse_graph = build_reverse_dependency_graph(graph)

    assert reverse_graph["auth.py"] == [
        "app.py",
        "tests/test_auth.py",
    ]
    assert reverse_graph["app.py"] == []


def test_resolves_imports_from_src_layout():
    index = {
        "files": [
            {
                "path": "src/reporadar/impact.py",
                "source": "def analyze_impact():\n    pass\n",
            },
            {
                "path": "tests/test_impact.py",
                "source": "from reporadar.impact import analyze_impact\n",
            },
        ]
    }

    graph = build_dependency_graph(index)

    assert graph["tests/test_impact.py"] == [
        "src/reporadar/impact.py",
    ]
