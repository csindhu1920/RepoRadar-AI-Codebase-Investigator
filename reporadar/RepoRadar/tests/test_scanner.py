
import sys
from pathlib import Path

import pytest

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "src")
)

from reporadar.scanner import scan_repository


def test_scans_python_files(tmp_path):
    (tmp_path / "app.py").write_text(
        "print('hello')\n", encoding="utf-8"
    )
    (tmp_path / "notes.txt").write_text(
        "not Python", encoding="utf-8"
    )

    result = scan_repository(tmp_path)

    assert result["indexed_count"] == 1
    assert result["files"][0]["path"] == "app.py"
    assert result["files"][0]["line_count"] == 1


def test_excludes_generated_directories(tmp_path):
    (tmp_path / "app.py").write_text(
        "print('hello')\n", encoding="utf-8"
    )

    generated = tmp_path / "__pycache__"
    generated.mkdir()
    (generated / "cached.py").write_text(
        "print('ignore')\n", encoding="utf-8"
    )

    result = scan_repository(tmp_path)

    paths = [item["path"] for item in result["files"]]

    assert paths == ["app.py"]


def test_missing_root_raises_error(tmp_path):
    missing = tmp_path / "does_not_exist"

    with pytest.raises(FileNotFoundError):
        scan_repository(missing)


def test_rejects_file_as_repository_root(tmp_path):
    file_path = tmp_path / "app.py"
    file_path.write_text("print('hello')\n", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        scan_repository(file_path)


def test_paths_are_relative(tmp_path):
    (tmp_path / "auth.py").write_text(
        "def login():\n    pass\n", encoding="utf-8"
    )

    result = scan_repository(tmp_path)

    assert result["files"][0]["path"] == "auth.py"
    assert not Path(result["files"][0]["path"]).is_absolute()


def test_excludes_venv_directory(tmp_path):
    # Create a normal project source file.
    (tmp_path / "app.py").write_text(
        "print('hello')\n",
        encoding="utf-8",
    )

    # Simulate a virtual environment containing Python code.
    venv_dir = tmp_path / ".venv"
    venv_dir.mkdir()

    (venv_dir / "fake_package.py").write_text(
        "print('this should be ignored')\n",
        encoding="utf-8",
    )

    # Scan the temporary repository.
    result = scan_repository(tmp_path)

    # Only app.py should be indexed.
    paths = [item["path"] for item in result["files"]]

    assert result["indexed_count"] == 1
    assert paths == ["app.py"]
    assert ".venv/fake_package.py" not in paths


def test_skips_files_larger_than_size_limit(tmp_path):
    from reporadar.scanner import MAX_FILE_SIZE_BYTES

    # Create a normal Python file.
    (tmp_path / "app.py").write_text(
        "print('hello')\n",
        encoding="utf-8",
    )

    # Create a Python file just over the size limit.
    large_file = tmp_path / "large.py"
    large_file.write_bytes(b"x" * (MAX_FILE_SIZE_BYTES + 1))

    result = scan_repository(tmp_path)

    paths = [item["path"] for item in result["files"]]

    assert paths == ["app.py"]
    assert result["indexed_count"] == 1
    assert result["skipped_count"] == 1
    assert result["skipped"][0]["path"] == "large.py"
    assert result["skipped"][0]["reason"] == "file_too_large"
