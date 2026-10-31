
import json
import sys
from pathlib import Path

# Allow this simple development entry point to find src/reporadar.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from reporadar.scanner import scan_repository


def main():
    repo_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else Path(__file__).resolve().parent
    )

    result = scan_repository(repo_path)

    # Avoid printing source code; show only summary metadata.
    summary = {
        "root": result["root"],
        "indexed_count": result["indexed_count"],
        "skipped_count": result["skipped_count"],
        "files": [
            {
                "path": item["path"],
                "language": item["language"],
                "line_count": item["line_count"],
                "size_bytes": item["size_bytes"],
            }
            for item in result["files"]
        ],
        "skipped": result["skipped"],
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
