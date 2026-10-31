
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from reporadar.indexer import build_index, load_index
from reporadar.semantic_search import semantic_search


def main():
    index_path = PROJECT_ROOT / "data" / "index.json"

    if index_path.exists():
        index = load_index(index_path)
    else:
        index = build_index(PROJECT_ROOT)

    query = "Where do we find Python functions and imports?"
    results = semantic_search(index, query, top_k=5)

    print(f"\nQuery: {query}")
    print("\nMost relevant code chunks:")

    for rank, result in enumerate(results, start=1):
        print(f"\n{rank}. {result['path']}")
        print(
            f"   Lines {result['start_line']}-"
            f"{result['end_line']}"
        )
        print(f"   Similarity: {result['score']:.4f}")
        print(f"   Code:\n{result['text']}")


if __name__ == "__main__":
    main()
