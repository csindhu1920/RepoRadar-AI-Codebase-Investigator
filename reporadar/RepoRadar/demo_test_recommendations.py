
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from reporadar.dependency import build_dependency_graph
from reporadar.impact import analyze_impact
from reporadar.test_recommender import recommend_tests


INDEX_PATH = PROJECT_ROOT / "data" / "index.json"


def main():
    if not INDEX_PATH.exists():
        print(f"Index not found: {INDEX_PATH}")
        return

    with INDEX_PATH.open("r", encoding="utf-8") as file:
        index = json.load(file)

    forward_graph = build_dependency_graph(index)

    if not forward_graph:
        print("No Python files found in the repository index.")
        return

    print("\nREPORADAR — TEST RECOMMENDATIONS")
    print("=" * 45)

    print("\nAvailable files:")
    for path in sorted(forward_graph):
        print(f"  {path}")

    changed_file = input(
        "\nEnter the exact changed-file path: "
    ).strip().replace("\\", "/")

    if changed_file not in forward_graph:
        print("File not found in the dependency graph.")
        return

    impact = analyze_impact(changed_file, forward_graph)

    recommendations = recommend_tests(
        changed_file,
        impact,
        forward_graph,
    )

    print(f"\nChanged file: {changed_file}")
    print(f"Potentially affected files: {impact['total_affected']}")

    print("\nRecommended tests, highest priority first:")

    if not recommendations:
        print("No relevant tests identified by current heuristics.")
        print("Consider running the full test suite.")
        return

    for number, item in enumerate(recommendations, start=1):
        print(f"\n{number}. {item['path']}")
        print(f"   Priority score: {item['priority']}")

        for reason in item["reasons"]:
            print(f"   Reason: {reason}")

    print("\nRecommendation only: run the tests to verify behavior.")


if __name__ == "__main__":
    main()
