
import sys
from pathlib import Path
from pprint import pprint

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from reporadar.impact import analyze_impact


def main():
    # Example dependency graph for demonstration.
    # Each file maps to the files it imports.
    forward_graph = {
        "app.py": ["auth.py"],
        "main.py": ["app.py"],
        "tests/test_auth.py": ["auth.py"],
        "tests/test_app.py": ["app.py"],
        "report.py": [],
    }

    changed_file = "auth.py"

    result = analyze_impact(changed_file, forward_graph)

    print("\nREPORADAR CHANGE IMPACT ANALYSIS")
    print("=" * 40)
    print(f"Changed file: {result['changed_file']}")

    print("\nDirectly affected files:")
    for file_path in result["directly_affected"]:
        print(f"  - {file_path}")

    print("\nTransitively affected files:")
    for file_path in result["transitively_affected"]:
        print(f"  - {file_path}")

    print("\nWhy are these files affected?")
    pprint(result["impact_paths"])

    print(f"\nTotal potentially affected files: {result['total_affected']}")


if __name__ == "__main__":
    main()
