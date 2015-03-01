# coding: utf8
from lex import tokens


def p_function_call(t):
    'function_call : simple_expression IDENTIFIER'
    if t[2] == '보여주기':
        print(t[1])


def p_simple_expression(t):
    'simple_expression : STRING_LITERAL'
    t[0] = eval(t[1])


def p_error(t):
    print("구문 오류입니다: {}".format(repr(t.value)))


import ply.yacc
ply.yacc.yacc()

parse = ply.yacc.parse
