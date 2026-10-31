
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from reporadar.search import search_index


def make_index():
    return {
        "files": [
            {
                "path": "auth.py",
                "source": (
                    "def login(username, password):\n"
                    "    if password == 'secret':\n"
                    "        return True\n"
                ),
            },
            {
                "path": "app.py",
                "source": (
                    "from auth import login\n"
                    "def main():\n"
                    "    return login('admin', 'secret')\n"
                ),
            },
        ]
    }


def test_finds_matching_keywords():
    results = search_index(make_index(), "password")

    assert len(results) >= 1
    assert results[0]["path"] == "auth.py"
    assert results[0]["line_number"] == 1


def test_returns_file_path_and_snippet():
    results = search_index(make_index(), "login")

    assert results
    assert all("path" in result for result in results)
    assert all("line_number" in result for result in results)
    assert all("snippet" in result for result in results)


def test_search_is_case_insensitive():
    results = search_index(make_index(), "LOGIN")

    assert results


def test_empty_query_returns_no_results():
    assert search_index(make_index(), "") == []


def test_top_k_limits_results():
    results = search_index(make_index(), "login", top_k=1)

    assert len(results) == 1


def test_invalid_top_k_raises_error():
    try:
        search_index(make_index(), "login", top_k=0)
        assert False, "Expected ValueError"
    except ValueError:
        pass
