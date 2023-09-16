from typing import Union, Optional
import libcst as cst
from libcst._nodes.module import Module

DocstringNode = Union[cst.Module, cst.ClassDef, cst.FunctionDef]

def get_docstring_statement(node: DocstringNode) -> Optional[cst.SimpleStatementLine|None]:
    """Extracts the docstring from the body of a node.

    Args:
        node: The node to extract the docstring from.

    Returns:
        The docstring statement if it exists, None otherwise.
    """
    if isinstance(node, cst.Module):
        body = node.body
    else:
        body = node.body.body
    if not body:
        return None

    statement = body[0]
    if not isinstance(statement, cst.SimpleStatementLine):
        return None

    expr = statement
    while isinstance(expr, (cst.BaseSuite, cst.SimpleStatementLine)):
        if len(expr.body) == 0:
            return None
        expr = expr.body[0]

    if not isinstance(expr, cst.Expr):
        return None

    val = expr.value
    if not isinstance(val, (cst.SimpleString, cst.ConcatenatedString)):
        return None

    evaluated_value = val.evaluated_value
    if isinstance(evaluated_value, bytes):
        return None

    return statement


class DocstringTransformer(cst.CSTTransformer):
    """A transformer class for replacing docstrings in a CST.

    Attributes:
        stack: A list to keep track of the current path in the CST.
        docstrings: A dictionary mapping paths in the CST to their corresponding docstrings.
    """

    def __init__(
        self,
        docstrings: dict[tuple[str, ...], cst.SimpleStatementLine],
    ):
        """Initializes the DocstringTransformer.

        Args:
            docstrings: A dictionary mapping paths in the CST to their corresponding docstrings.
        """
        self.stack: list[str] = []
        self.docstrings = docstrings

    def visit_Module(self, node: cst.Module) -> bool | None:
        """Visits a Module node.

        Args:
            node: The Module node.

        Returns:
            True or None.
        """
        self.stack.append("")

    def leave_Module(self, original_node: Module, updated_node: Module) -> Module:
        """Leaves a Module node.

        Args:
            original_node: The original Module node.
            updated_node: The updated Module node.

        Returns:
            The updated Module node.
        """
        return self._leave(original_node, updated_node)  # type: ignore

    def visit_ClassDef(self, node: cst.ClassDef) -> bool | None:
        """Visits a ClassDef node.

        Args:
            node: The ClassDef node.

        Returns:
            True or None.
        """
        self.stack.append(node.name.value)

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.CSTNode:
        """Leaves a ClassDef node.

        Args:
            original_node: The original ClassDef node.
            updated_node: The updated ClassDef node.

        Returns:
            The updated ClassDef node.
        """
        return self._leave(original_node, updated_node)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:
        """Visits a FunctionDef node.

        Args:
            node: The FunctionDef node.

        Returns:
            True or None.
        """
        self.stack.append(node.name.value)

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.CSTNode:
        """Leaves a FunctionDef node.

        Args:
            original_node: The original FunctionDef node.
            updated_node: The updated FunctionDef node.

        Returns:
            The updated FunctionDef node.
        """
        return self._leave(original_node, updated_node)

    def _leave(self, original_node: DocstringNode, updated_node: DocstringNode) -> DocstringNode:
        """Leaves a DocstringNode.

        Args:
            original_node: The original DocstringNode.
            updated_node: The updated DocstringNode.

        Returns:
            The updated DocstringNode.
        """
        key = tuple(self.stack)
        self.stack.pop()

        if hasattr(updated_node, "decorators"):
            for decorator in updated_node.decorators: # type: ignore
                if isinstance(decorator.decorator, cst.Name):
                    if decorator.decorator.value == "overload":
                        return updated_node
                elif isinstance(decorator.decorator, cst.Call):
                    if isinstance(decorator.decorator.func, cst.Name) and decorator.decorator.func.value == "overload":
                        return updated_node

        statement = self.docstrings.get(key)
        if not statement:
            return updated_node

        original_statement = get_docstring_statement(original_node)

        if isinstance(updated_node, cst.Module):
            body = updated_node.body
            if original_statement:
                return updated_node.with_changes(body=(statement, *body[1:]))
            else:
                updated_node = updated_node.with_changes(
                    body=(statement, cst.EmptyLine(), *body))
                return updated_node

        body = updated_node.body.body[1:] if original_statement else updated_node.body.body
        return updated_node.with_changes(body=updated_node.body.with_changes(body=(statement, *body)))

class DocstringCollector(cst.CSTVisitor):
    """A visitor class for collecting docstrings from a CST.

    Attributes:
        stack: A list to keep track of the current path in the CST.
        docstrings: A dictionary mapping paths in the CST to their corresponding docstrings.
    """
    def __init__(self):
        """Initializes the DocstringCollector."""
        self.stack: list[str] = []
        self.docstrings: dict[tuple[str, ...], cst.SimpleStatementLine] = {}

    def visit_Module(self, node: cst.Module) -> bool | None:
        """Visits a Module node.

        Args:
            node: The Module node.

        Returns:
            True or None.
        """
        self.stack.append("")

    def leave_Module(self, node: cst.Module) -> None:
        """Leaves a Module node.

        Args:
            node: The Module node.
        """
        return self._leave(node)

    def visit_ClassDef(self, node: cst.ClassDef) -> bool | None:
        """Visits a ClassDef node.

        Args:
            node: The ClassDef node.

        Returns:
            True or None.
        """
        self.stack.append(node.name.value)

    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        """Leaves a ClassDef node.

        Args:
            node: The ClassDef node.
        """
        return self._leave(node)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:
        """Visits a FunctionDef node.

        Args:
            node: The FunctionDef node.

        Returns:
            True or None.
        """
        self.stack.append(node.name.value)

    def leave_FunctionDef(self, node: cst.FunctionDef) -> None:
        """Leaves a FunctionDef node.

        Args:
            node: The FunctionDef node.
        """
        return self._leave(node)

    def _leave(self, node: DocstringNode) -> None:
        """Leaves a DocstringNode.

        Args:
            node: The DocstringNode.
        """
        key = tuple(self.stack)
        self.stack.pop()

        if hasattr(node, "decorators"):
            for decorator in node.decorators: # type: ignore
                if isinstance(decorator.decorator, cst.Name):
                    if decorator.decorator.value == "overload":
                        return
                elif isinstance(decorator.decorator, cst.Call):
                    if isinstance(decorator.decorator.func, cst.Name) and decorator.decorator.func.value == "overload":
                        return

        statement = get_docstring_statement(node)
        if statement:
            self.docstrings[key] = statement

def merge_docstring(code: str, code_with_docstring: str):
    """Merges the docstrings from the code_with_docstring into the code.

    Args:
        code: The code without docstrings.
        code_with_docstring: The code with docstrings.

    Returns:
        The modified code with merged docstrings.
    """
    code_tree = cst.parse_module(code)
    documented_code_tree = cst.parse_module(code_with_docstring)

    visitor = DocstringCollector()
    documented_code_tree.visit(visitor)
    transformer = DocstringTransformer(visitor.docstrings)
    modified_tree = code_tree.visit(transformer)
    return modified_tree.code
