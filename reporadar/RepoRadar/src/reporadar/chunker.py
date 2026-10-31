
def chunk_file(file_info, chunk_size=30, overlap=5):
    """
    Split a file's source code into overlapping line chunks.

    Each chunk preserves the original file path and line numbers.
    """
    if chunk_size < 1:
        raise ValueError("chunk_size must be at least 1")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be >= 0 and smaller than chunk_size"
        )

    source_lines = file_info.get("source", "").splitlines()
    path = file_info["path"]

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(source_lines), step):
        end = min(start + chunk_size, len(source_lines))

        chunk_text = "\n".join(source_lines[start:end])

        chunks.append({
            "chunk_id": f"{path}:{start + 1}-{end}",
            "path": path,
            "start_line": start + 1,
            "end_line": end,
            "text": chunk_text,
        })

        if end == len(source_lines):
            break

    return chunks


def chunk_index(index, chunk_size=30, overlap=5):
    """Split every indexed file into searchable chunks."""
    all_chunks = []

    for file_info in index.get("files", []):
        all_chunks.extend(
            chunk_file(
                file_info,
                chunk_size=chunk_size,
                overlap=overlap,
            )
        )

    return all_chunks
