
from collections import deque
from typing import Iterable


def build_reverse_graph(
    forward_graph: dict[str, Iterable[str]],
) -> dict[str, set[str]]:
    """
    Convert a forward dependency graph into a reverse graph.

    Forward meaning:
        app.py -> auth.py
        app.py imports auth.py

    Reverse meaning:
        auth.py -> app.py
        app.py depends on auth.py
    """
    reverse_graph: dict[str, set[str]] = {}

    # Include files even if they have no dependencies.
    for source, dependencies in forward_graph.items():
        reverse_graph.setdefault(source, set())

        for dependency in dependencies:
            reverse_graph.setdefault(dependency, set())
            reverse_graph[dependency].add(source)

    return reverse_graph


def analyze_impact(
    changed_file: str,
    forward_graph: dict[str, Iterable[str]],
) -> dict:
    """
    Find files that may be affected by a change.

    The changed file itself is not included in the affected files.
    """
    if not changed_file or not changed_file.strip():
        raise ValueError("Changed file must not be empty")

    reverse_graph = build_reverse_graph(forward_graph)

    # Include a changed file that is not already in the graph.
    reverse_graph.setdefault(changed_file, set())

    direct = sorted(reverse_graph[changed_file])

    # Store each discovered file and its path from the changed file.
    paths: dict[str, list[str]] = {}
    queue = deque(
        (dependent, [changed_file, dependent])
        for dependent in direct
    )

    while queue:
        current, path = queue.popleft()
        if current == changed_file:
            continue
        

        # If already reached, keep the first shortest path.
        if current in paths:
            continue

        paths[current] = path

        for dependent in sorted(reverse_graph.get(current, set())):
            if dependent not in paths:
                queue.append((dependent, path + [dependent]))

    direct_set = set(direct)
    transitive = sorted(set(paths) - direct_set)

    return {
        "changed_file": changed_file,
        "directly_affected": direct,
        "transitively_affected": transitive,
        "impact_paths": {
            file_path: paths[file_path]
            for file_path in sorted(paths)
        },
        "total_affected": len(paths),
    }
