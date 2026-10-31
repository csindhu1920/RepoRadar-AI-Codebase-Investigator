import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from reporadar.dependency import build_dependency_graph
from reporadar.impact import analyze_impact
from reporadar.scanner import scan_repository


def print_impact_report(
    changed_file: str,
    forward_graph: dict[str, list[str]],
) -> None:
    result = analyze_impact(changed_file, forward_graph)

    print("\nREPORADAR — REAL CHANGE IMPACT")
    print("=" * 40)
    print(f"Changed file: {result['changed_file']}")

    print("\nDirectly affected files:")
    for path in result["directly_affected"]:
        print(f"  - {path}")

    print("\nTransitively affected files:")
    for path in result["transitively_affected"]:
        print(f"  - {path}")

    print("\nImpact paths:")
    for path, dependency_path in result["impact_paths"].items():
        print(f"  {path}: {' -> '.join(dependency_path)}")

    print(f"\nTotal affected files: {result['total_affected']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze which Python files may be affected by a change."
    )
    parser.add_argument(
        "changed_file",
        help="Python file changed, relative to this repository root",
    )
    args = parser.parse_args()

    changed_path = Path(args.changed_file)
    if not changed_path.is_absolute():
        changed_path = PROJECT_ROOT / changed_path

    try:
        changed_file = changed_path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        parser.error("changed_file must be inside the repository")

    forward_graph = build_dependency_graph(scan_repository(PROJECT_ROOT))
    if changed_file not in forward_graph:
        parser.error(f"Python file not found or not indexed: {changed_file}")

    print_impact_report(changed_file, forward_graph)


if __name__ == "__main__":
    main()