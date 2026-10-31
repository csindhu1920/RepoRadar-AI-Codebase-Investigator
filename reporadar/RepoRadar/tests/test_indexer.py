
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "src")
)

from reporadar.indexer import build_index, save_index, load_index


def test_build_index_records_file_metadata(tmp_path):
    (tmp_path / "auth.py").write_text(
        "def login():\n    return 'ok'\n",
        encoding="utf-8",
    )

    index = build_index(tmp_path)

    assert index["schema_version"] == 1
    assert index["indexed_count"] == 1
    assert index["files"][0]["path"] == "auth.py"
    assert index["files"][0]["file_id"] == "auth.py"
    assert "def login" in index["files"][0]["source"]


def test_save_and_load_index(tmp_path):
    (tmp_path / "auth.py").write_text(
        "def login():\n    return 'ok'\n",
        encoding="utf-8",
    )

    index = build_index(tmp_path)
    output_path = tmp_path / "data" / "index.json"

    save_index(index, output_path)
    loaded_index = load_index(output_path)

    assert loaded_index == index
    assert output_path.exists()


def test_load_rejects_unsupported_schema(tmp_path):
    index_path = tmp_path / "index.json"
    index_path.write_text(
        '{"schema_version": 999}',
        encoding="utf-8",
    )

    import pytest

    with pytest.raises(ValueError, match="Unsupported index schema"):
        load_index(index_path)
