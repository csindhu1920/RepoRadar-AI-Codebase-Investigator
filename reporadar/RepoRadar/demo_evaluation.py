
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from reporadar.evaluation import evaluate_retrieval
from reporadar.hybrid_search import hybrid_search


INDEX_PATH = PROJECT_ROOT / "data" / "index.json"


def main():
    if not INDEX_PATH.exists():
        print(f"Index not found: {INDEX_PATH}")
        return

    with INDEX_PATH.open("r", encoding="utf-8") as file:
        index = json.load(file)

    indexed_paths = {
        item["path"].replace("\\", "/")
        for item in index.get("files", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }

    # These cases are tailored to the sample project you indexed.
    # Only evaluate cases whose expected files exist in the index.
    proposed_cases = [
        {
            "question": "Where is authentication implemented?",
            "expected_paths": ["auth.py"],
        },
        {
            "question": "Where are authentication tests defined?",
            "expected_paths": ["tests/test_auth.py"],
        },
        {
            "question": "Where is the application entry point?",
            "expected_paths": ["app.py"],
        },
    ]

    cases = [
        case
        for case in proposed_cases
        if all(path in indexed_paths for path in case["expected_paths"])
    ]

    if not cases:
        print("No evaluation cases match the current index.")
        print("Review the indexed files and update proposed_cases.")
        return

    report = evaluate_retrieval(
        index=index,
        cases=cases,
        search_fn=hybrid_search,
        top_k=5,
    )

    print("\nREPORADAR — RETRIEVAL EVALUATION")
    print("=" * 45)
    print(f"Questions evaluated: {report['total_questions']}")
    print(f"Top K: {report['top_k']}")
    print(f"Hit Rate@K: {report['hit_rate_at_k']:.2%}")
    print(f"Mean Recall@K: {report['mean_recall_at_k']:.2%}")
    print(f"MRR: {report['mrr']:.3f}")

    print("\nPer-question results:")

    for number, case in enumerate(report["cases"], start=1):
        print(f"\n{number}. {case['question']}")
        print(f"   Expected: {case['expected_paths']}")
        print(f"   Retrieved: {case['retrieved_paths']}")
        print(f"   Hit Rate@K: {case['hit_rate_at_k']:.2f}")
        print(f"   Recall@K: {case['recall_at_k']:.2f}")
        print(f"   Reciprocal Rank: {case['reciprocal_rank']:.3f}")

    # Save a report that can be compared with future changes.
    report_path = PROJECT_ROOT / "data" / "evaluation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print(f"\nEvaluation report saved to: {report_path}")


if __name__ == "__main__":
    main()
