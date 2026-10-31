
import pytest

from reporadar.evaluation import evaluate_retrieval


def test_perfect_retrieval_scores():
    def fake_search(index, question, top_k=5):
        return [
            {"path": "auth.py"},
            {"path": "app.py"},
        ]

    report = evaluate_retrieval(
        index={},
        cases=[
            {
                "question": "Where is authentication implemented?",
                "expected_paths": ["auth.py", "app.py"],
            }
        ],
        search_fn=fake_search,
        top_k=2,
    )

    assert report["total_questions"] == 1
    assert report["hit_rate_at_k"] == 1.0
    assert report["mean_recall_at_k"] == 1.0
    assert report["mrr"] == 1.0


def test_recall_measures_expected_files_found():
    def fake_search(index, question, top_k=5):
        return [{"path": "auth.py"}]

    report = evaluate_retrieval(
        index={},
        cases=[
            {
                "question": "Find authentication code",
                "expected_paths": ["auth.py", "app.py"],
            }
        ],
        search_fn=fake_search,
        top_k=5,
    )

    assert report["hit_rate_at_k"] == 1.0
    assert report["mean_recall_at_k"] == 0.5
    assert report["mrr"] == 1.0


def test_mrr_rewards_higher_ranked_relevant_files():
    def fake_search(index, question, top_k=5):
        return [
            {"path": "other.py"},
            {"path": "auth.py"},
        ]

    report = evaluate_retrieval(
        index={},
        cases=[
            {
                "question": "Find authentication code",
                "expected_paths": ["auth.py"],
            }
        ],
        search_fn=fake_search,
        top_k=5,
    )

    assert report["mrr"] == 0.5


def test_no_relevant_results_scores_zero():
    def fake_search(index, question, top_k=5):
        return [{"path": "unrelated.py"}]

    report = evaluate_retrieval(
        index={},
        cases=[
            {
                "question": "Find authentication code",
                "expected_paths": ["auth.py"],
            }
        ],
        search_fn=fake_search,
    )

    assert report["hit_rate_at_k"] == 0.0
    assert report["mean_recall_at_k"] == 0.0
    assert report["mrr"] == 0.0


def test_empty_evaluation_cases_are_rejected():
    with pytest.raises(ValueError):
        evaluate_retrieval(
            index={},
            cases=[],
            search_fn=lambda index, question, top_k=5: [],
        )


def test_empty_question_is_rejected():
    with pytest.raises(ValueError):
        evaluate_retrieval(
            index={},
            cases=[
                {
                    "question": "",
                    "expected_paths": ["auth.py"],
                }
            ],
            search_fn=lambda index, question, top_k=5: [],
        )


def test_invalid_top_k_is_rejected():
    with pytest.raises(ValueError):
        evaluate_retrieval(
            index={},
            cases=[
                {
                    "question": "Find authentication",
                    "expected_paths": ["auth.py"],
                }
            ],
            search_fn=lambda index, question, top_k=5: [],
            top_k=0,
        )
