import libcst as cst
import libcst.matchers as m

def simplify_code(code: str) -> str:
    module = cst.parse_module(code)

    class RemoveFunctionBodies(cst.CSTTransformer):
        def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
            return updated_node.with_changes(
                body=cst.IndentedBlock(
                    body=[cst.SimpleStatementLine(body=[cst.Pass()])])
            )

        def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
            # 对于类的方法，我们也使用 pass 替换它们的主体
            # 同时，我们移除类的 docstring
            new_body = []
            for statement in original_node.body.body:
                if isinstance(statement, cst.FunctionDef):
                    new_body.append(statement.with_changes(
                        body=cst.IndentedBlock(
                            body=[cst.SimpleStatementLine(body=[cst.Pass()])])
                    ))
                elif isinstance(statement, cst.SimpleStatementLine) and m.matches(statement, m.SimpleStatementLine(body=[m.Expr()])):
                    # 这是一个 docstring，我们跳过它
                    continue
                else:
                    new_body.append(statement)
            return updated_node.with_changes(body=cst.IndentedBlock(body=new_body))

    simplified_module = module.visit(RemoveFunctionBodies())

    return simplified_module.code

def remove_comments(code: str) -> str:
    module = cst.parse_module(code)

    class RemoveComments(cst.CSTTransformer):
        def leave_Comment(self, original_node: cst.Comment, updated_node: cst.Comment) -> cst.RemovalSentinel:
            return cst.RemoveFromParent()

    module_without_comments = module.visit(RemoveComments())

    return module_without_comments.code

def remove_unused_imports(code: str) -> str:
    module = cst.parse_module(code)

    # 创建一个转换器去掉所有的 import 语句
    class RemoveImports(cst.CSTTransformer):
        def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.RemovalSentinel:
            return cst.RemoveFromParent()

        def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.RemovalSentinel:
            return cst.RemoveFromParent()

    # 使用转换器去掉所有的 import 语句
    module_without_imports = module.visit(RemoveImports())

    # 然后在剩下的代码中收集使用的名称
    all_used_names = set()

    class CollectUsedNames(cst.CSTVisitor):
        def visit_Name(self, node: cst.Name):
            all_used_names.add(node.value)

    module_without_imports.visit(CollectUsedNames())

    # 最后，再次遍历原模块，移除未使用的 import
    class RemoveUnusedImports(cst.CSTTransformer):
        def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import:
            new_names = [
                name for name in original_node.names if name.name.value in all_used_names
            ]
            return updated_node.with_changes(names=new_names) if new_names else cst.RemoveFromParent() # type: ignore

        def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.ImportFrom:
            if original_node.names is not None:
                new_names = [
                    name for name in original_node.names if name.name.value in all_used_names # type: ignore
                ]
                return updated_node.with_changes(names=new_names) if new_names else cst.RemoveFromParent() # type: ignore
            return updated_node

    simplified_module = module.visit(RemoveUnusedImports())

    return simplified_module.code

def code_interface(code: str) -> str:
    code = simplify_code(code)
    code = remove_comments(code)
    code = remove_unused_imports(code)
    return code