from pathlib import PurePosixPath


def recommend_tests(
    changed_file: str,
    impact_result: dict,
    forward_graph: dict[str, list[str]],
) -> list[dict]:
    """
    Recommend tests based on change-impact analysis.

    Args:
        changed_file: Repository-relative path of the changed file.
        impact_result: Result returned by analyze_impact().
        forward_graph: Mapping of files to the files they import.

    Returns:
        Test recommendations sorted by descending priority.
    """
    if not changed_file or not changed_file.strip():
        raise ValueError("Changed file must not be empty")

    if not isinstance(impact_result, dict):
        raise ValueError("Impact result must be a dictionary")

    if not isinstance(forward_graph, dict):
        raise ValueError("Forward graph must be a dictionary")

    changed_file = changed_file.replace("\\", "/")
    changed_module = PurePosixPath(changed_file).stem.lower()

    direct = set(impact_result.get("directly_affected", []))
    transitive = set(impact_result.get("transitively_affected", []))
    affected = direct | transitive

    test_files = {
        path
        for path in forward_graph
        if (
            PurePosixPath(path).name.lower().startswith("test_")
            or PurePosixPath(path).name.lower().endswith("_test.py")
            or "tests/" in path.replace("\\", "/").lower()
        )
    }

    imported_by = {}

    for source, dependencies in forward_graph.items():
        for dependency in dependencies:
            imported_by.setdefault(dependency, set()).add(source)

    candidates = {}

    def add_candidate(path, score, reason):
        if path not in candidates:
            candidates[path] = {
                "path": path,
                "priority": score,
                "reasons": [],
            }

        candidates[path]["priority"] = max(
            candidates[path]["priority"], score
        )

        if reason not in candidates[path]["reasons"]:
            candidates[path]["reasons"].append(reason)

    for test_path in sorted(test_files):
        test_name = PurePosixPath(test_path).stem.lower()

        if test_path in imported_by.get(changed_file, set()):
            add_candidate(
                test_path,
                100,
                "Directly imports the changed file",
            )

        for affected_file in sorted(direct):
            if test_path in imported_by.get(affected_file, set()):
                add_candidate(
                    test_path,
                    90,
                    f"Imports directly affected file: {affected_file}",
                )

        for affected_file in sorted(transitive):
            if test_path in imported_by.get(affected_file, set()):
                add_candidate(
                    test_path,
                    70,
                    f"Imports transitively affected file: {affected_file}",
                )

        if test_path in affected:
            add_candidate(
                test_path,
                80,
                "Listed as affected by dependency analysis",
            )

        if changed_module and changed_module in test_name:
            add_candidate(
                test_path,
                60,
                "Test filename matches the changed module",
            )

    return sorted(
        candidates.values(),
        key=lambda item: (-item["priority"], item["path"]),
    )
