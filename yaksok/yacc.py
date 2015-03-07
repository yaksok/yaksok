# coding: utf8
import ast
import logging

from .lex import tokens, IndentLexer
from .ast_tool import transform


precedence = (
    ("left", "EQ", "GT", "LT"),
    ("left", "TILDE"),
    ("left", "PLUS", "MINUS"),
    ("left", "MULT", "DIV"),
)

binop_cls = {
    '+': ast.Add,
    '-': ast.Sub,
    '*': ast.Mult,
    '/': ast.Div,
    '>': ast.Gt,
    '<': ast.Lt,
    '=': ast.Eq,
}

_gen_sym_idx = 0
def gen_sym():
    global _gen_sym_idx
    _gen_sym_idx += 1
    return '____{}gs____gs'.format(_gen_sym_idx)


def flatten(l):
    def flatten_iter(l):
        if isinstance(l, list):
            for x in l:
                for y in flatten_iter(x):
                    yield y
        else:
            yield l
    return list(flatten_iter(l))

assert flatten([[1,2,[3,4],5],[6,7]]) == [1,2,3,4,5,6,7]

def p_file_input_end(t):
    """file_input_end : file_input ENDMARKER
                    | file_input ENDMARKER WS""" # meaningless rule to avoid unused token message
    t[0] = t[1]

def p_file_input(t):
    """file_input : file_input NEWLINE
                  | file_input stmt
                  | NEWLINE
                  | stmt"""
    if isinstance(t[len(t)-1], str):
        if len(t) == 3:
            t[0] = t[1]
        else:
            t[0] = []
    else:
        if len(t) == 3:
            t[0] = flatten(t[1]+[t[2]])
        else:
            t[0] = flatten([t[1]])


def p_stmts(t):
    '''stmts : stmts stmt
             | stmt'''
    if len(t) == 3:
        t[0] = flatten(t[1] + [t[2]])
    else:
        t[0] = flatten([t[1]])


def p_suite(t):
    '''suite : NEWLINE INDENT stmts DEDENT'''
    # suite : stmt NEWLINE 는 사용 불가, 무조건 다음 줄에
    if len(t) == 2:
        t[0] = [t[1]]
    else:
        t[0] = t[3]


def p_defun_str(t):
    '''defun_str : STRING_LITERAL'''
    if '\n' in t[1]:
        print("구문 오류입니다.")
        print("줄바꿈이 들어간 약속은 만들 수 없습니다.")
        raise SyntaxError
    t[0] = t[1]


def p_function_description_item_ws(t):
    '''function_description_item : WS'''
    t[0] = ('WS', t[1])


def p_function_description_item_identifier(t):
    '''function_description_item : IDENTIFIER'''
    t[0] = ('IDENTIFIER', t[1])


def p_function_description_item_str(t):
    '''function_description_item : defun_str'''
    t[0] = ('STR', t[1])


def p_function_description(t):
    '''function_description : function_description function_description_item
                            | function_description_item'''
    if len(t) == 3:
        t[0] = t[1] + [t[2]]
    else:
        t[0] = [t[1]]


def validate_function_description(fd_list):
    for idx, (ty, token) in enumerate(fd_list):
        if ty == "STR":
            if (idx > 0 and idx + 1< len(fd_list) and
                    fd_list[idx-1][0] != 'WS' and fd_list[idx+1][0] != 'WS'):
                print('구문 오류입니다.')
                print('문자열 양 옆으로 빈 칸 없이 붙여쓸 수 없습니다.')
                raise SyntaxError


def p_function_def_stmt(t):
    '''stmt : DEFUN WS function_description suite'''
    proto = t[3]
    validate_function_description(proto)
    arg_list = ''.join(item[1] for item in proto if item[0] == 'IDENTIFIER')
    internal_function_name = gen_sym()

    codes = '''
def {internal_function_name}({arg_list}):
    <:suite:>
try:
    ____functions
except:
    ____functions = []

____functions.append(({internal_function_name}, {proto}))
'''.format(**locals())

    t[0] = transform(codes, dict(suite=t[4]), expose=True)


def p_loop_stmt(t):
    '''stmt : expression IDENTIFIER IDENTIFIER IDENTIFIER LOOP suite'''
    if t[2] != '의' or t[4] != '마다':
        print("구문 오류입니다: {} {} {} {}".format(t[2], t[3], t[4], t[5]))
        print("\t'~ 의 ~ 마다 반복' 꼴이어야 합니다.")
        raise SyntaxError
    for_var = ast.Name(t[3], ast.Store())
    for_var.lineno = t.lineno(3)
    for_var.col_offset = -1 # XXX

    t[0] = ast.For(for_var, t[1], t[6], [])
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX


def p_if_stmt(t):
    '''stmt : IF expression THEN suite'''
    t[0] = ast.If(t[2], t[4], [])
    t[0].lineno = t.lineno(4)
    t[0].col_offset = -1  # XXX


def p_assign_stmt(t):
    '''stmt : target ASSIGN expression NEWLINE'''
    t[0] = ast.Assign(t[1], t[3])
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX


def p_target(t):
    '''target : IDENTIFIER'''
    identifier = ast.Name(t[1], ast.Store())
    identifier.lineno = t.lineno(1)
    identifier.col_offset = -1  # XXX
    t[0] = [identifier]


def p_target_subscription(t):
    '''target : primary LSQUARE expression RSQUARE'''
    index = ast.Index(make_sub_one(t, 3))
    index.lineno = t.lineno(3)
    index.col_offset = -1  # XXX
    subscription = ast.Subscript(t[1], index, ast.Store())
    subscription.lineno = t.lineno(1)
    subscription.col_offset = -1  # XXX
    t[0] = [subscription]


def p_expression_stmt(t):
    '''stmt : expression NEWLINE'''
    t[0] = ast.Expr(t[1])
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX


def p_expression(t):
    '''expression : call
                  | logic_expr'''
    t[0] = t[1]


def p_call(t):
    '''call : expression IDENTIFIER'''
    func = ast.Name(t[2], ast.Load())
    func.lineno = t.lineno(2)
    func.col_offset = -1  # XXX
    t[0] = ast.Call(func, [t[1]], [], None, None)
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX


def p_logic_expr(t):
    '''logic_expr : arith_expr EQ arith_expr
                  | arith_expr GT arith_expr
                  | arith_expr LT arith_expr'''
    t[0] = ast.Compare(t[1], [binop_cls[t[2]]()], [t[3]])
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX


def p_logic_expr_arith_expr(t):
    '''logic_expr : arith_expr'''
    t[0] = t[1]


# precedence 주면 PLY가 알아서 해줌
def p_arith_expr(t):
    '''arith_expr : arith_expr PLUS arith_expr
                  | arith_expr MINUS arith_expr
                  | arith_expr MULT arith_expr
                  | arith_expr DIV arith_expr'''
    t[0] = ast.BinOp(t[1], binop_cls[t[2]](), t[3])
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX


def make_add_one(t, idx):
    one = ast.Num(1)
    one.lineno = t.lineno(idx)
    one.col_offset = -1  # XXX

    add_one = ast.BinOp(t[idx], binop_cls['+'](), one)
    add_one.lineno = t.lineno(idx)
    add_one.col_offset = -1  # XXX

    return add_one


def make_sub_one(t, idx):
    one = ast.Num(1)
    one.lineno = t.lineno(idx)
    one.col_offset = -1  # XXX

    add_one = ast.BinOp(t[idx], binop_cls['-'](), one)
    add_one.lineno = t.lineno(idx)
    add_one.col_offset = -1  # XXX

    return add_one


def p_arith_expr_primary(t):
    '''arith_expr : primary'''
    t[0] = t[1]


def p_primary(t):
    '''primary : atom
               | subscription'''
    t[0] = t[1]


def p_subscription(t):
    '''subscription : primary LSQUARE expression RSQUARE'''
    #index = ast.Index(make_sub_one(t, 2))
    #index.lineno = t.lineno(2)
    #index.col_offset = -1  # XXX
    index = t[3]

    func = ast.Name('____subscript', ast.Load())
    func.lineno = t.lineno(1)
    func.col_offset = -1  # XXX

    t[0] = ast.Call(func, [t[1], index], [], None, None)
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX

    #t[0] = ast.Subscript(t[-1], index, ast.Load())
    #t[0].lineno = t.lineno(-1)
    #t[0].col_offset = -1  # XXX


def p_atom(t):
    '''atom : num
            | str
            | list
            | range'''
    t[0] = t[1]


def p_atom_true(t):
    '''atom : TRUE'''
    t[0] = ast.NameConstant(True)
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX


def p_atom_false(t):
    '''atom : FALSE'''
    t[0] = ast.NameConstant(False)
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX


def p_atom_identifier(t):
    '''atom : IDENTIFIER'''
    t[0] = ast.Name(t[1], ast.Load())
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX


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


def p_range(t):
    '''range : arith_expr TILDE arith_expr'''
    func = ast.Name('____range', ast.Load())
    func.lineno = t.lineno(2)
    func.col_offset = -1  # XXX
    add_one = make_add_one(t, 3)
    t[0] = ast.Call(func, [t[1], add_one], [], None, None)
    t[0].lineno = t.lineno(2)
    t[0].col_offset = -1  # XXX


def p_atom_list(t):
    '''list : LSQUARE RSQUARE
            | LSQUARE list_items RSQUARE'''
    if len(t) == 3:
        t[0] = ast.List([], ast.Load())
        t[0].lineno = t.lineno(1)
        t[0].col_offset = -1  # XXX
    else:
        t[0] = ast.List(t[2], ast.Load())
        t[0].lineno = t.lineno(1)
        t[0].col_offset = -1  # XXX


def p_list_items(t):
    '''list_items : expression
                  | list_items COMMA expression'''
    if len(t) == 2:
        t[0] = [t[1]]
    else:
        t[0] = t[1] + [t[3]]


def p_atom_paren(t):
    '''atom : LPAR expression RPAR'''
    t[0] = t[2]


def p_error(t):
    if t:
        print("구문 오류입니다({}번째 줄): {}".format(t.lineno, repr(t.value)))
    else:
        print("구문 오류입니다.")


class Parser:
    def __init__(self, lexer = None):
        import ply.yacc
        if lexer is None:
            lexer = IndentLexer()
        self.lexer = lexer
        self.parser = ply.yacc.yacc(start="file_input_end", debug=False)

    def parse(self, code, interactive=False):
        self.lexer.input(code)
        tree = self.parser.parse(lexer = self.lexer)
        if interactive:
            return ast.Interactive(tree)
        else:
            return ast.Module(tree)


parser = Parser()


def compile_code(code, file_name=None):
    interactive = file_name is None
    tree = parser.parse(code, interactive=interactive)
    logging.debug(ast.dump(tree))
    return compile(tree, file_name or '<string>', 'single' if interactive else 'exec')
