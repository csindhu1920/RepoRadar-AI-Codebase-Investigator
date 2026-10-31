
import sys
from pathlib import Path

import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from reporadar.chunker import chunk_file, chunk_index


# TEST 1: Split a file into overlapping chunks
def test_splits_file_into_chunks():
    file_info = {
        "path": "auth.py",
        "source": "\n".join(
            f"line {i}" for i in range(1, 8)
        ),
    }

    chunks = chunk_file(
        file_info,
        chunk_size=3,
        overlap=1,
    )

    assert len(chunks) == 3
    assert chunks[0]["start_line"] == 1
    assert chunks[0]["end_line"] == 3
    assert chunks[1]["start_line"] == 3
    assert chunks[1]["end_line"] == 5
    assert chunks[2]["start_line"] == 5
    assert chunks[2]["end_line"] == 7


# TEST 2: Preserve the file path and source code
def test_preserves_source_path_and_text():
    file_info = {
        "path": "auth.py",
        "source": "def login():\n    return True",
    }

    chunks = chunk_file(file_info)

    assert chunks[0]["path"] == "auth.py"
    assert chunks[0]["start_line"] == 1
    assert "def login():" in chunks[0]["text"]
    assert "return True" in chunks[0]["text"]


# TEST 3: An empty file should produce no chunks
def test_empty_file_returns_no_chunks():
    file_info = {
        "path": "empty.py",
        "source": "",
    }

    assert chunk_file(file_info) == []


# TEST 4: Reject an invalid chunk size
def test_invalid_chunk_size_raises_error():
    file_info = {
        "path": "auth.py",
        "source": "x = 1",
    }

    with pytest.raises(ValueError):
        chunk_file(file_info, chunk_size=0)


# TEST 5: Reject overlap greater than or equal to chunk size
def test_overlap_must_be_smaller_than_chunk_size():
    file_info = {
        "path": "auth.py",
        "source": "x = 1",
    }

    with pytest.raises(ValueError):
        chunk_file(
            file_info,
            chunk_size=3,
            overlap=3,
        )


# TEST 6: Chunk every file in the index
def test_chunks_entire_index():
    index = {
        "files": [
            {
                "path": "a.py",
                "source": "x = 1",
            },
            {
                "path": "b.py",
                "source": "y = 2",
            },
        ]
    }

    chunks = chunk_index(index)

    assert len(chunks) == 2
    assert {chunk["path"] for chunk in chunks} == {
        "a.py",
        "b.py",
    }
