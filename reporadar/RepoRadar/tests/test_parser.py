
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "src")
)

from reporadar.parser import parse_python_file


def test_extracts_functions_and_parameters():
    source = (
        "def login(username):\n"
        "    return username\n"
    )

    result = parse_python_file(source, "auth.py")

    assert result["syntax_error"] is None
    assert len(result["functions"]) == 1
    assert result["functions"][0]["name"] == "login"
    assert result["functions"][0]["parameters"] == ["username"]
    assert result["functions"][0]["line"] == 1


def test_extracts_classes_and_methods():
    source = (
        "class User:\n"
        "    def login(self, username):\n"
        "        return username\n"
    )

    result = parse_python_file(source, "user.py")

    assert result["classes"][0]["name"] == "User"
    assert result["classes"][0]["line"] == 1
    assert any(
        function["qualified_name"] == "User.login"
        for function in result["functions"]
    )


def test_extracts_imports():
    source = (
        "import os\n"
        "from auth import login\n"
    )

    result = parse_python_file(source, "app.py")

    assert len(result["imports"]) == 2
    assert result["imports"][0]["names"][0]["name"] == "os"
    assert result["imports"][1]["module"] == "auth"
    assert result["imports"][1]["names"][0]["name"] == "login"


def test_handles_syntax_errors():
    source = "def broken(:\n    pass\n"

    result = parse_python_file(source, "broken.py")

    assert result["syntax_error"] is not None
    assert result["syntax_error"]["line"] == 1
    assert result["functions"] == []
    assert result["classes"] == []
