
import json
import sys
from pathlib import Path

# Make the src directory available for imports.
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from reporadar.hybrid_search import hybrid_search


def main():
    index_path = PROJECT_ROOT / "data" / "index.json"

    with index_path.open("r", encoding="utf-8") as file:
        index = json.load(file)

    query = "Where is password authentication handled?"

    results = hybrid_search(
        index,
        query,
        top_k=5,
    )

    print(f"\nQuery: {query}")
    print("\nHybrid search results:\n")

    if not results:
        print("No matching code found.")
        return

    for rank, result in enumerate(results, start=1):
        print(f"{rank}. {result['path']}")
        print(
            f"   Lines: {result['start_line']}"
            f"-{result['end_line']}"
        )
        print(f"   Hybrid score: {result['hybrid_score']:.5f}")
        print(f"   Sources: {', '.join(result['source_types'])}")
        print(f"   Keyword score: {result['keyword_score']}")
        print(f"   Semantic score: {result['semantic_score']}")
        print("   Code:")
        print(f"   {result['text'][:300]}")
        print()


if __name__ == "__main__":
    main()
