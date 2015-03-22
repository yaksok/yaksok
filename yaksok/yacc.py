# coding: utf8
import ast
import logging

from .lex import tokens, IndentLexer
from .ast_tool import transform


precedence = (
    #("left", "OR"),
    #("left", "AND"),
    ("nonassoc", "EQ", "GT", "LT", "NE", "GTEQ", "LTEQ"),
    #("left", "TILDE"),
    #("left", "PLUS", "MINUS"),
    #("left", "MULT", "DIV"),
    #("right", "UMINUS"),
)

binop_cls = {
    '+': ast.Add,
    '-': ast.Sub,
    '%': ast.Mod,
    '*': ast.Mult,
    '/': ast.Div,
    '>': ast.Gt,
    '<': ast.Lt,
    '>=': ast.GtE,
    '<=': ast.LtE,
    '=': ast.Eq,
    '!=': ast.NotEq,
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

errors = []
def report_error(t, msg):
    try:
        errors.append((t.lineno, msg))
    except:
        errors.append((-1, msg))

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
        report_error(t, "구문 오류입니다.")
        report_error(t, "\t줄바꿈이 들어간 약속은 만들 수 없습니다.")
        raise SyntaxError
    t[0] = t[1]


def p_function_description_item_ws(t):
    '''function_description_item : WS'''
    t[0] = [('WS', t[1])]


def p_function_description_item_identifier(t):
    '''function_description_item : IDENTIFIER'''
    t[0] = [('IDENTIFIER', t[1])]


def p_function_description_item_str(t):
    '''function_description_item : defun_str'''

    body = eval(t[1])

    # whitespace가 포함된 경우 여러 STR을 지정한 것과 마찬가지로 만들어준다
    # "안녕 세계" === "안녕" "세계"
    if ' ' in body:
        body = body.split(' ')
        new_body = [('WS', ' ')] * (len(body)*2-1)
        new_body[::2] = body
        body = new_body
    else:
        body = [body]

    for idx, element in enumerate(body):
        if idx%2 == 1: 
            continue
        # 을/를 이/가 등의 조사 지원
        if '/' in element:
            element = element.split('/')
            body[idx] = ('STRS', element)
        else:
            body[idx] = ('STR', element)
    t[0] = body


def p_function_description(t):
    '''function_description : function_description function_description_item
                            | function_description_item'''
    if len(t) == 3:
        t[0] = t[1] + t[2]
    else:
        t[0] = t[1]


def validate_function_description(fd_list):
    for idx, (ty, token) in enumerate(fd_list):
        if ty == "STR":
            if (idx + 1 < len(fd_list) and 
                    fd_list[idx+1][0] != 'WS'):
                report_error(t, '구문 오류입니다.')
                report_error(t, '\t약속을 만들때, 문자열 다음은 반드시 빈 칸이어야 합니다.')
                raise SyntaxError

            # 앞에는 무조건 띄우는 걸로 합시다
            #if (idx > 0 and idx + 1 < len(fd_list) and
                    #fd_list[idx-1][0] != 'WS' and fd_list[idx+1][0] != 'WS'):
                #report_error(t, '구문 오류입니다.')
                #report_error(t, '\t문자열 양 옆으로 빈 칸 없이 붙여쓸 수 없습니다.')
                #raise SyntaxError

def p_translate_stmt(t):
    '''stmt : TRANSLATE WS function_description NEWLINE SPECIALBLOCK SPECIALBLOCK NEWLINE'''
    if t[1] == 'python':
        proto = t[3]
        body = t[6]
        while proto[-1][0] == 'WS':
            proto.pop()
        validate_function_description(proto)
        arg_list = ','.join(item[1] for item in proto if item[0] == 'IDENTIFIER')
        internal_function_name = gen_sym()

        codes = '''
def {internal_function_name}({arg_list}):
    {body}
try:
    ____functions
except:
    ____functions = []

____functions.append(({internal_function_name}, {proto}))
'''.format(**locals())

        t[0] = transform(codes, {}, expose=True)
    else:
        t[0] = []


def p_function_return_stmt(t):
    '''stmt : DEFUN WS END_BLOCK NEWLINE'''
    t[0] = transform('return 결과', {}, expose=True)[0]
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1 # XXX


def p_break_stmt(t):
    '''stmt : LOOP END_BLOCK NEWLINE'''
    t[0] = transform('break', {}, expose=True)[0]
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1 # XXX


def p_continue_stmt(t):
    '''stmt : LOOP CONTINUE NEWLINE'''
    t[0] = transform('continue', {}, expose=True)[0]
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1 # XXX


def p_pass_stmt(t):
    '''stmt : PASS NEWLINE'''
    t[0] = ast.Pass()
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1 # XXX

def p_function_def_stmt(t):
    '''stmt : DEFUN WS function_description suite'''
    proto = t[3]
    while proto[-1][0] == 'WS':
        proto.pop()

    validate_function_description(proto)
    arg_list = ','.join(item[1] for item in proto if item[0] == 'IDENTIFIER')
    internal_function_name = gen_sym()

    codes = '''
def {internal_function_name}({arg_list}):
    결과 = None
    <:suite:>
    return 결과
try:
    ____functions
except:
    ____functions = []

____functions.append(({internal_function_name}, {proto}))
'''.format(**locals())

    t[0] = transform(codes, dict(suite=t[4]), expose=True)


def p_infinite_loop_stmt(t):
    '''stmt : LOOP suite'''
    one = ast.Num(1)
    one.lineno = t.lineno(1)
    one.col_offset = -1  # XXX

    suite = t[2]

    t[0] = ast.While(one, suite, [])
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX


def p_loop_stmt(t):
    #'''stmt : expression IDENTIFIER IDENTIFIER IDENTIFIER LOOP suite'''
    #use_loop_before = False
    '''stmt : LOOP expression IDENTIFIER IDENTIFIER IDENTIFIER suite'''
    use_loop_before = True
    if use_loop_before:
        container, 의, variable, 마다, suite = t[2], t[3], t[4], t[5], t[6]
        container_idx = 2
        variable_idx = 4
    else:
        container, 의, variable, 마다, suite = t[1], t[2], t[3], t[4], t[6]
        container_idx = 1
        variable_idx = 3

    if 의 != '의' or 마다 != '마다':
        if use_loop_before:
            report_error(t, "구문 오류입니다: 반복 {} {} {}".format(의, variable, 마다))
        else:
            report_error(t, "구문 오류입니다: {} {} {} 반복".format(의, variable, 마다))
        report_error(t, "\t'~ 의 ~ 마다 반복' 꼴이어야 합니다.")
        raise SyntaxError
    for_var = ast.Name(variable, ast.Store())
    for_var.lineno = t.lineno(variable_idx)
    for_var.col_offset = -1 # XXX

    t[0] = ast.For(for_var, container, suite, [])
    t[0].lineno = t.lineno(container_idx)
    t[0].col_offset = -1  # XXX


def p_empty(t):
    '''empty : '''


def p_if_else_or_empty(t):
    '''else_or_empty : ELSE suite
                     | empty'''
    if len(t) == 2:
        t[0] = []
    else:
        t[0] = t[2]


def p_if_elif(t):
    '''elif : ELSE IF expression THEN suite
            | ELSEAND IF expression THEN suite'''
    # NOTE
    # 아니면 만약, 아니라면 만약 / 아니면서 만약
    # ELSE랑 충분히 헷갈릴 수 있으므로 일단 모두 처리가능하게
    elif_block = ast.If(t[3], t[5], [])
    elif_block.lineno = t.lineno(4)
    elif_block.col_offset = -1  # XXX
    t[0] = elif_block


# 부정 조건문의 elif 버전
def p_if_elif_else(t):
    '''elif : ELSE IF expression ELSE suite
            | ELSEAND IF expression ELSE suite'''
    # NOTE
    # 아니면 만약, 아니라면 만약 / 아니면서 만약
    # ELSE랑 충분히 헷갈릴 수 있으므로 일단 모두 처리가능하게
    not_ast = ast.Not()
    not_ast.lineno = t.lineno(2)
    nonassoc.col_offset = -1 # XXX

    cond = ast.UnaryOp(not_ast, t[3])
    cond.lineno = t.lineno(2)
    cond.col_offset = -1 # XXX

    elif_block = ast.If(cond, t[5], [])
    elif_block.lineno = t.lineno(4)
    elif_block.col_offset = -1  # XXX
    t[0] = elif_block


def p_if_elifs(t):
    '''elifs : elifs elif
             | empty'''
    if len(t) == 3:
        t[0] = t[1] + [t[2]]
    else:
        t[0] = []

def p_if_stmt(t):
    '''stmt : IF expression THEN suite elifs else_or_empty'''
    last = t[6]
    elifs = t[5]
    for elif_block in elifs:
        elif_block.orelse = last
        last = [elif_block]
    t[0] = ast.If(t[2], t[4], last)
    t[0].lineno = t.lineno(3)
    t[0].col_offset = -1  # XXX


def p_if_else_stmt(t):
    '''stmt : IF expression ELSE suite'''
    pass_ast = ast.Pass()
    pass_ast.lineno = t.lineno(1)
    pass_ast.col_offset = -1 # XXX
    t[0] = ast.If(t[2], [pass_ast], t[4])
    t[0].lineno = t.lineno(4)
    t[0].col_offset = -1  # XXX


def p_assign_stmt(t):
    '''stmt : target ASSIGN expression NEWLINE
            | target ASSIGN call NEWLINE
            | target ASSIGN import_call NEWLINE'''
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


def p_imported_call_stmt(t):
    '''stmt : import_call NEWLINE'''
    t[0] = ast.Expr(t[1])
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1 # XXX


def p_imported_call(t):
    '''import_call : ATMARK IDENTIFIER call'''
    # call is ast.Call()

    codes = '''____getmodule("{}")['____functions']'''.format(t[2])
    last_arg = transform(codes, {}, expose=True)[0].value

    call_ast = t[3]
    call_ast.args[-1] = last_arg
    t[0] = call_ast


def p_call_stmt(t):
    '''stmt : call NEWLINE'''
    t[0] = ast.Expr(t[1])
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX


def p_expression(t):
    '''expression : logic_or_expr'''
    t[0] = t[1]


def p_logic_or_expr(t):
    '''logic_or_expr : logic_or_expr OR logic_and_expr
                     | logic_and_expr'''
    if len(t) == 4:
        if isinstance(t[1], ast.BoolOp) and isinstance(t[1].op, ast.Or):
            t[0] = t[1]
            t[0].values.append(t[3])
        else:
            or_ast = ast.Or()
            or_ast.lineno = t.lineno(2)
            or_ast.col_offset = -1 # XXX
            t[0] = ast.BoolOp(or_ast, [t[1], t[3]])
            t[0].lineno = t.lineno(2)
            t[0].col_offset = -1 # XXX
    else:
        t[0] = t[1]


def p_logic_and_expr(t):
    '''logic_and_expr : logic_and_expr AND logic_expr
                      | logic_expr'''
    if len(t) == 4:
        if isinstance(t[1], ast.BoolOp) and isinstance(t[1].op, ast.And):
            t[0] = t[1]
            t[0].values.append(t[3])
        else:
            and_ast = ast.And()
            and_ast.lineno = t.lineno(2)
            and_ast.col_offset = -1 # XXX
            t[0] = ast.BoolOp(and_ast, [t[1], t[3]])
            t[0].lineno = t.lineno(2)
            t[0].col_offset = -1 # XXX
    else:
        t[0] = t[1]


def p_call_expression_list(t):
    '''call_expression_list : call_expression_list expression
                            | expression'''
    # expression or IDENTIFIER or expression+IDENTIFIER(조사 붙여쓰기)
    def unwrap_name(x):
        if isinstance(x, ast.Name):
            return ('NAME', x.id)
        return ('EXPR', x)

    if len(t) == 3:
        t[0] = t[1] + [unwrap_name(t[2])]
    else:
        t[0] = [unwrap_name(t[1])]


def p_call(t):
    '''call : call_expression_list'''

    call_expression_list = t[1]
    call_matcher_appender = []
    arg_s = {}
    for idx, (ty, val) in enumerate(call_expression_list):
        if isinstance(val, ast.AST):
            arg_s['t{}'.format(idx)] = val
            call_matcher_appender.append("(({!r}, <:t{}:>))\n".format(ty, idx))
        else:
            call_matcher_appender.append("(({!r}, {!r}))\n".format(ty, val))
    call_matcher_appender = ','.join(call_matcher_appender)
    arg_s['call_matcher_appender'] = call_matcher_appender

    codes = '''____find_and_call_function([{call_matcher_appender}], ____locals(), ____globals(), ____functions)'''.format(**arg_s)
    t[0] = transform(codes, arg_s, expose=True)[0].value


def p_logic_expr(t):
    '''logic_expr : arith_expr EQ arith_expr
                  | arith_expr NE arith_expr
                  | arith_expr GT arith_expr
                  | arith_expr LT arith_expr
                  | arith_expr GTEQ arith_expr
                  | arith_expr LTEQ arith_expr'''
    t[0] = ast.Compare(t[1], [binop_cls[t[2]]()], [t[3]])
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX


def p_logic_expr_arith_expr(t):
    '''logic_expr : arith_expr'''
    t[0] = t[1]


def p_arith_expr(t):
    '''arith_expr : arith_expr PLUS term
                  | arith_expr MINUS term'''
    t[0] = ast.BinOp(t[1], binop_cls[t[2]](), t[3])
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX

def p_arith_expr_term(t):
    '''arith_expr : term'''
    t[0] = t[1]


def p_term(t):
    '''term : term MULT factor
            | term DIV factor
            | term MOD factor'''
    t[0] = ast.BinOp(t[1], binop_cls[t[2]](), t[3])
    t[0].lineno = t.lineno(1)
    t[0].col_offset = -1  # XXX


def p_term_factor(t):
    '''term : factor'''
    t[0] = t[1]


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


def p_factor_unary_expr(t):
    '''factor : unary_expr'''
    t[0] = t[1]


def p_unary_expr_primary(t):
    '''unary_expr : primary'''
    t[0] = t[1]


def p_unary_expr_minus_primary(t):
    #'''unary_expr : MINUS primary %prec UMINUS'''
    '''unary_expr : MINUS primary'''
    usub = ast.USub()
    usub.lineno = t.lineno(1)
    usub.col_offset = -1 # XXX
    t[0] = ast.UnaryOp(usub, t[2])
    t[0].lineno = t.lineno(2)
    t[0].col_offset = -1 # XXX


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
    '''atom : LPAR expression RPAR
            | LPAR call RPAR
            | LPAR import_call RPAR'''
    t[0] = t[2]


def p_error(t):
    report_error(t, "구문 오류입니다. (원인불명) {}".format(t))


class Parser:
    def __init__(self, lexer = None):
        import ply.yacc
        if lexer is None:
            lexer = IndentLexer()
        self.lexer = lexer
        self.parser = ply.yacc.yacc(start="file_input_end", debug=False)
        del errors[:]


    def parse(self, code, file_name, interactive=False):
        self.lexer.input(code)
        tree = self.parser.parse(lexer = self.lexer, debug=False)
        if errors:
            first_error = None
            for line, msg in errors:
                if line == -1:
                    print('{}\t{}'.format(file_name, msg))
                else:
                    print('{}:{}\t{}'.format(file_name, line, msg))
            raise SyntaxError
        if interactive:
            return ast.Interactive(tree)
        else:
            return ast.Module(tree)


parser = Parser()


def compile_code(code, file_name=None):
    interactive = file_name is None
    tree = parser.parse(code, file_name or '<string>', interactive=interactive)
    #logging.debug(ast.dump(tree))
    return compile(tree, file_name or '<string>', 'single' if interactive else 'exec')

def to_ast(code, file_name = None):
    interactive = file_name is None
    tree = parser.parse(code, file_name or '<string>', interactive=interactive)
    return tree
