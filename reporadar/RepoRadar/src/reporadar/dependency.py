
from pathlib import PurePosixPath

from reporadar.parser import parse_python_file


def build_dependency_graph(index):
    """
    Build a graph of local Python-file dependencies.

    Each file maps to the local files it imports.
    External libraries are ignored.
    """
    files = index["files"]

    # Map Python module names to repository-relative file paths.
    module_to_path = {}

    for file_info in files:
        path = PurePosixPath(file_info["path"])

        if path.name == "__init__.py":
            module_parts = list(path.parent.parts)
        else:
            module_parts = list(path.with_suffix("").parts)

        if module_parts and module_parts[0] == "src":
            module_parts = module_parts[1:]

        module_name = ".".join(module_parts)

        if module_name:
            module_to_path[module_name] = file_info["path"]

    graph = {
        file_info["path"]: set()
        for file_info in files
    }

    for file_info in files:
        source_path = file_info["path"]
        parsed = parse_python_file(
            file_info["source"],
            source_path,
        )

        for imported in parsed["imports"]:
            module = imported["module"]

            if imported["kind"] == "import":
                imported_modules = [
                    item["name"]
                    for item in imported["names"]
                ]
            else:
                imported_modules = [module] if module else []

            for imported_module in imported_modules:
                # Find the imported module or its parent module.
                candidate = imported_module

                while candidate:
                    if candidate in module_to_path:
                        target_path = module_to_path[candidate]

                        if target_path != source_path:
                            graph[source_path].add(target_path)

                        break

                    if "." not in candidate:
                        break

                    candidate = candidate.rsplit(".", 1)[0]

    # Return predictable, JSON-friendly lists.
    return {
        path: sorted(dependencies)
        for path, dependencies in sorted(graph.items())
    }


def build_reverse_dependency_graph(graph):
    """Find the files that depend on each file."""
    reverse_graph = {
        path: []
        for path in graph
    }

    for source_path, dependencies in graph.items():
        for dependency in dependencies:
            reverse_graph[dependency].append(source_path)

    return {
        path: sorted(dependents)
        for path, dependents in sorted(reverse_graph.items())
    }
