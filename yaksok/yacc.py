# coding: utf8
import ast

from lex import tokens


precedence = (
#    ("left", "EQ", "GT", "LT"),
    ("left", "PLUS", "MINUS"),
    ("left", "MULT", "DIV"),
)

binop_cls = {
    '+': ast.Add,
    '-': ast.Sub,
    '*': ast.Mult,
    '/': ast.Div,
}


def p_stmts(t):
    '''stmts : stmts stmt
             | stmt'''
    if len(t) == 3:
        t[0] = t[1] + [t[2]]
    else:
        t[0] = [t[1]]


def p_expression_stmt(t):
    '''stmt : expression'''
    t[0] = ast.Expr(t[1])
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX



def p_expression(t):
    '''expression : call
                  | arith_expr'''
    t[0] = t[1]


def p_call(t):
    '''call : expression IDENTIFIER'''
    func = ast.Name(t[2], ast.Load())
    func.lineno = t.lineno(2)
    func.col_offset = -1  # XXX
    t[0] = ast.Call(func, [t[1]], [], None, None)
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX


# precedence 주면 PLY가 알아서 해줌
def p_arith_expr(t):
    '''arith_expr : arith_expr PLUS arith_expr
                  | arith_expr MINUS arith_expr
                  | arith_expr MULT arith_expr
                  | arith_expr DIV arith_expr'''
    t[0] = ast.BinOp(t[1], binop_cls[t[2]](), t[3])
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX
def p_arith_expr_atom(t):
    '''arith_expr : atom'''
    t[0] = t[1]


def p_atom(t):
    '''atom : num
            | str'''
    t[0] = t[1]


def p_num(t):
    '''num : INTEGER'''
    t[0] = ast.Num(eval(t[1]))
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX


def p_str(t):
    '''str : STRING_LITERAL'''
    t[0] = ast.Str(eval(t[1]))
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX


def p_error(t):
    if t:
        print("구문 오류입니다: {}".format(repr(t.value)))
    else:
        print("구문 오류입니다.")


import ply.yacc
ply.yacc.yacc()


def parse(code, interactive=False):
    tree = ply.yacc.parse(code)
    if interactive:
        return ast.Interactive(tree)
    else:
        return ast.Module(tree)


def compile_code(code, file_name=None):
    interactive = file_name is None
    tree = parse(code, interactive=interactive)
    print(ast.dump(tree))
    return compile(tree, file_name or '<string>', 'single' if interactive else 'exec')
