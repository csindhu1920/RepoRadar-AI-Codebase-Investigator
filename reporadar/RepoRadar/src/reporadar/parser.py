
import ast


class CodeStructureVisitor(ast.NodeVisitor):
    """Collect function, class, and import information from Python AST."""

    def __init__(self):
        self.functions = []
        self.classes = []
        self.imports = []
        self.scope = []

    def visit_FunctionDef(self, node):
        self._record_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node):
        self._record_function(node, is_async=True)

    def _record_function(self, node, is_async):
        qualified_name = ".".join(self.scope + [node.name])

        self.functions.append({
            "name": node.name,
            "qualified_name": qualified_name,
            "line": node.lineno,
            "end_line": node.end_lineno,
            "parameters": [
                arg.arg for arg in node.args.args
            ],
            "is_async": is_async,
        })

        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_ClassDef(self, node):
        qualified_name = ".".join(self.scope + [node.name])

        self.classes.append({
            "name": node.name,
            "qualified_name": qualified_name,
            "line": node.lineno,
            "end_line": node.end_lineno,
            "bases": [
                ast.unparse(base) for base in node.bases
            ],
        })

        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_Import(self, node):
        self.imports.append({
            "kind": "import",
            "module": None,
            "names": [
                {
                    "name": alias.name,
                    "alias": alias.asname,
                }
                for alias in node.names
            ],
            "line": node.lineno,
        })

    def visit_ImportFrom(self, node):
        self.imports.append({
            "kind": "from",
            "module": node.module,
            "level": node.level,
            "names": [
                {
                    "name": alias.name,
                    "alias": alias.asname,
                }
                for alias in node.names
            ],
            "line": node.lineno,
        })


def parse_python_file(source, path="<unknown>"):
    """Extract code structure from Python source without executing it."""
    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as exc:
        return {
            "path": path,
            "functions": [],
            "classes": [],
            "imports": [],
            "syntax_error": {
                "message": exc.msg,
                "line": exc.lineno,
                "offset": exc.offset,
            },
        }

    visitor = CodeStructureVisitor()
    visitor.visit(tree)

    return {
        "path": path,
        "functions": visitor.functions,
        "classes": visitor.classes,
        "imports": visitor.imports,
        "syntax_error": None,
    }
