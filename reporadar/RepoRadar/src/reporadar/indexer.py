
import json
from pathlib import Path

from reporadar.scanner import scan_repository

INDEX_SCHEMA_VERSION = 1


def build_index(repo_path):
    """Scan a repository and build a structured index."""
    scan_result = scan_repository(repo_path)

    indexed_files = []

    for file_info in scan_result["files"]:
        record = {
            "file_id": file_info["path"],
            "path": file_info["path"],
            "language": file_info["language"],
            "size_bytes": file_info["size_bytes"],
            "line_count": file_info["line_count"],
            "source": file_info["source"],
        }
        indexed_files.append(record)

    return {
        "schema_version": INDEX_SCHEMA_VERSION,
        "root": scan_result["root"],
        "indexed_count": len(indexed_files),
        "skipped_count": scan_result["skipped_count"],
        "files": indexed_files,
        "skipped": scan_result["skipped"],
    }


def save_index(index, output_path):
    """Save an index as a UTF-8 JSON file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(index, file, indent=2, ensure_ascii=False)


def load_index(index_path):
    """Load a saved JSON index."""
    index_path = Path(index_path)

    with index_path.open("r", encoding="utf-8") as file:
        index = json.load(file)

    if index.get("schema_version") != INDEX_SCHEMA_VERSION:
        raise ValueError("Unsupported index schema version")

    return index
