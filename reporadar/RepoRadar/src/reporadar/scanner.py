
from pathlib import Path
import os

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
}

MAX_FILE_SIZE_BYTES = 1_000_000  # 1 MB


def scan_repository(repo_path: str | Path) -> dict:
    """Scan a repository and collect metadata for Python files."""
    root = Path(repo_path).expanduser().resolve()

    if not root.exists():
        raise FileNotFoundError(f"Repository not found: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    indexed_files = []
    skipped_files = []

    # Prune excluded directories before descending into them.
    for current_dir, dirs, filenames in os.walk(
        root, followlinks=False
    ):
        dirs[:] = sorted(
            d for d in dirs
            if d not in EXCLUDED_DIRS
            and not (Path(current_dir) / d).is_symlink()
        )

        for filename in sorted(filenames):
            path = Path(current_dir) / filename

            if path.suffix.lower() != ".py":
                continue

            try:
                # Do not follow file symlinks.
                if path.is_symlink():
                    skipped_files.append({
                        "path": path.relative_to(root).as_posix(),
                        "reason": "symlink",
                    })
                    continue

                relative_path = path.relative_to(root).as_posix()

                # Check size before loading the file into memory.
                size_bytes = path.stat().st_size
                if size_bytes > MAX_FILE_SIZE_BYTES:
                    skipped_files.append({
                        "path": relative_path,
                        "reason": "file_too_large",
                    })
                    continue

                source = path.read_text(encoding="utf-8")
                line_count = len(source.splitlines())

                indexed_files.append({
                    "path": relative_path,
                    "language": "python",
                    "size_bytes": size_bytes,
                    "line_count": line_count,
                    "source": source,
                })

            except (OSError, UnicodeError, ValueError) as exc:
                skipped_files.append({
                    "path": path.relative_to(root).as_posix(),
                    "reason": type(exc).__name__,
                })

    indexed_files.sort(key=lambda item: item["path"])
    skipped_files.sort(key=lambda item: item["path"])

    return {
        "root": str(root),
        "indexed_count": len(indexed_files),
        "skipped_count": len(skipped_files),
        "files": indexed_files,
        "skipped": skipped_files,
    }
