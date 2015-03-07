import ast
class MyTransformer(ast.NodeTransformer):
    def __init__(self, temporary_names):
        self.temporary_names = temporary_names

    def visit_has_body(self, node):
        for idx, expr in enumerate(node.body):
            if (isinstance(expr, ast.Expr) and
                    isinstance(expr.value, ast.Name) and
                    expr.value.id in self.temporary_names and
                    isinstance(self.temporary_names[expr.value.id], list)):
                node.body[idx:idx+1] = self.temporary_names[expr.value.id]
        return node

    visit_ClassDef = visit_has_body
    visit_FunctionDef = visit_has_body

    def visit_Name(self, node):
        if node.id in self.temporary_names:
            if not isinstance(self.temporary_names[node.id], list):
                return ast.copy_location(self.temporary_names[node.id], node)
        return node

def transform(code, mapping, expose=False):
    temporary_names = {}
    
    for idx, (k, v) in enumerate(mapping.items()):
        temporary_name = '____temp{}____192837172____'.format(idx)
        temporary_names[temporary_name] = v
        code = code.replace('<:'+k+':>', temporary_name)
    tree = ast.parse(code)

    MyTransformer(temporary_names).visit(tree)
    if expose:
        assert isinstance(tree, ast.Module)
        return tree.body
    return tree

